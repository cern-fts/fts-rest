from datetime import datetime, timedelta
from fts3.model import Job, File, JobActiveStates
from fts3.model import Credential, BannedSE
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.middleware.fts3auth import authorize, authorized
from fts3rest.lib.middleware.fts3auth.constants import *
from pylons import request
from pylons.controllers.util import abort
import hashlib
import json
import re
import socket
import types
import urllib
import urlparse
import uuid


DEFAULT_PARAMS = {
    'bring_online'     : -1,
    'verify_checksum'  : False,
    'copy_pin_lifetime': -1,
    'gridftp'          : '',
    'job_metadata'     : None,
    'overwrite'        : False,
    'reuse'            : False,
    'source_spacetoken': '',
    'spacetoken'       : '',
    'retry'            : 0
}


def _hexdump(bytes):
    return ''.join(map(lambda b: "%02x" % ord(b), bytes))


def _hashed_id(id):
    assert id is not None
    digest = hashlib.md5(str(id)).digest()
    b16digest = digest.encode('hex')
    return int(b16digest[:4], 16)


class JobsController(BaseController):

    def _getJob(self, id):
        job = Session.query(Job).get(id)
        if job is None:
            abort(404, 'No job with the id "%s" has been found' % id)
        if not authorized(TRANSFER,
                          resource_owner=job.user_dn, resource_vo=job.vo_name):
            abort(403, 'Not enough permissions to check the job "%s"' % id)
        return job

    @authorize(TRANSFER)
    @jsonify
    def index(self, **kwargs):
        """GET /jobs: All jobs in the collection"""
        jobs = Session.query(Job).filter(Job.job_state.in_(JobActiveStates))

        # Filtering
        if 'user_dn' in request.params and request.params['user_dn']:
            jobs = jobs.filter(Job.user_dn == request.params['user_dn'])
        if 'vo_name' in request.params and request.params['vo_name']:
            jobs = jobs.filter(Job.vo_name == request.params['vo_name'])

        # Return
        return jobs.all()

    @jsonify
    def cancel(self, id, **kwargs):
        """DELETE /jobs/id: Delete an existing item"""
        job = self._getJob(id)

        if job.job_state in JobActiveStates:
            now = datetime.now()

            job.job_state    = 'CANCELED'
            job.finish_time  = now
            job.job_finished = now
            job.reason       = 'Job canceled by the user'

            for f in job.files:
                if f.file_state in JobActiveStates:
                    f.file_state   = 'CANCELED'
                    f.job_finished = now
                    f.finish_time  = now
                    f.reason       = 'Job canceled by the user'

            Session.merge(job)
            Session.commit()

            job = self._getJob(id)

        files = job.files
        return job

    @jsonify
    def show(self, id, **kwargs):
        """GET /jobs/id: Show a specific item"""
        job = self._getJob(id)
        # Trigger the query, so it is serialized
        files = job.files
        return job

    @jsonify
    def showField(self, id, field, **kwargs):
        """GET /jobs/id/field: Show a specific field from an item"""
        job = self._getJob(id)
        if hasattr(job, field):
            return getattr(job, field)
        else:
            abort(404, 'No such field')

    @authorize(TRANSFER)
    @jsonify
    def submit(self, **kwargs):
        """PUT /jobs: Submits a new job"""
        # First, the request has to be valid JSON
        try:
            if request.method == 'PUT':
                unencodedBody = request.body
            elif request.method == 'POST':
                if request.content_type == 'application/json':
                    unencodedBody = request.body
                else:
                    unencodedBody = urllib.unquote_plus(request.body)
            else:
                abort(400, 'Unsupported method %s' % request.method)

            submittedDict = json.loads(unencodedBody)

        except ValueError, e:
            abort(400, 'Badly formatted JSON request (%s)' % str(e))

        # The auto-generated delegation id must be valid
        user = request.environ['fts3.User.Credentials']
        credential = Session.query(Credential).get((user.delegation_id, user.user_dn))
        if credential is None:
            abort(403, 'No delegation id found for "%s"' % user.user_dn)
        if credential.expired():
            remaining = credential.remaining()
            seconds = abs(remaining.seconds + remaining.days * 24 * 3600)
            abort(403, 'The delegated credentials expired %d seconds ago' % seconds)
        if credential.remaining() < timedelta(hours=1):
            abort(403, 'The delegated credentials has less than one hour left')

        # Populate the job and file
        job = self._setupJobFromDict(submittedDict, user)

        # Set job source and dest se depending on the transfers
        self._setJobSourceAndDestination(job)

        # Validate that there are no bad combinations
        if job.reuse_job and self._hasMultipleOptions(job.files):
            abort(400,
                  'Can not specify reuse and multiple replicas at the same time')

        # Update the database
        Session.merge(job)
        Session.flush()

        # Update hashed_id and vo_name
        for file in Session.query(File).filter(File.job_id == job.job_id):
            file.hashed_id = _hashed_id(file.file_id)
            file.vo_name   = job.vo_name
            Session.merge(file)

        # Commit and return
        Session.commit()
        return job

    def _setJobSourceAndDestination(self, job):
        job.source_se = job.files[0].source_se
        job.dest_se   = job.files[0].dest_se
        for file in job.files:
            if file.source_se != job.source_se:
                job.source_se = None
            if file.dest_se != job.dest_se:
                job.dest_se = None

    def _setupJobFromDict(self, jobDict, user):
        try:
            if len(jobDict['files']) == 0:
                abort(400, 'No transfers specified')

            # Initialize defaults
            # If the client is giving a NULL for a parameter with a default,
            # use the default
            params = dict()
            params.update(DEFAULT_PARAMS)
            if 'params' in jobDict:
                params.update(jobDict['params'])
                for (k, v) in params.iteritems():
                    if v is None and k in DEFAULT_PARAMS:
                        params[k] = DEFAULT_PARAMS[k]

            # Create
            job = Job()

            # Job
            job.job_id                   = str(uuid.uuid1())
            job.job_state                = 'SUBMITTED'
            job.reuse_job                = self._yesOrNo(params['reuse'])
            job.retry                    = int(params['retry'])
            job.job_params               = params['gridftp']
            job.submit_host              = socket.getfqdn()
            job.user_dn                  = user.user_dn

            if 'credential' in jobDict:
                job.user_cred  = jobDict['credential']
                job.cred_id    = str()
            else:
                job.user_cred  = str()
                job.cred_id    = user.delegation_id

            job.voms_cred                = ' '.join(user.voms_cred)
            job.vo_name                  = user.vos[0] if len(user.vos) > 0 and user.vos[0] else 'nil'
            job.submit_time              = datetime.now()
            job.priority                 = 3
            job.space_token              = params['spacetoken']
            job.overwrite_flag           = self._yesOrNo(params['overwrite'])
            job.source_space_token       = params['source_spacetoken'] 
            job.copy_pin_lifetime        = int(params['copy_pin_lifetime'])
            job.verify_checksum          = self._yesOrNo(params['verify_checksum'])
            job.bring_online             = int(params['bring_online'])
            job.job_metadata             = params['job_metadata']
            job.job_params               = str()

            # Files
            findex = 0
            for t in jobDict['files']:
                job.files.extend(self._populateFiles(t, findex))
                findex += 1

            if len(job.files) == 0:
                abort(400, 'No pair with matching protocols')

            # If copy_pin_lifetime is specified, go to staging directly
            if job.copy_pin_lifetime > -1:
                job.job_state = 'STAGING'
                for t in job.files:
                    t.file_state = 'STAGING'

            return job

        except ValueError, e:
            abort(400, 'Invalid value within the request: %s' % str(e))
        except TypeError, e:
            abort(400, 'Malformed request: %s' % str(e))
        except KeyError, e:
            abort(400, 'Missing parameter: %s' % str(e))


    def _protocolMatchAndValid(self, srcScheme, dstScheme):
        forbiddenSchemes = ['', 'file']
        return srcScheme not in forbiddenSchemes and \
                dstScheme not in forbiddenSchemes and \
                (srcScheme == dstScheme or srcScheme == 'srm' or dstScheme == 'srm')

    def _validateUrl(self, url):
        if re.match('^\w+://', url.geturl()) is None:
            raise ValueError('Malformed URL (%s)' % url)
        if not url.path or (url.path == '/' and not url.query):
            raise ValueError('Missing path (%s)' % url)
        if not url.hostname or url.hostname == '':
            raise ValueError('Missing host (%s)' % url)

    def _populateFiles(self, filesDict, findex):
        files = []

        # Extract matching pairs
        pairs = []
        for s in filesDict['sources']:
            source_url = urlparse.urlparse(s)
            self._validateUrl(source_url)
            for d in filesDict['destinations']:
                dest_url   = urlparse.urlparse(d)
                self._validateUrl(dest_url)
                if self._protocolMatchAndValid(source_url.scheme, dest_url.scheme):
                    pairs.append((s, d))

        # Create one File entry per matching pair
        for (s, d) in pairs:
            file = File()

            file.file_index  = findex
            file.file_state  = 'SUBMITTED'
            file.source_surl = s
            file.dest_surl   = d
            file.source_se   = self._getSE(s)
            file.dest_se     = self._getSE(d)

            file.user_filesize = filesDict.get('filesize', None)
            if file.user_filesize is None:
                file.user_filesize = 0
            file.selection_strategy = filesDict.get('selection_strategy', None)

            file.checksum = filesDict.get('checksum', None)
            file.file_metadata = filesDict.get('metadata', None)

            files.append(file)
        return files

    def _getSE(self, uri):
        parsed = urlparse.urlparse(uri)
        return "%s://%s" % (parsed.scheme, parsed.hostname)

    def _yesOrNo(self, value):
        if isinstance(value, types.StringType):
            return len(value) > 0 and value[0].upper() == 'Y'
        elif value:
            return True
        else:
            return False

    def _hasMultipleOptions(self, files):
        ids = map(lambda f: f.file_index, files)
        idCount = len(ids)
        uniqueIdCount = len(set(ids))
        return uniqueIdCount != idCount

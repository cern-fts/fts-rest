from datetime import datetime, timedelta
from fts3.model import Job, File, JobActiveStates
from fts3.model import Credential, BannedSE, OptimizerActive
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.http_exceptions import HTTPAuthenticationTimeout
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


def _hashed_id(id):
    assert id is not None
    digest = hashlib.md5(str(id)).digest()
    b16digest = digest.encode('hex')
    return int(b16digest[:4], 16)


def _set_job_source_and_destination(job):
    """
    Iterates through the files that belong to the job, and determines the
    'overall' job source and destination Storage Elements
    """
    job.source_se = job.files[0].source_se
    job.dest_se   = job.files[0].dest_se
    for file in job.files:
        if file.source_se != job.source_se:
            job.source_se = None
        if file.dest_se != job.dest_se:
            job.dest_se = None


def _get_storage_element(uri):
    """
    Returns the storage element of the given uri, which is the scheme + hostname without the port
    """
    parsed = urlparse.urlparse(uri)
    return "%s://%s" % (parsed.scheme, parsed.hostname)


def _yes_or_no(value):
    if isinstance(value, types.StringType):
        return len(value) > 0 and value[0].upper() == 'Y'
    elif value:
        return True
    else:
        return False

def _has_multiple_options(files):
    """
    Returns True if the set of transfers defines different options
    for the same destination.
    This sort of transfers can not be accepted when reuse is enabled
    """
    ids = map(lambda f: f.file_index, files)
    id_count = len(ids)
    unique_id_count = len(set(ids))
    return unique_id_count != id_count


def _valid_third_party_transfer(src_scheme, dst_scheme):
    """
    Return True if the source scheme and the destination scheme define a
    third party transfer
    """
    ForbiddenSchemes = ['', 'file']
    return src_scheme not in ForbiddenSchemes and \
            dst_scheme not in ForbiddenSchemes and \
            (src_scheme == dst_scheme or src_scheme == 'srm' or dst_scheme == 'srm')


def _validate_url(url):
    """
    Validates the format and content of the url
    """
    if re.match('^\w+://', url.geturl()) is None:
        raise ValueError('Malformed URL (%s)' % url)
    if not url.path or (url.path == '/' and not url.query):
        raise ValueError('Missing path (%s)' % url)
    if not url.hostname or url.hostname == '':
        raise ValueError('Missing host (%s)' % url)


def _populate_files(files_dict, findex):
    """
    From the dictionary files_dict, generate a list of transfers for a job
    """
    files = []

    # Extract matching pairs
    pairs = []
    for s in files_dict['sources']:
        source_url = urlparse.urlparse(s.strip())
        _validate_url(source_url)
        for d in files_dict['destinations']:
            dest_url   = urlparse.urlparse(d.strip())
            _validate_url(dest_url)
            if _valid_third_party_transfer(source_url.scheme, dest_url.scheme):
                pairs.append((source_url.geturl(), dest_url.geturl()))

    # Create one File entry per matching pair
    for (s, d) in pairs:
        file = File()

        file.file_index  = findex
        file.file_state  = 'SUBMITTED'
        file.source_surl = s
        file.dest_surl   = d
        file.source_se   = _get_storage_element(s)
        file.dest_se     = _get_storage_element(d)

        file.user_filesize = files_dict.get('filesize', None)
        if file.user_filesize is None:
            file.user_filesize = 0
        file.selection_strategy = files_dict.get('selection_strategy', None)

        file.checksum = files_dict.get('checksum', None)
        file.file_metadata = files_dict.get('metadata', None)
        file.activity = files_dict.get('activity', None)

        files.append(file)
    return files


def _setup_job_from_dict(job_dict, user):
    """
    From the dictionary, create and populate a Job
    """
    try:
        if len(job_dict['files']) == 0:
            abort(400, 'No transfers specified')

        # Initialize defaults
        # If the client is giving a NULL for a parameter with a default,
        # use the default
        params = dict()
        params.update(DEFAULT_PARAMS)
        if 'params' in job_dict:
            params.update(job_dict['params'])
            for (k, v) in params.iteritems():
                if v is None and k in DEFAULT_PARAMS:
                    params[k] = DEFAULT_PARAMS[k]

        # Create
        job = Job()

        # Job
        job.job_id                   = str(uuid.uuid1())
        job.job_state                = 'SUBMITTED'
        job.reuse_job                = _yes_or_no(params['reuse'])
        job.retry                    = int(params['retry'])
        job.job_params               = params['gridftp']
        job.submit_host              = socket.getfqdn()
        job.user_dn                  = user.user_dn

        if 'credential' in job_dict:
            job.user_cred  = job_dict['credential']
            job.cred_id    = str()
        else:
            job.user_cred  = str()
            job.cred_id    = user.delegation_id

        job.voms_cred                = ' '.join(user.voms_cred)
        job.vo_name                  = user.vos[0] if len(user.vos) > 0 and user.vos[0] else 'nil'
        job.submit_time              = datetime.utcnow()
        job.priority                 = 3
        job.space_token              = params['spacetoken']
        job.overwrite_flag           = _yes_or_no(params['overwrite'])
        job.source_space_token       = params['source_spacetoken'] 
        job.copy_pin_lifetime        = int(params['copy_pin_lifetime'])
        job.verify_checksum          = params['verify_checksum']
        job.bring_online             = int(params['bring_online'])
        job.job_metadata             = params['job_metadata']
        job.job_params               = str()

        # Files
        findex = 0
        for t in job_dict['files']:
            job.files.extend(_populate_files(t, findex))
            findex += 1

        if len(job.files) == 0:
            abort(400, 'No pair with matching protocols')

        # If copy_pin_lifetime OR bring_online are specified, go to staging directly
        if job.copy_pin_lifetime > 0 or job.bring_online > 0:
            job.job_state = 'STAGING'
            for t in job.files:
                t.file_state = 'STAGING'

        # If a checksum is provided, but no checksum is available, 'relaxed' comparison
        # (Not nice, but need to keep functionality!)
        has_checksum = False
        for f in job.files:
            if f.checksum is not None and len(f.checksum) > 0:
                has_checksum = True
                break
        if not job.verify_checksum and has_checksum:
            job.verify_checksum = 'r'

        _set_job_source_and_destination(job)

        return job

    except ValueError, e:
        abort(400, 'Invalid value within the request: %s' % str(e))
    except TypeError, e:
        abort(400, 'Malformed request: %s' % str(e))
    except KeyError, e:
        abort(400, 'Missing parameter: %s' % str(e))


class JobsController(BaseController):
    """
    Operations on jobs and transfers
    """

    def _get_job(self, id):
        job = Session.query(Job).get(id)
        if job is None:
            abort(404, 'No job with the id "%s" has been found' % id)
        if not authorized(TRANSFER,
                          resource_owner=job.user_dn, resource_vo=job.vo_name):
            abort(403, 'Not enough permissions to check the job "%s"' % id)
        return job


    @doc.query_arg('user_dn', 'Filter by user DN')
    @doc.query_arg('vo_name', 'Filter by VO')
    @doc.query_arg('dlg_id', 'Filter by delegation ID')
    @doc.query_arg('state_in', 'Comma separated list of job states to filter. ACTIVE only by default')
    @doc.response(403, 'Operation forbidden')
    @doc.response(400, 'DN and delegation ID do not match')
    @doc.return_type(array_of = Job)
    @authorize(TRANSFER)
    @jsonify
    def index(self, **kwargs):
        """
        Get a list of active jobs, or those that match the filter requirements
        """
        user = request.environ['fts3.User.Credentials']

        jobs = Session.query(Job)

        filter_dn = request.params.get('user_dn', None)
        filter_vo = request.params.get('vo_name', None)
        filter_dlg_id = request.params.get('dlg_id', None)
        filter_state = request.params.get('state_in', None)
        
        if filter_dlg_id and filter_dlg_id != user.delegation_id:
            abort(403, 'The provided delegation id does not match your delegation id')
        if filter_dlg_id and filter_dn and filter_dn != user.user_dn:
            abort(400, 'The provided DN and delegation id do not correspond to the same user')
        if not filter_dlg_id and filter_state:
            abort(403, 'To filter by state, you need to provide dlg_id')
            
        if filter_state:
            filter_state = filter_state.split(',')
        else:
            filter_state = JobActiveStates
        
        jobs = jobs.filter(Job.job_state.in_(filter_state))
        if filter_dn:
            jobs = jobs.filter(Job.user_dn == filter_dn)
        if filter_vo:
            jobs = jobs.filter(Job.vo_name == filter_vo)
        if filter_dlg_id:
            jobs = jobs.filter(Job.cred_id == filter_dlg_id)

        # Return list, limiting the size
        return jobs.limit(100).all()

    @doc.response(404, 'The job doesn\'t exist')
    @doc.return_type(Job)
    @jsonify
    def show(self, id, **kwargs):
        """
        Get the job with the given ID
        """
        job = self._get_job(id)
        # Trigger the query, so it is serialized
        files = job.files
        return job

    @doc.response(404, 'The job or the field doesn\'t exist')
    @jsonify
    def showField(self, id, field, **kwargs):
        """
        Get a specific field from the job identified by id
        """
        job = self._get_job(id)
        if hasattr(job, field):
            return getattr(job, field)
        else:
            abort(404, 'No such field')

    @doc.response(404, 'The job doesn\'t exist')
    @doc.return_type(Job)
    @jsonify
    def cancel(self, id, **kwargs):
        """
        Cancel the given job
        
        Returns the canceled job with its current status. CANCELED if it was canceled,
        its final status otherwise
        """
        job = self._get_job(id)

        if job.job_state in JobActiveStates:
            now = datetime.utcnow()

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

            job = self._get_job(id)

        files = job.files
        return job

    @doc.input('Submission description', 'SubmitSchema')
    @doc.response(400, 'The submission request could not be understood')
    @doc.response(403, 'The user doesn\'t have enough permissions to submit')
    @doc.response(419, 'The credentials need to be re-delegated')
    @doc.return_type(Job)
    @authorize(TRANSFER)
    @jsonify
    def submit(self, **kwargs):
        """
        Submits a new job
        
        It returns the information about the new submitted job. To know the format for the
        submission, /api-docs/schema/submit gives the expected format encoded as a JSON-schema.
        It can be used to validate (i.e in Python, jsonschema.validate)
        """
        # First, the request has to be valid JSON
        try:
            if request.method == 'PUT':
                unencoded_body = request.body
            elif request.method == 'POST':
                if request.content_type == 'application/json':
                    unencoded_body = request.body
                else:
                    unencoded_body = urllib.unquote_plus(request.body)
            else:
                abort(400, 'Unsupported method %s' % request.method)

            submitted_dict = json.loads(unencoded_body)

        except ValueError, e:
            abort(400, 'Badly formatted JSON request (%s)' % str(e))

        # The auto-generated delegation id must be valid
        user = request.environ['fts3.User.Credentials']
        credential = Session.query(Credential).get((user.delegation_id, user.user_dn))
        if credential is None:
            abort(419, 'No delegation id found for "%s"' % user.user_dn)
        if credential.expired():
            remaining = credential.remaining()
            seconds = abs(remaining.seconds + remaining.days * 24 * 3600)
            abort(419, 'The delegated credentials expired %d seconds ago' % seconds)
        if credential.remaining() < timedelta(hours=1):
            abort(419, 'The delegated credentials has less than one hour left')

        # Populate the job and file
        job = _setup_job_from_dict(submitted_dict, user)

        # Validate that there are no bad combinations
        if job.reuse_job and _has_multiple_options(job.files):
            abort(400,
                  'Can not specify reuse and multiple replicas at the same time')

        # Update the database
        Session.merge(job)
        Session.flush()

        # Update hashed_id and vo_name, while updating OptimizerActive
        # Mind that, for reuse jobs, we hash the job_id!
        hashed_job_id = _hashed_id(job.job_id)
        for file in Session.query(File).filter(File.job_id == job.job_id):
            if job.reuse_job:
                file.hashed_id = hashed_job_id
            else:
                file.hashed_id = _hashed_id(file.file_id)
            file.vo_name   = job.vo_name
            Session.merge(file)
            
            optimizer_active = OptimizerActive()
            optimizer_active.source_se = file.source_se
            optimizer_active.dest_se = file.dest_se
            Session.merge(optimizer_active)

        # Commit and return
        Session.commit()
        return job

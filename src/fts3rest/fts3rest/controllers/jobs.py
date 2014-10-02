#   Copyright notice:
#   Copyright  Members of the EMI Collaboration, 2013.
#
#   See www.eu-emi.eu for details on the copyright holders
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from datetime import datetime, timedelta
from pylons import request
from sqlalchemy.orm import noload
import hashlib
import json
import logging
import pylons
import socket
import types
import urllib
import urlparse
import uuid

from fts3.model import Job, File, JobActiveStates, FileActiveStates
from fts3.model import DataManagement, DataManagementActiveStates
from fts3.model import Credential, OptimizerActive, BannedSE, FileRetryLog
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.http_exceptions import *
from fts3rest.lib.middleware.fts3auth import authorize, authorized
from fts3rest.lib.middleware.fts3auth.constants import *


log = logging.getLogger(__name__)

DEFAULT_PARAMS = {
    'bring_online': -1,
    'verify_checksum': False,
    'copy_pin_lifetime': -1,
    'gridftp': '',
    'job_metadata': None,
    'overwrite': False,
    'reuse': False,
    'multihop': False,
    'source_spacetoken': '',
    'spacetoken': '',
    'retry': 0
}


def _set_job_source_and_destination(job, files):
    """
    Iterates through the files that belong to the job, and determines the
    'overall' job source and destination Storage Elements
    """
    if job['reuse_job'] == 'H':
        job['source_se'] = files[0]['source_se']
        job['dest_se'] = files[-1]['dest_se']
    else:
        job['source_se'] = files[0]['source_se']
        job['dest_se'] = files[0]['dest_se']
        for f in files:
            if f['source_se'] != job['source_se']:
                job['source_se'] = None
            if f['dest_se'] != job['dest_se']:
                job['dest_se'] = None


def _get_storage_element(uri):
    """
    Returns the storage element of the given uri, which is the scheme + hostname without the port

    Args:
        uri: An urlparse instance
    """
    return "%s://%s" % (uri.scheme, uri.hostname)


def _yes_or_no(value):
    if isinstance(value, types.StringType) or isinstance(value, types.UnicodeType):
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
    ids = map(lambda f: f['file_index'], files)
    id_count = len(ids)
    unique_id_count = len(set(ids))
    return unique_id_count != id_count


def _valid_third_party_transfer(src_scheme, dst_scheme):
    """
    Return True if the source scheme and the destination scheme define a
    third party transfer
    """
    forbidden_schemes = ['', 'file']
    return src_scheme not in forbidden_schemes and \
        dst_scheme not in forbidden_schemes and \
        (src_scheme == dst_scheme or
         src_scheme in ['srm', 'lfc'] or
         dst_scheme in ['srm', 'lfc'])


def _validate_url(url):
    """
    Validates the format and content of the url
    """
    if not url.scheme:
        raise ValueError('Missing scheme (%s)' % url.geturl())
    if url.scheme == 'file':
        raise ValueError('Can not transfer local files (%s)' % url.geturl())
    if not url.path or (url.path == '/' and not url.query):
        raise ValueError('Missing path (%s)' % url.geturl())
    if not url.hostname or url.hostname == '':
        raise ValueError('Missing host (%s)' % url.geturl())


def _valid_filesize(value):
    if isinstance(value, float):
        return value
    elif value is None:
        return 0.0
    else:
        return float(value)


def _generate_hashed_id(job_id, f_index):
    """
    Generates a hashed if from the job_id and the file index inside this job
    """
    concat = "%s:%d" % (job_id, f_index)
    return int(hashlib.md5(concat).hexdigest()[-4:], 16)


def _populate_files(files_dict, job_id, f_index, vo_name, shared_hashed_id=None):
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
            dest_url = urlparse.urlparse(d.strip())
            _validate_url(dest_url)
            pairs.append((source_url, dest_url))

    # Create one File entry per matching pair
    initial_state='SUBMITTED'
    if len(files_dict['sources']) > 1 and len(files_dict['destinations']) == 1:
        initial_state='NOT_USED'
        if not shared_hashed_id:
            shared_hashed_id = _generate_hashed_id(job_id, f_index)

    for (s, d) in pairs:
        f = dict(
            job_id=job_id,
            file_index=f_index,
            file_state=initial_state,
            source_surl=s.geturl(),
            dest_surl=d.geturl(),
            source_se=_get_storage_element(s),
            dest_se=_get_storage_element(d),
            vo_name=vo_name,
            user_filesize=_valid_filesize(files_dict.get('filesize', 0)),
            selection_strategy=files_dict.get('selection_strategy', None),
            checksum=files_dict.get('checksum', None),
            file_metadata=files_dict.get('metadata', None),
            activity=files_dict.get('activity', 'default'),
            hashed_id=shared_hashed_id if shared_hashed_id else _generate_hashed_id(job_id, f_index)
        )
        files.append(f)

    if len(files) > 0 and initial_state == 'NOT_USED':
        files[0]['file_state']='SUBMITTED'

    return files

def _build_internal_job_params(params):
    """
    Generates the value for job.internal_job_params depending on the
    received protocol parameters
    """
    param_list = list()
    if 'nostreams' in params:
        param_list.append("nostreams:%d" % int(params['nostreams']))
    if 'timeout' in params:
        param_list.append("timeout:%d" % int(params['timeout']))
    if 'buffer_size' in params:
        param_list.append("buffersize:%d" % int(params['buffer_size']))
    if 'strict_copy' in params:
        param_list.append("strict")
    if len(param_list) == 0:
        return None
    else:
        return ','.join(param_list)


def _submit_transfer(user, job_dict, params):
    """
    Submit a transfer job
    Returns a pair job, array of File
    """
    reuse_flag = 'N'
    if params['multihop']:
        reuse_flag = 'H'
    elif _yes_or_no(params['reuse']):
        reuse_flag = 'Y'

    job_id = str(uuid.uuid1())
    job = dict(
        job_id=job_id,
        job_state='SUBMITTED',
        reuse_job=reuse_flag,
        retry=int(params['retry']),
        job_params=params['gridftp'],
        submit_host=socket.getfqdn(),
        agent_dn='rest',
        user_dn=user.user_dn,
        voms_cred=' '.join(user.voms_cred),
        vo_name=user.vos[0],
        submit_time=datetime.utcnow(),
        priority=3,
        space_token=params['spacetoken'],
        overwrite_flag=_yes_or_no(params['overwrite']),
        source_space_token=params['source_spacetoken'],
        copy_pin_lifetime=int(params['copy_pin_lifetime']),
        checksum_method=params['verify_checksum'],
        bring_online=params['bring_online'],
        job_metadata=params['job_metadata'],
        internal_job_params=_build_internal_job_params(params)
    )

    if 'credential' in params:
        job['user_cred'] = params['credential']
    elif 'credentials' in params:
        job['user_cred'] = params['credentials']
    job['cred_id'] = user.delegation_id

    # If reuse is enabled, generate one single "hash" for all files
    if reuse_flag in ('H', 'Y'):
        shared_hashed_id = _generate_hashed_id(job_id, 0)
    else:
        shared_hashed_id = None

    # Files
    files = []
    f_index = 0
    for t in job_dict['files']:
        files.extend(_populate_files(t, job_id, f_index, job['vo_name'], shared_hashed_id))
        f_index += 1

    if len(files) == 0:
        raise HTTPBadRequest('No valid pairs available')

    # If copy_pin_lifetime OR bring_online are specified, go to staging directly
    if job['copy_pin_lifetime'] > 0 or job['bring_online'] > 0:
        job['job_state'] = 'STAGING'
        for t in files:
            t['file_state'] = 'STAGING'

    # If a checksum is provided, but no checksum is available, 'relaxed' comparison
    # (Not nice, but need to keep functionality!)
    has_checksum = False
    for f in files:
        if f['checksum'] is not None:
            has_checksum = len(f['checksum']) > 0
            break
    if not job['checksum_method'] and has_checksum:
        job['checksum_method'] = 'r'

    _set_job_source_and_destination(job, files)

    return job, files


def _submit_deletion(user, job_dict, params):
    """
    Submit a deletion job.
    Returns a pair job, array of DataManagement
    """
    job_id = str(uuid.uuid1())
    job = dict(
        job_id=job_id,
        job_state='DELETE',
        reuse_job=None,
        retry=int(params['retry']),
        job_params=params['gridftp'],
        submit_host=socket.getfqdn(),
        agent_dn='rest',
        user_dn=user.user_dn,
        voms_cred=' '.join(user.voms_cred),
        vo_name=user.vos[0],
        submit_time=datetime.utcnow(),
        priority=3,
        space_token=params['spacetoken'],
        overwrite_flag='N',
        source_space_token=params['source_spacetoken'],
        copy_pin_lifetime=-1,
        checksum_method=None,
        bring_online=None,
        job_metadata=params['job_metadata'],
        internal_job_params=None
    )

    if 'credential' in params:
        job['user_cred'] = params['credential']
    elif 'credentials' in params:
        job['user_cred'] = params['credentials']
    job['cred_id'] = user.delegation_id

    shared_hashed_id = _generate_hashed_id(job_id, 0)

    datamanagement = []
    for dm in job_dict['delete']:
        if isinstance(dm, dict):
            entry = dm
        elif isinstance(dm, str) or isinstance(dm, unicode):
            entry = dict(surl=dm)
        else:
            raise ValueError("Invalid type for the deletion item (%s)" % type(dm))
        surl = urlparse.urlparse(entry['surl'])
        _validate_url(surl)
        datamanagement.append(dict(
            job_id=job_id,
            vo_name=user.vos[0],
            file_state='DELETE',
            source_surl=entry['surl'],
            source_se=_get_storage_element(surl),
            dest_surl = None,
            dest_se = None,
            hashed_id=shared_hashed_id,
            file_metadata=entry.get('metadata', None)
        ))

    _set_job_source_and_destination(job, datamanagement)

    return job, datamanagement


def _setup_job_from_dict(job_dict, user):
    """
    From the submitted dictionary, create and populate dictionaries
    suitable for insertion
    """
    try:
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

        if job_dict.get('files', None) and job_dict.get('delete', None):
            raise HTTPBadRequest('Transfer and metadata simultaneous operations not supported')
        elif job_dict.get('files', None):
            job, files = _submit_transfer(user, job_dict, params)
            datamanagement = list()
        elif job_dict.get('delete', None):
            job, datamanagement = _submit_deletion(user, job_dict, params)
            files = list()
        else:
            raise HTTPBadRequest('No transfers specified')

        return job, files, datamanagement

    except ValueError, e:
        raise HTTPBadRequest('Invalid value within the request: %s' % str(e))
    except TypeError, e:
        raise HTTPBadRequest('Malformed request: %s' % str(e))
    except KeyError, e:
        raise HTTPBadRequest('Missing parameter: %s' % str(e))


def _apply_banning(files):
    """
    Query the banning information for all pairs, reject the job
    as soon as one SE can not submit.
    Update wait_timeout and wait_timestamp is there is a hit
    """
    # Usually, banned SES will be in the order of ~100 max
    # Files may be several thousands
    # We get all banned in memory so we avoid querying too many times the DB
    # We then build a dictionary to make look up easy
    banned_ses = dict()
    for b in Session.query(BannedSE):
        banned_ses[str(b.se)] = (b.vo, b.status, b.wait_timeout)

    now = datetime.utcnow()
    for f in files:
        source_banned = banned_ses.get(str(f['source_se']), None)
        dest_banned = banned_ses.get(str(f['dest_se']), None)
        timeout = None

        if source_banned and (source_banned[0] == f['vo_name'] or source_banned[0] is None):
            if source_banned[1] != 'WAIT_AS':
                raise HTTPForbidden("%s is banned" % f['source_se'])
            timeout = source_banned[2]

        if dest_banned and (dest_banned[0] == f['vo_name'] or dest_banned[0] is None):
            if dest_banned[1] != 'WAIT_AS':
                raise HTTPForbidden("%s is banned" % f['dest_se'])
            if not timeout:
                timeout = dest_banned[2]
            else:
                timeout = max(timeout, dest_banned[2])

        if timeout is not None:
            f['wait_timestamp'] = now
            f['wait_timeout'] = timeout


class JobsController(BaseController):
    """
    Operations on jobs and transfers
    """

    @staticmethod
    def _get_job(job_id):
        job = Session.query(Job).get(job_id)
        if job is None:
            raise HTTPNotFound('No job with the id "%s" has been found' % job_id)
        if not authorized(TRANSFER,
                          resource_owner=job.user_dn, resource_vo=job.vo_name):
            raise HTTPForbidden('Not enough permissions to check the job "%s"' % job_id)
        return job

    def options(self):
        """
        Answer the OPTIONS method over /jobs
        """
        pylons.response.headers['Allow'] = 'PUT, POST, GET, OPTIONS'
        return []

    def job_options(self, job_id):
        """
        Answers the OPTIONS method over /jobs/job-id
        """
        pylons.response.headers['Allow'] = 'GET, DELETE'
        return []

    @doc.query_arg('user_dn', 'Filter by user DN')
    @doc.query_arg('vo_name', 'Filter by VO')
    @doc.query_arg('dlg_id', 'Filter by delegation ID')
    @doc.query_arg('state_in', 'Comma separated list of job states to filter. ACTIVE only by default')
    @doc.query_arg('source_se', 'Source storage element')
    @doc.query_arg('dest_se', 'Destination storage element')
    @doc.query_arg('limit', 'Limit the number of results')
    @doc.response(403, 'Operation forbidden')
    @doc.response(400, 'DN and delegation ID do not match')
    @doc.return_type(array_of=Job)
    @authorize(TRANSFER)
    @jsonify
    def index(self):
        """
        Get a list of active jobs, or those that match the filter requirements
        """
        user = request.environ['fts3.User.Credentials']

        jobs = Session.query(Job)

        filter_dn = request.params.get('user_dn', None)
        filter_vo = request.params.get('vo_name', None)
        filter_dlg_id = request.params.get('dlg_id', None)
        filter_state = request.params.get('state_in', None)
        filter_source = request.params.get('source_se', None)
        filter_dest = request.params.get('dest_se', None)
        try:
            filter_limit = int(request.params.get('limit', 0))
        except:
            filter_limit = 0

        if filter_dlg_id and filter_dlg_id != user.delegation_id:
            raise HTTPForbidden('The provided delegation id does not match your delegation id')
        if filter_dlg_id and filter_dn and filter_dn != user.user_dn:
            raise HTTPBadRequest('The provided DN and delegation id do not correspond to the same user')
        if not filter_dlg_id and filter_state:
            raise HTTPForbidden('To filter by state, you need to provide dlg_id')
        if filter_limit < 0 or filter_limit > 500:
            raise HTTPBadRequest('The limit must be positive and less or equal than 500')

        if filter_state:
            filter_state = filter_state.split(',')
            jobs = jobs.filter(Job.job_state.in_(filter_state))
            if not filter_limit:
                filter_not_before = datetime.utcnow() - timedelta(hours=1)
                jobs = jobs.filter((Job.job_finished == None) | (Job.job_finished >= filter_not_before))
        else:
            jobs = jobs.filter(Job.job_finished == None)

        if filter_dn:
            jobs = jobs.filter(Job.user_dn == filter_dn)
        if filter_vo:
            jobs = jobs.filter(Job.vo_name == filter_vo)
        if filter_dlg_id:
            jobs = jobs.filter(Job.cred_id == filter_dlg_id)
        if filter_source:
            jobs = jobs.filter(Job.source_se == filter_source)
        if filter_dest:
            jobs = jobs.filter(Job.dest_se == filter_dest)

        if filter_limit:
            return jobs[:filter_limit]
        else:
            return jobs.all()

    @doc.query_arg('files', 'Comma separated list of file fields to retrieve in this query')
    @doc.response(404, 'The job doesn\'t exist')
    @doc.response(413, 'The user doesn\'t have enough privileges')
    @doc.return_type(Job)
    @jsonify
    def get(self, job_id):
        """
        Get the job with the given ID
        """
        job = JobsController._get_job(job_id)

        if 'files' in request.GET:
            fields = request.GET['files'].split(',')
            files = list()
            log.info('XXX')
            for f in Session.query(File).filter(File.job_id == job.job_id).all():
                fd = dict()
                for field in fields:
                    try:
                        fd[field] = getattr(f, field)
                    except:
                        pass
                files.append(fd)
            job.__dict__['files'] = files

        return job

    @doc.response(404, 'The job or the field doesn\'t exist')
    @doc.response(413, 'The user doesn\'t have enough privileges')
    @jsonify
    def get_field(self, job_id, field):
        """
        Get a specific field from the job identified by id
        """
        job = JobsController._get_job(job_id)
        if hasattr(job, field):
            return getattr(job, field)
        else:
            raise HTTPNotFound('No such field')

    @doc.response(404, 'The job doesn\'t exist')
    @doc.response(413, 'The user doesn\'t have enough privileges')
    @doc.return_type(array_of=File)
    @jsonify
    def get_files(self, job_id):
        """
        Get the files within a job
        """
        owner = Session.query(Job.user_dn, Job.vo_name).filter(Job.job_id == job_id).first()
        if owner is None:
            raise HTTPNotFound('No job with the id "%s" has been found' % job_id)
        if not authorized(TRANSFER, resource_owner=owner[0], resource_vo=owner[1]):
            raise HTTPForbidden('Not enough permissions to check the job "%s"' % job_id)
        files = Session.query(File).filter(File.job_id == job_id).options(noload(File.retries))
        return files.all()

    @doc.response(404, 'The job or the file don\'t exist')
    @doc.response(413, 'The user doesn\'t have enough privileges')
    @jsonify
    def get_file_retries(self, job_id, file_id):
        """
        Get the retries for a given file
        """
        owner = Session.query(Job.user_dn, Job.vo_name).filter(Job.job_id == job_id).all()
        if owner is None or len(owner) < 1:
            raise HTTPNotFound('No job with the id "%s" has been found' % job_id)
        if not authorized(TRANSFER,
                          resource_owner=owner[0][0], resource_vo=owner[0][1]):
            raise HTTPForbidden('Not enough permissions to check the job "%s"' % job_id)
        f = Session.query(File.file_id).filter(File.file_id == file_id)
        if not f:
            raise HTTPNotFound('No file with the id "%d" has been found' % file_id)
        retries = Session.query(FileRetryLog).filter(FileRetryLog.file_id == file_id)
        return retries.all()

    @doc.response(207, 'For multiple job requests if there has been any error')
    @doc.response(404, 'The job doesn\'t exist')
    @doc.response(413, 'The user doesn\'t have enough privileges')
    @doc.return_type(Job)
    @jsonify
    def cancel(self, job_id_list, start_response):
        """
        Cancel the given job

        Returns the canceled job with its current status. CANCELED if it was canceled,
        its final status otherwise
        """
        requested_job_ids = job_id_list.split(',')
        cancellable_jobs = list()
        response = list()
        multistatus = False

        # First, check which job ids exist and can be accessed
        for job_id in requested_job_ids:
            if not job_id:  # Skip empty
                continue
            try:
                job = JobsController._get_job(job_id)
                if job.job_state in JobActiveStates:
                    cancellable_jobs.append(job)
                else:
                    setattr(job, 'http_status', '304 Not Modified')
                    setattr(job, 'http_message', 'The job is in a terminal state')
                    log.warning("The job %s can not be canceled, since it is %s" % (job_id, job.job_state))
                    response.append(job)
                    multistatus = True
            except HTTPClientError, e:
                response.append(dict(
                    job_id=job_id,
                    http_status="%s %s" % (e.code, e.title),
                    http_message=e.detail
                ))
                multistatus = True

        # Now, cancel those that can be canceled
        now = datetime.utcnow()
        try:
            for job in cancellable_jobs:
                job.job_state = 'CANCELED'
                job.finish_time = now
                job.job_finished = now
                job.reason = 'Job canceled by the user'

                Session.query(File).filter(File.job_id == job.job_id).filter(File.file_state.in_(FileActiveStates))\
                    .update({
                        'file_state': 'CANCELED', 'reason': 'Job canceled by the user',
                        'job_finished': now, 'finish_time': now
                    })
                Session.query(DataManagement).filter(DataManagement.job_id == job.job_id)\
                    .filter(DataManagement.file_state.in_(DataManagementActiveStates))\
                    .update({
                        'file_state': 'CANCELED', 'reason': 'Job canceled by the user',
                        'job_finished': now, 'finish_time': now
                    })
                job = Session.merge(job)

                log.info("Job %s canceled" % job.job_id)
                setattr(job, 'http_status', "200 Ok")
                setattr(job, 'http_message', None)
                response.append(job)
            Session.commit()
        except:
            Session.rollback()
            raise

        # Return 200 if everything is Ok, 207 if there is any errors,
        # and, if input was only one, do not return an array
        if len(requested_job_ids) == 1:
            single = response[0]
            if isinstance(single, Job):
                if single.http_status not in ('200 Ok', '304 Not Modified'):
                    start_response(single.http_status, [('Content-Type', 'application/json')])
            elif single['http_status'] not in ('200 Ok', '304 Not Modified'):
                start_response(single['http_status'], [('Content-Type', 'application/json')])
            return single

        if multistatus:
            start_response("207 Multi-Status", [('Content-Type', 'application/json')])
        return response

    @doc.input('Submission description', 'SubmitSchema')
    @doc.response(400, 'The submission request could not be understood')
    @doc.response(403, 'The user doesn\'t have enough permissions to submit')
    @doc.response(419, 'The credentials need to be re-delegated')
    @doc.return_type('{"job_id": <job id>}')
    @authorize(TRANSFER)
    @jsonify
    def submit(self):
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
                raise HTTPBadRequest('Unsupported method %s' % request.method)

            submitted_dict = json.loads(unencoded_body)

        except ValueError, e:
            raise HTTPBadRequest('Badly formatted JSON request (%s)' % str(e))

        # The auto-generated delegation id must be valid
        user = request.environ['fts3.User.Credentials']
        credential = Session.query(Credential).get((user.delegation_id, user.user_dn))
        if credential is None:
            raise HTTPAuthenticationTimeout('No delegation found for "%s"' % user.user_dn)
        if credential.expired():
            remaining = credential.remaining()
            seconds = abs(remaining.seconds + remaining.days * 24 * 3600)
            raise HTTPAuthenticationTimeout(
                'The delegated credentials expired %d seconds ago (%s)' % (seconds, user.delegation_id)
            )
        if credential.remaining() < timedelta(hours=1):
            raise HTTPAuthenticationTimeout(
                'The delegated credentials has less than one hour left (%s)' % user.delegation_id
            )

        # Populate the job and files
        job, files, datamanagement = _setup_job_from_dict(submitted_dict, user)

        # Reject for SE banning
        # If any SE does not accept submissions, reject the whole job
        # Update wait_timeout and wait_timestamp if WAIT_AS is set
        _apply_banning(files)
        _apply_banning(datamanagement)

        # Validate that there are no bad combinations
        if _has_multiple_options(files):
            if job['reuse_job'] == 'Y':
                raise HTTPBadRequest('Can not specify reuse and multiple replicas at the same time')
            job['reuse_job'] = 'R'

        # Update the optimizer
        unique_pairs = set(map(lambda f: (f['source_se'], f['dest_se']), files))
        for (source_se, dest_se) in unique_pairs:
            optimizer_active = OptimizerActive()
            optimizer_active.source_se = source_se
            optimizer_active.dest_se = dest_se
            Session.merge(optimizer_active)

        # Update the database
        try:
            Session.execute(Job.__table__.insert(), [job])
            if len(files):
                Session.execute(File.__table__.insert(), files)
            if len(datamanagement):
                Session.execute(DataManagement.__table__.insert(), datamanagement)
            Session.commit()
        except:
            Session.rollback()
            raise

        if len(files):
            log.info("Job %s submitted with %d transfers" % (job['job_id'], len(files)))
        else:
            log.info("Job %s submitted with %d data management operations" % (job['job_id'], len(datamanagement)))

        return {'job_id': job['job_id']}

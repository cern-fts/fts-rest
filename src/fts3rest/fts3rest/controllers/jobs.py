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
from requests.exceptions import HTTPError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import noload

from fts3rest.lib.helpers.msgbus import submit_state_change

try:
    import simplejson as json
except ImportError:
    import json
import logging

from fts3.model import Job, File, JobActiveStates, FileActiveStates
from fts3.model import DataManagement, DataManagementActiveStates
from fts3.model import Credential, FileRetryLog
from fts3.model import CloudStorage, CloudStorageUser
from fts3rest.lib.JobBuilder import JobBuilder
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify, get_input_as_dict, swift
from fts3rest.lib.http_exceptions import *
from fts3rest.lib.middleware.fts3auth import authorize, authorized
from fts3rest.lib.middleware.fts3auth.constants import *


log = logging.getLogger(__name__)

def _multistatus(responses, start_response, expecting_multistatus=False):
    """
    Return 200 if everything is Ok, 207 if there is any errors,
    and, if input was only one, do not return an array
    """
    if not expecting_multistatus:
        single = responses[0]
        if isinstance(single, Job):
            if single.http_status not in ('200 Ok', '304 Not Modified'):
                start_response(single.http_status, [('Content-Type', 'application/json')])
        elif single['http_status'] not in ('200 Ok', '304 Not Modified'):
            start_response(single['http_status'], [('Content-Type', 'application/json')])
        return single

    for response in responses:
        if isinstance(response, dict) and not response.get('http_status', '').startswith('2'):
            start_response("207 Multi-Status", [('Content-Type', 'application/json')])
            break
    return responses


def _set_swift_credentials(se_url, user_dn, access_token):
    storage_name = 'SWIFT:' + se_url[se_url.rfind('/') + 1:]
    cloud_user = Session.query(CloudStorageUser).filter_by(user_dn=user_dn, storage_name=storage_name).one()
    cloud_storage = Session.query(CloudStorage).get(storage_name)
    if cloud_user and cloud_storage:
        try:
            cloud_user = swift.get_os_token(cloud_user, access_token, cloud_storage)
            Session.merge(cloud_user)
            Session.commit()
        except Exception as ex:
            log.warning("Failed to retrieve OS token for dn: %s because: %s" % (user_dn, str(ex)))
            Session.rollback()
    else:
        log.info("Error retrieving cloud user %s for storage %s", (user_dn, storage_name))


class JobsController(BaseController):
    """
    Operations on jobs and transfers
    """

    @staticmethod
    def _get_job(job_id, env=None):
        job = Session.query(Job).get(job_id)
        if job is None:
            raise HTTPNotFound('No job with the id "%s" has been found' % job_id)
        if not authorized(TRANSFER,
                          resource_owner=job.user_dn, resource_vo=job.vo_name,
                          env=env):
            raise HTTPForbidden('Not enough permissions to check the job "%s"' % job_id)
        return job

    @doc.query_arg('user_dn', 'Filter by user DN')
    @doc.query_arg('vo_name', 'Filter by VO')
    @doc.query_arg('dlg_id', 'Filter by delegation ID')
    @doc.query_arg('state_in', 'Comma separated list of job states to filter. ACTIVE only by default')
    @doc.query_arg('source_se', 'Source storage element')
    @doc.query_arg('dest_se', 'Destination storage element')
    @doc.query_arg('limit', 'Limit the number of results')
    @doc.query_arg('time_window', 'For terminal states, limit results to hours[:minutes] into the past')
    @doc.query_arg('fields', 'Return only a subset of the fields')
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
        filter_fields = request.params.get('fields', None)
        try:
            filter_limit = int(request.params['limit'])
        except:
            filter_limit = None
        try:
            components = request.params['time_window'].split(':')
            hours = components[0]
            minutes = components[1] if len(components) > 1 else 0
            filter_time = timedelta(hours=int(hours), minutes=int(minutes))
        except:
            filter_time = None

        if filter_dlg_id and filter_dlg_id != user.delegation_id:
            raise HTTPForbidden('The provided delegation id does not match your delegation id')
        if filter_dn and filter_dn != user.user_dn:
            raise HTTPBadRequest('The provided DN and delegation id do not correspond to the same user')
        if filter_limit is not None and filter_limit < 0 or filter_limit > 500:
            raise HTTPBadRequest('The limit must be positive and less or equal than 500')

        # Automatically apply filters depending on granted level
        granted_level = user.get_granted_level_for(TRANSFER)
        if granted_level == PRIVATE:
            filter_dlg_id = user.delegation_id
        elif granted_level == VO:
            filter_vo = user.vos[0]
        elif granted_level == NONE:
            raise HTTPForbidden('User not allowed to list jobs')

        if filter_state:
            filter_state = filter_state.split(',')
            jobs = jobs.filter(Job.job_state.in_(filter_state))
            if filter_limit is None:
                if filter_time is not None:
                    filter_not_before = datetime.utcnow() - filter_time
                    jobs = jobs.filter(Job.job_finished >= filter_not_before)
                else:
                    jobs = jobs.filter(Job.job_finished == None)
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
            jobs = jobs.order_by(Job.submit_time.desc())[:filter_limit]
        else:
            jobs = jobs.yield_per(100).enable_eagerloads(False)

        if filter_fields:
            original_jobs = jobs

            def _field_subset():
                fields = filter_fields.split(',')
                for job in original_jobs:
                    entry = dict()
                    for field in fields:
                        if hasattr(job, field):
                            entry[field] = getattr(job, field)
                    yield entry

            jobs = _field_subset()

        return jobs

    @doc.query_arg('files', 'Comma separated list of file fields to retrieve in this query')
    @doc.response(200, 'The jobs exist')
    @doc.response(207, 'Some job had an error')
    @doc.response(403, 'The user doesn\'t have enough privileges')
    @doc.response(404, 'The job doesn\'t exist')
    @doc.return_type(Job)
    @jsonify
    def get(self, job_list, start_response):
        """
        Get the job with the given ID
        """
        job_ids = job_list.split(',')
        status_error_count = 0

        # request is not available inside the generator
        environ = request.environ
        if 'files' in request.GET:
            file_fields = request.GET['files'].split(',')
        else:
            file_fields = []

        statuses = list()
        for job_id in filter(len, job_ids):
            try:
                job = JobsController._get_job(job_id, env=environ)
                if len(file_fields):
                    class FileIterator(object):
                        def __init__(self, job_id):
                            self.job_id = job_id

                        def __call__(self):
                            for f in Session.query(File).filter(File.job_id == self.job_id):
                                fd = dict()
                                for field in file_fields:
                                    try:
                                        fd[field] = getattr(f, field)
                                    except AttributeError:
                                        pass
                                yield fd
                    job.__dict__['files'] = FileIterator(job.job_id)()
                setattr(job, 'http_status', '200 Ok')
                statuses.append(job)
            except HTTPError, e:
                statuses.append(dict(
                    job_id=job_id,
                    http_status="%s %s" % (e.code, e.title),
                    http_message=e.detail
                ))
                status_error_count += 1

        if len(job_ids) == 1:
            if status_error_count == 1:
                start_response(statuses[0].get('http_status'), [('Content-Type', 'application/json')])
            return statuses[0]
        elif status_error_count > 0:
            start_response('207 Multi-Status', [('Content-Type', 'application/json')])

        return statuses

    @doc.response(403, 'The user doesn\'t have enough privileges')
    @doc.response(404, 'The job or the field doesn\'t exist')
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

    @doc.response(403, 'The user doesn\'t have enough privileges')
    @doc.response(404, 'The job doesn\'t exist')
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
        return files.yield_per(100).enable_eagerloads(False)

    @doc.response(403, 'The user doesn\'t have enough privileges')
    @doc.response(404, 'The job doesn\'t exist')
    @doc.return_type(array_of=DataManagement)
    @jsonify
    def get_dm(self, job_id):
        """
        Get the data management tasks within a job
        """
        owner = Session.query(Job.user_dn, Job.vo_name).filter(Job.job_id == job_id).first()
        if owner is None:
            raise HTTPNotFound('No job with the id "%s" has been found' % job_id)
        if not authorized(TRANSFER, resource_owner=owner[0], resource_vo=owner[1]):
            raise HTTPForbidden('Not enough permissions to check the job "%s"' % job_id)
        dm = Session.query(DataManagement).filter(DataManagement.job_id == job_id)
        return dm.yield_per(100).enable_eagerloads(False)

    @doc.response(403, 'The user doesn\'t have enough privileges')
    @doc.response(404, 'The job doesn\'t exist')
    @doc.return_type('File final states (array if multiple files were given)')
    @jsonify
    def cancel_files(self, job_id, file_ids):
        """
        Cancel individual files - comma separated for multiple - within a job
        """
        job = self._get_job(job_id)

        if job.job_type != 'N':
            raise HTTPBadRequest('Multihop or reuse jobs must be cancelled at once (%s)' % str(job.job_type))

        file_ids = file_ids.split(',')
        changed_states = list()

        try:
            # Mark files in the list as CANCELED
            for file_id in file_ids:
                file = Session.query(File).get(file_id)
                if not file or file.job_id != job_id:
                    changed_states.append('File does not belong to the job')
                    continue

                if file.file_state not in FileActiveStates:
                    changed_states.append(file.file_state)
                    continue

                file.file_state = 'CANCELED'
                file.finish_time = datetime.utcnow()
                file.dest_surl_uuid = None
                changed_states.append('CANCELED')
                Session.merge(file)

            # Mark job depending on the status of the rest of files
            not_changed_states = map(lambda f: f.file_state, filter(lambda f: f.file_id not in file_ids, job.files))
            all_states = not_changed_states + changed_states

            # All files within the job have been canceled
            if len(not_changed_states) == 0:
                job.job_state = 'CANCELED'
                job.cancel_job = True
                job.job_finished = datetime.utcnow()
                log.warning('Cancelling all remaining files within the job %s' % job_id)
            # No files in non-terminal, mark the job as CANCELED too
            elif len(filter(lambda s: s in FileActiveStates, all_states)) == 0:
                log.warning('Cancelling a file within a job with others in terminal state (%s)' % job_id)
                job.job_state = 'CANCELED'
                job.cancel_job = True
                job.job_finished = datetime.utcnow()
            else:
                log.warning('Cancelling files within a job with others still active (%s)' % job_id)

            Session.merge(job)
            Session.commit()
        except:
            Session.rollback()
            raise
        return changed_states if len(changed_states) > 1 else changed_states[0]

    @doc.response(403, 'The user doesn\'t have enough privileges')
    @doc.response(404, 'The job or the file don\'t exist')
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
    @doc.response(403, 'The user doesn\'t have enough privileges')
    @doc.response(404, 'The job doesn\'t exist')
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
        responses = list()

        # First, check which job ids exist and can be accessed
        for job_id in requested_job_ids:
            # Skip empty
            if not job_id:
                continue
            try:
                job = JobsController._get_job(job_id)
                if job.job_state in JobActiveStates:
                    cancellable_jobs.append(job)
                else:
                    setattr(job, 'http_status', '304 Not Modified')
                    setattr(job, 'http_message', 'The job is in a terminal state')
                    log.warning("The job %s can not be canceled, since it is %s" % (job_id, job.job_state))
                    responses.append(job)
            except HTTPClientError, e:
                responses.append(dict(
                    job_id=job_id,
                    http_status="%s %s" % (e.code, e.title),
                    http_message=e.detail
                ))

        # Now, cancel those that can be canceled
        now = datetime.utcnow()
        try:
            for job in cancellable_jobs:
                job.job_state = 'CANCELED'
                job.cancel_job = True
                job.job_finished = now
                job.reason = 'Job canceled by the user'

                # FTS3 daemon expects finish_time to be NULL in order to trigger the signal
                # to fts_url_copy, but this only makes sense if pid is set
                Session.query(File).filter(File.job_id == job.job_id)\
                    .filter(File.file_state.in_(FileActiveStates), File.pid != None)\
                    .update({
                        'file_state': 'CANCELED', 'reason': 'Job canceled by the user', 'dest_surl_uuid':None,
                        'finish_time': None 
                    }, synchronize_session=False)
                Session.query(File).filter(File.job_id == job.job_id)\
                    .filter(File.file_state.in_(FileActiveStates), File.pid == None) \
                    .update({
                        'file_state': 'CANCELED', 'reason': 'Job canceled by the user', 'dest_surl_uuid':None,
                        'finish_time': now
                    }, synchronize_session=False)
                # However, for data management operations there is nothing to signal, so
                # set job_finished
                Session.query(DataManagement).filter(DataManagement.job_id == job.job_id)\
                    .filter(DataManagement.file_state.in_(DataManagementActiveStates))\
                    .update({
                        'file_state': 'CANCELED', 'reason': 'Job canceled by the user',
                        'job_finished': now, 'finish_time': now
                    }, synchronize_session=False)
                job = Session.merge(job)

                log.info("Job %s canceled" % job.job_id)
                setattr(job, 'http_status', "200 Ok")
                setattr(job, 'http_message', None)
                responses.append(job)
                Session.expunge(job)
            Session.commit()
            Session.expire_all()
        except:
            Session.rollback()
            raise

        return _multistatus(responses, start_response, expecting_multistatus=len(requested_job_ids) > 1)

    @doc.response(207, 'For multiple job requests if there has been any error')
    @doc.response(403, 'The user doesn\'t have enough privileges')
    @doc.response(404, 'The job doesn\'t exist')
    @jsonify
    def modify(self, job_id_list, start_response):
        """
        Modify a job, or set of jobs
        """
        requested_job_ids = job_id_list.split(',')
        modifiable_jobs = list()
        responses = list()

        # First, check which job ids exist and can be accessed
        for job_id in requested_job_ids:
            # Skip empty
            if not job_id:
                continue
            try:
                job = JobsController._get_job(job_id)
                if job.job_state in JobActiveStates:
                    modifiable_jobs.append(job)
                else:
                    setattr(job, 'http_status', '304 Not Modified')
                    setattr(job, 'http_message', 'The job is in a terminal state')
                    log.warning("The job %s can not be modified, since it is %s" % (job_id, job.job_state))
                    responses.append(job)
            except HTTPClientError, e:
                responses.append(dict(
                    job_id=job_id,
                    http_status="%s %s" % (e.code, e.title),
                    http_message=e.detail
                ))

        # Now, modify those that can be
        modification = get_input_as_dict(request)

        priority = None
        try:
            priority = int(modification['params']['priority'])
        except KeyError:
            pass
        except ValueError:
            raise HTTPBadRequest('Invalid priority value')

        try:
            for job in modifiable_jobs:
                if priority:
                    for file in job.files:
                        file.priority = priority
                        file = Session.merge(file)
                        log.info("File from Job %s priority changed to %d" % (job.job_id, priority))
                    job.priority = priority
                    job = Session.merge(job)
                    log.info("Job %s priority changed to %d" % (job.job_id, priority))
                setattr(job, 'http_status', "200 Ok")
                setattr(job, 'http_message', None)
                responses.append(job)
                Session.expunge(job)
            Session.commit()
            Session.expire_all()
        except:
            Session.rollback()
            raise

        return _multistatus(responses, start_response, expecting_multistatus=len(requested_job_ids) > 1)

    @doc.input('Submission description', 'SubmitSchema')
    @doc.response(400, 'The submission request could not be understood')
    @doc.response(403, 'The user doesn\'t have enough permissions to submit')
    @doc.response(409, 'The request could not be completed due to a conflict with the current state of the resource')
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
        submitted_dict = get_input_as_dict(request)

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
        if user.method != 'oauth2' and credential.remaining() < timedelta(hours=1):
            raise HTTPAuthenticationTimeout(
                'The delegated credentials has less than one hour left (%s)' % user.delegation_id
            )

        # Populate the job and files
        populated = JobBuilder(user, **submitted_dict)

        log.info("%s (%s) is submitting a transfer job" % (user.user_dn, user.vos[0]))

        # Exchange access token for OS token(s) for swift stores
        source_se = populated.job['source_se']
        dest_se = populated.job['dest_se']
        access_token = credential.proxy[:credential.proxy.find(':')]
        if source_se[:5] == 'swift':
            _set_swift_credentials(source_se, user.user_dn, access_token)
        if dest_se[:5] == 'swift' and dest_se != source_se:
            _set_swift_credentials(dest_se, user.user_dn, access_token)

        # Insert the job
        try:
            try:
                Session.execute(Job.__table__.insert(), [populated.job])
            except IntegrityError:
                raise HTTPConflict('The sid provided by the user is duplicated')
            if len(populated.files):
                Session.execute(File.__table__.insert(), populated.files)
            if len(populated.datamanagement):
                Session.execute(DataManagement.__table__.insert(), populated.datamanagement)
            Session.flush()
            Session.commit()
        except IntegrityError as err:
            Session.rollback()
            raise HTTPConflict('The submission is duplicated '+ str(err))
        except:
            Session.rollback()
            raise

        # Send messages
        # Need to re-query so we get the file ids
        job = Session.query(Job).get(populated.job_id)
        for i in range(len(job.files)):
            try:
                submit_state_change(job, job.files[i], populated.files[0]['file_state'])
            except Exception, e:
                log.warning("Failed to write state message to disk: %s" % e.message)

        if len(populated.files):
            log.info("Job %s submitted with %d transfers" % (populated.job_id, len(populated.files)))
        elif len(populated.datamanagement):
            log.info(
                "Job %s submitted with %d data management operations" % (populated.job_id, len(populated.datamanagement))
            )

        return {'job_id': populated.job_id}

    @doc.response(403, 'The user doesn\'t have enough privileges')
    @doc.response(404, 'The job doesn\'t exist')
    @doc.response(409, 'The request could not be completed due to a conflict with the current state of the resource')
    @doc.return_type('Affected transfers, dm and jobs count')
    @jsonify
    def cancel_all_by_vo(self, vo_name):
        """
        Cancel all files by the given vo_name
        """
        user = request.environ['fts3.User.Credentials']

        now = datetime.utcnow()
        if not user.is_root:
            raise HTTPForbidden(
                'User does not have root privileges'
            )

        try:
            # FTS3 daemon expects finish_time to be NULL in order to trigger the signal
            # to fts_url_copy
            file_count = Session.query(File).filter(File.vo_name == vo_name)\
                .filter(File.file_state.in_(FileActiveStates))\
                .update({
                    'file_state': 'CANCELED', 'reason': 'Job canceled by the user', 'dest_surl_uuid':None,
                    'finish_time': None
                }, synchronize_session=False)

            # However, for data management operations there is nothing to signal, so
            # set job_finished
            dm_count = Session.query(DataManagement).filter(DataManagement.vo_name == vo_name)\
                .filter(DataManagement.file_state.in_(DataManagementActiveStates))\
                .update({
                    'file_state': 'CANCELED', 'reason': 'Job canceled by the user',
                    'job_finished': now, 'finish_time': now
                }, synchronize_session=False)

            job_count = Session.query(Job).filter(Job.vo_name == vo_name)\
                .filter(Job.job_state.in_(JobActiveStates))\
                .update({
                    'job_state': 'CANCELED', 'reason': 'Job canceled by the user',
                    'job_finished': now
                }, synchronize_session=False)
            Session.commit()
            Session.expire_all()
            log.info("Active jobs for VO %s canceled" % vo_name)
        except:
            Session.rollback()
            raise
        return {
            "affected_files": file_count,
            "affected_dm": dm_count,
            "affected_jobs": job_count
        }

    @doc.response(403, 'The user doesn\'t have enough privileges')
    @doc.response(404, 'The job doesn\'t exist')
    @doc.return_type('File final states (array if multiple files were given)')
    @jsonify
    def cancel_all(self):
        """
        Cancel all files
        """
        user = request.environ['fts3.User.Credentials']

        now = datetime.utcnow()
        if not user.is_root:
            raise HTTPForbidden(
                'User does not have root privileges'
            )

        try:
            # FTS3 daemon expects finish_time to be NULL in order to trigger the signal
            # to fts_url_copy
            file_count = Session.query(File).filter(File.file_state.in_(FileActiveStates))\
                .update({
                    'file_state': 'CANCELED', 'reason': 'Job canceled by the user',  'dest_surl_uuid':None,
                    'finish_time': None
                }, synchronize_session=False)

            # However, for data management operations there is nothing to signal, so
            # set job_finished
            dm_count = Session.query(DataManagement)\
                .filter(DataManagement.file_state.in_(DataManagementActiveStates))\
                .update({
                    'file_state': 'CANCELED', 'reason': 'Job canceled by the user',
                    'job_finished': now, 'finish_time': now
                }, synchronize_session=False)

            job_count = Session.query(Job).filter(Job.job_state.in_(JobActiveStates))\
                .update({
                    'job_state': 'CANCELED', 'reason': 'Job canceled by the user', 
                    'job_finished': now
                }, synchronize_session=False)
            Session.commit()
            Session.expire_all()
            log.info("Active jobs canceled")
        except:
            Session.rollback()
            raise

        return {
            "affected_files": file_count,
            "affected_dm": dm_count,
            "affected_jobs": job_count
        }

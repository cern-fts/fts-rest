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

import json
import logging
import urllib

from fts3.model import Job, File, JobActiveStates, FileActiveStates
from fts3.model import DataManagement, DataManagementActiveStates
from fts3.model import Credential, OptimizerActive, FileRetryLog
from fts3rest.lib.JobBuilder import JobBuilder
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.http_exceptions import *
from fts3rest.lib.middleware.fts3auth import authorize, authorized
from fts3rest.lib.middleware.fts3auth.constants import *


log = logging.getLogger(__name__)


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
        if filter_dlg_id and filter_dn and filter_dn != user.user_dn:
            raise HTTPBadRequest('The provided DN and delegation id do not correspond to the same user')
        if not filter_dlg_id and filter_state:
            raise HTTPForbidden('To filter by state, you need to provide dlg_id')
        if filter_limit is not None and filter_limit < 0 or filter_limit > 500:
            raise HTTPBadRequest('The limit must be positive and less or equal than 500')

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
            jobs = jobs[:filter_limit]
        else:
            jobs = jobs.yield_per(100)

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
        multistatus = False

        # request is not available inside the generator
        environ = request.environ
        fields = request.GET.get('files', '').split(',')

        statuses = list()
        for job_id in filter(len, job_ids):
            try:
                job = JobsController._get_job(job_id, env=environ)
                if len(fields):
                    def files():
                        for f in Session.query(File).filter(File.job_id == job.job_id).yield_per(100):
                            fd = dict()
                            for field in fields:
                                try:
                                    fd[field] = getattr(f, field)
                                except:
                                    pass
                            yield fd
                    job.__dict__['files'] = files()
                setattr(job, 'http_status', '200 Ok')
                statuses.append(job)
            except HTTPError, e:
                if len(job_ids) == 1:
                    raise
                statuses.append(dict(
                    job_id=job_id,
                    http_status="%s %s" % (e.code, e.title),
                    http_message=e.detail
                ))
                multistatus = True

        if len(job_ids) == 1:
            return statuses[0]

        if multistatus:
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
        return files.yield_per(100)

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

                # FTS3 daemon expects job_finished to be NULL in order to trigger the signal
                # to fts_url_copy
                Session.query(File).filter(File.job_id == job.job_id).filter(File.file_state.in_(FileActiveStates))\
                    .update({
                        'file_state': 'CANCELED', 'reason': 'Job canceled by the user',
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
                response.append(job)
                Session.expunge(job)
            Session.commit()
            Session.expire_all()
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
        populated = JobBuilder(**submitted_dict)
        populated.set_user(user)

        try:
            # Insert the job
            Session.execute(Job.__table__.insert(), [populated.job])
            if len(populated.files):
                Session.execute(File.__table__.insert(), populated.files)
            if len(populated.datamanagement):
                Session.execute(DataManagement.__table__.insert(), populated.datamanagement)

            # Insert into the optimizer
            unique_pairs = set(map(lambda f: (f['source_se'], f['dest_se']), populated.files))
            for (source_se, dest_se) in unique_pairs:
                if not Session.query(OptimizerActive).get((source_se, dest_se)):
                    optimizer_active = OptimizerActive()
                    optimizer_active.source_se = source_se
                    optimizer_active.dest_se = dest_se
                    optimizer_active.ema = 0
                    optimizer_active.datetime = datetime.utcnow()
                    Session.add(optimizer_active)
            Session.commit()
        except:
            Session.rollback()
            raise

        if len(populated.files):
            log.info("Job %s submitted with %d transfers" % (populated.job_id, len(populated.files)))
        elif len(populated.datamanagement):
            log.info(
                "Job %s submitted with %d data management operations" % (populated.job_id, len(populated.datamanagement))
            )

        return {'job_id': populated.job_id}

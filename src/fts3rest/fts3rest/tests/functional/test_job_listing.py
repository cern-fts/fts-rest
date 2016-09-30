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

import json
from datetime import datetime, timedelta

from fts3.model import FileRetryLog, Job, File
from fts3rest.lib.base import Session
from fts3rest.lib.middleware.fts3auth import UserCredentials, constants
from fts3rest.tests import TestController


class TestJobListing(TestController):
    """
    Tests for the job controller, listing, stating, etc.
    """

    def _submit(self, file_metadata=None, dest_surl='root://dest.ch/file'):
        job = {
            'files': [{
                'sources': ['root://source.es/file'],
                'destinations': [dest_surl],
                'selection_strategy': 'orderly',
                'checksum': 'adler32:1234',
                'filesize': 1024,
                'metadata': {'mykey': 'myvalue'},
            }],
            'params': {'overwrite': True, 'verify_checksum': True}
        }
        if file_metadata:
            job['files'][0]['metadata'] = file_metadata

        job_id = self.app.put(
            url="/jobs",
            params=json.dumps(job),
            status=200
        ).json['job_id']

        # Make sure it was commited to the DB
        self.assertGreater(len(job_id), 0)
        return job_id

    def _terminal(self, state, window):
        job_id = self._submit()
        job = Session.query(Job).get(job_id)
        files = Session.query(File).filter(File.job_id == job_id)
        finish_time = datetime.utcnow() - window
        job.finish_time = finish_time
        job.job_finished = finish_time
        job.job_state = state
        Session.merge(job)
        for f in files:
            f.finish_time = finish_time
            f.job_finished = finish_time
            f.file_state = state
            Session.merge(f)
        Session.commit()
        return job_id

    def test_show_job(self):
        """
        Get information about a job
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job_id = self._submit()
        job = self.app.get(url="/jobs/%s" % job_id, status=200).json

        self.assertEqual(job['job_id'], job_id)
        self.assertEqual(job['job_state'], 'SUBMITTED')

    def test_missing_job(self):
        """
        Request an invalid job
        """
        self.setup_gridsite_environment()
        error = self.app.get(
            url="/jobs/1234x",
            status=404
        ).json

        self.assertEquals(error['status'], '404 Not Found')
        self.assertEquals(error['message'], 'No job with the id "1234x" has been found')

    def test_list_job_default(self):
        """
        List active jobs
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job_id = self._submit()

        job_list = self.app.get(url="/jobs", status=200).json
        self.assertTrue(job_id in map(lambda j: j['job_id'], job_list))

    def test_list_with_dlg_id(self):
        """
        List active jobs with the right delegation id
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        creds = self.get_user_credentials()

        job_id = self._submit()

        job_list = self.app.get(
            url="/jobs",
            params={'dlg_id': creds.delegation_id},
            status=200
        ).json
        self.assertTrue(job_id in map(lambda j: j['job_id'], job_list))

    def test_list_with_dn(self):
        """
        List active jobs with the right user DN
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        creds = self.get_user_credentials()

        job_id = self._submit()

        job_list = self.app.get(
            url="/jobs",
            params={'user_dn': creds.user_dn},
            status=200
        ).json
        self.assertTrue(job_id in map(lambda j: j['job_id'], job_list))

    def test_list_with_vo(self):
        """
        List active jobs with the right VO
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        creds = self.get_user_credentials()

        job_id = self._submit()

        job_list = self.app.get(
            url="/jobs",
            params={'vo_name': creds.vos[0]},
            status=200
        ).json
        self.assertTrue(job_id in map(lambda j: j['job_id'], job_list))

    def test_list_bad_dlg_id(self):
        """
        Trying to list jobs belonging to a different delegation id
        must be forbidden
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        creds = self.get_user_credentials()

        self.app.get(url="/jobs",
                     params={'dlg_id': creds.delegation_id + '1234'},
                     status=403)

    def test_list_bad_dn(self):
        """
        Trying to list with the right delegation id mismatched bad DN is a bad
        request
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        creds = self.get_user_credentials()

        self.app.get(url="/jobs",
                     params={'dlg_id': creds.delegation_id, 'user_dn': '/CN=1234'},
                     status=400)

    def test_list_with_state_empty(self):
        """
        Filter by state (no match)
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        creds = self.get_user_credentials()

        job_id = self._submit()

        job_list = self.app.get(
            url="/jobs",
            params={'dlg_id': creds.delegation_id, 'state_in': 'FINISHED,FAILED,CANCELED'},
            status=200
        ).json
        self.assertFalse(job_id in map(lambda j: j['job_id'], job_list))

    def test_list_with_state_match(self):
        """
        Filter by state (match)
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        creds = self.get_user_credentials()

        job_id = self._submit()

        job_list = self.app.get(
            url="/jobs",
            params={'dlg_id': creds.delegation_id, 'state_in': 'ACTIVE,SUBMITTED'},
            status=200
        ).json
        self.assertTrue(job_id in map(lambda j: j['job_id'], job_list))

    def test_list_with_source_se(self):
        """
        Filter by source storage
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job_id = self._submit()

        job_list = self.app.get(
            url="/jobs",
            params={'source_se': 'root://source.es'},
            status=200
        ).json
        self.assertTrue(job_id in map(lambda j: j['job_id'], job_list))

        job_list = self.app.get(
            url="/jobs",
            params={'source_se': 'gsiftp://source.es'},
            status=200
        ).json
        self.assertTrue(job_id not in map(lambda j: j['job_id'], job_list))

    def test_list_with_dest_se(self):
        """
        Filter by destination storage
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job_id = self._submit()

        job_list = self.app.get(
            url="/jobs",
            params={'dest_se': 'root://dest.ch'},
            status=200
        ).json
        self.assertTrue(job_id in map(lambda j: j['job_id'], job_list))

        job_list = self.app.get(
            url="/jobs",
            params={'dest_se': 'gsiftp://dest.ch'},
            status=200
        ).json
        self.assertTrue(job_id not in map(lambda j: j['job_id'], job_list))

    def test_list_no_vo(self):
        """
        Submit a valid job with no VO data in the credentials. Listing it should be possible
        afterwards (regression test for FTS-18)
        """
        self.setup_gridsite_environment(no_vo=True)
        self.push_delegation()

        job_id = self._submit()

        # Must be in the listings!
        job_list = self.app.get(url="/jobs", status=200).json
        self.assertTrue(job_id in map(lambda j: j['job_id'], job_list))

    def test_get_no_vo(self):
        """
        Submit a valid job with no VO data in the credentials. Stating it should be possible
        afterwards (regression test for FTS-18)
        """
        self.setup_gridsite_environment(no_vo=True)
        self.push_delegation()

        job_id = self._submit()

        # Must be in the listings!
        job_info = self.app.get(url="/jobs/%s" % job_id, status=200).json
        self.assertEqual(job_id, job_info['job_id'])
        self.assertEqual(self.get_user_credentials().vos[0], job_info['vo_name'])

    def test_get_field(self):
        """
        Request a field from a job
        """
        self.setup_gridsite_environment(no_vo=True)
        self.push_delegation()

        job_id = self._submit()

        state = self.app.get(url="/jobs/%s/job_state" % job_id, status=200).json
        self.assertEqual(state, 'SUBMITTED')

    def test_get_job_forbidden(self):
        """
        Ask for a job we don't have permission to get
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        job_id = self._submit()

        old_granted = UserCredentials.get_granted_level_for
        UserCredentials.get_granted_level_for = lambda self_, op: None

        error = self.app.get("/jobs/%s" % job_id, status=403).json

        UserCredentials.get_granted_level_for = old_granted

        self.assertEqual(error['status'], '403 Forbidden')

    def test_get_missing_field(self):
        """
        Ask for a field that doesn't exist
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        job_id = self._submit()

        error = self.app.get(url="/jobs/%s/not_really_a_field" % job_id, status=404).json

        self.assertEqual(error['status'], '404 Not Found')
        self.assertEqual(error['message'], 'No such field')

    def test_get_files(self):
        """
        Get the files within a job
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        job_id = self._submit()

        files = self.app.get(url="/jobs/%s/files" % job_id, status=200).json

        self.assertEqual(1, len(files))
        self.assertEqual("root://source.es/file", files[0]['source_surl'])
        self.assertEqual("root://dest.ch/file", files[0]['dest_surl'])
        self.assertEqual(1024, files[0]['user_filesize'])

    def test_no_retries(self):
        """
        Get the retries for a file, without retries
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        job_id = self._submit()

        files = self.app.get(url="/jobs/%s/files" % job_id, status=200).json
        file_id = files[0]['file_id']

        retries = self.app.get(url="/jobs/%s/files/%d/retries" % (job_id, file_id), status=200).json
        self.assertEqual(0, len(retries))

    def test_get_retries(self):
        """
        Get the retries for a file, forcing one
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        job_id = self._submit()

        files = self.app.get(url="/jobs/%s/files" % job_id, status=200).json
        file_id = files[0]['file_id']

        retry = FileRetryLog()
        retry.file_id = file_id
        retry.attempt = 1
        retry.datetime = datetime.utcnow()
        retry.reason = 'Blahblahblah'

        Session.merge(retry)
        Session.commit()

        retries = self.app.get(url="/jobs/%s/files/%d/retries" % (job_id, file_id), status=200).json

        self.assertEqual(1, len(retries))
        self.assertEqual(1, retries[0]['attempt'])
        self.assertEqual('Blahblahblah', retries[0]['reason'])

    def test_get_files_in_job(self):
        """
        Users may want to get information about nested files in one go, so let them ask for
        some of their fields.
        See FTS-137
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        job_id = self._submit()

        job = self.app.get(url="/jobs/%s?files=start_time,source_surl" % job_id, status=200).json

        self.assertIn('files', job)
        self.assertEqual(1, len(job['files']))
        f = job['files'][0]
        self.assertIn('start_time', f)
        self.assertIn('source_surl', f)
        self.assertNotIn('finish_time', f)
        self.assertNotIn('dest_surl', f)

        self.assertEqual('root://source.es/file', f['source_surl'])

    def test_get_multiple_jobs(self):
        """
        Query multiple jobs at once
        See FTS-147
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        N_JOBS = 5
        job_ids = list()
        for i in range(N_JOBS):
            job_ids.append(self._submit())

        job_list = self.app.get(
            url="/jobs/%s?files=start_time,source_surl,file_state" % ','.join(job_ids),
            status=200
        ).json

        self.assertEqual(list, type(job_list))
        self.assertEqual(N_JOBS, len(job_list))

        matches = 0
        for job in job_list:
            if job['job_id'] in job_ids:
                matches += 1
            for f in job['files']:
                self.assertIn('start_time', f)
                self.assertIn('source_surl', f)
                self.assertNotIn('finish_time', f)
                self.assertNotIn('dest_surl', f)
                self.assertIn('file_state', f)
                self.assertEqual('SUBMITTED', f['file_state'])

        self.assertEqual(N_JOBS, matches)

    def test_get_multiple_jobs_one_missing(self):
        """
        Same as test_get_multiple_jobs, but push one missing job
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        N_JOBS = 5
        job_ids = list()
        for i in range(N_JOBS):
            job_ids.append(self._submit())
        job_ids.append('12345-BADBAD-09876')

        job_list = self.app.get(
            url="/jobs/%s?files=start_time,source_surl,file_state" % ','.join(job_ids), status=207
        ).json

        self.assertEqual(list, type(job_list))
        self.assertEqual(N_JOBS + 1, len(job_list))

        for job in job_list:
            if job['job_id'] == '12345-BADBAD-09876':
                self.assertEqual('404 Not Found', job['http_status'])
            else:
                self.assertEqual('200 Ok', job['http_status'])

    def test_filter_by_time(self):
        """
        Filter by time_window
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        creds = self.get_user_credentials()

        job_id = self._terminal('FINISHED', timedelta(minutes=30))

        # Try one hour
        job_list = self.app.get(url="/jobs",
            params={
                'dlg_id': creds.delegation_id,
                'state_in': 'FINISHED',
                'time_window': '1'},
            status=200
        ).json

        self.assertIn(job_id, [j['job_id'] for j in job_list])

        # Try 15 minutes
        job_list = self.app.get(url="/jobs",
            params={
                'dlg_id': creds.delegation_id,
                'state_in': 'FINISHED',
                'time_window': '0:15'
            },
            status=200
        ).json

        self.assertNotIn(job_id, [j['job_id'] for j in job_list])

    def test_get_multiple_with_files(self):
        """
        Query multiple jobs at once, asking for a subset of the fields of their files
        Regression for FTS-265
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job1 = self._submit(file_metadata='a')
        job2 = self._submit(file_metadata='5')
        job3 = self._submit(file_metadata='?')

        jobs = self.app.get(
            url="/jobs/%s?files=job_id,file_metadata" % ','.join([job1, job2, job3]),
            status=200).json

        self.assertEqual(3, len(jobs))
        self.assertEqual(jobs[0]['job_id'], jobs[0]['files'][0]['job_id'])
        self.assertEqual('a',               jobs[0]['files'][0]['file_metadata'])
        self.assertEqual(jobs[1]['job_id'], jobs[1]['files'][0]['job_id'])
        self.assertEqual('5',               jobs[1]['files'][0]['file_metadata'])
        self.assertEqual(jobs[2]['job_id'], jobs[2]['files'][0]['job_id'])
        self.assertEqual('?',               jobs[2]['files'][0]['file_metadata'])

    def test_query_something_running(self):
        """
        Query if there are any active or submitted files for a given destination surl
        Requested by ATLAS to query if a given destination file landed on the DB
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job1 = self._submit(dest_surl='gsiftp://test/path')
        job2 = self._submit(dest_surl='gsiftp://test2/path')

        files = self.app.get(
            url="/files?dest_surl=gsiftp://test2/path",
            status=200
        ).json

        self.assertNotIn(job1, map(lambda f: f['job_id'], files))
        self.assertIn(job2, map(lambda f: f['job_id'], files))

        files = self.app.get(
            url="/files?dest_surl=gsiftp://test/path",
            status=200
        ).json

        self.assertIn(job1, map(lambda f: f['job_id'], files))
        self.assertNotIn(job2, map(lambda f: f['job_id'], files))

    def test_list_granted_private(self):
        """
        Configure access level to PRIVATE, so the user can only see their own transfers
        """
        self.setup_gridsite_environment(dn='/CN=fakeson')
        self.push_delegation()

        self._submit()
        self._submit()

        self.setup_gridsite_environment()
        self.push_delegation()

        job3 = self._submit()

        old_granted = UserCredentials.get_granted_level_for
        UserCredentials.get_granted_level_for = lambda self_, op: constants.PRIVATE

        jobs = self.app.get(url="/jobs", status=200).json

        UserCredentials.get_granted_level_for = old_granted

        self.assertEqual(1, len(jobs))
        self.assertEqual(job3, jobs[0]['job_id'])

    def test_list_granted_vo(self):
        """
        Configure access level to VO, so the user can see their own transfers and others, if they
        belong to the same vo
        """
        self.setup_gridsite_environment(dn='/CN=fakeson', no_vo=True)
        self.push_delegation()

        self._submit()
        self._submit()

        self.setup_gridsite_environment(dn='/CN=jameson')
        self.push_delegation()

        job1 = self._submit()
        job2 = self._submit()

        self.setup_gridsite_environment()
        self.push_delegation()

        job3 = self._submit()

        old_granted = UserCredentials.get_granted_level_for
        UserCredentials.get_granted_level_for = lambda self_, op: constants.VO

        jobs = self.app.get(url="/jobs", status=200).json

        UserCredentials.get_granted_level_for = old_granted

        self.assertEqual(3, len(jobs))
        job_ids = map(lambda j: j['job_id'], jobs)
        self.assertIn(job1, job_ids)
        self.assertIn(job2, job_ids)
        self.assertIn(job3, job_ids)

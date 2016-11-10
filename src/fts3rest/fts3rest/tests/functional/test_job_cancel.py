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

from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import Job, File, JobActiveStates, Credential, FileActiveStates, FileTerminalStates
from datetime import datetime, timedelta


class TestJobCancel(TestController):
    """
    Tests for the job cancellation
    """

    def tearDown(self):
        cert = 'SSL_SERVER_S_DN'
        if cert in self.app.extra_environ:
            del self.app.extra_environ['SSL_SERVER_S_DN']


    def _submit(self, count=1, reuse=False):
        """
        Submit a valid job
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        files = []
        for i in xrange(count):
            files.append({
                'sources': ['root://source.es/file%d' % i],
                'destinations': ['root://dest.ch/file%d' % i],
                'selection_strategy': 'orderly',
                'checksum': 'adler32:1234',
                'filesize': 1024,
                'metadata': {'mykey': 'myvalue'},
            })

        job = {
            'files': files,
            'params': {'overwrite': True, 'verify_checksum': True, 'reuse': reuse}
        }

        job_id = self.app.put(
            url="/jobs",
            params=json.dumps(job),
            status=200
        ).json['job_id']

        return str(job_id)
    
    def _submit_none_reuse(self, count=1, big_files=0):
        """
        Submit a valid job without specifying reuse
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        files = []
        for i in xrange(count):
            files.append({
                'sources': ['root://source.es/file%d' % i],
                'destinations': ['root://dest.ch/file%d' % i],
                'selection_strategy': 'orderly',
                'checksum': 'adler32:1234',
                'filesize': 1024,
                'metadata': {'mykey': 'myvalue'},
            })
        for j in xrange(big_files):
            files.append({
                'sources': ['root://source.es/file%d' % i],
                'destinations': ['root://dest.ch/file%d' % i],
                'selection_strategy': 'orderly',
                'checksum': 'adler32:1234',
                'filesize': 104857600,
                'metadata': {'mykey': 'myvalue'},
            })

        job = {
            'files': files,
            'params': {'overwrite': True, 'verify_checksum': True}
        }

        job_id = self.app.put(
            url="/jobs",
            params=json.dumps(job),
            status=200
        ).json['job_id']

        return str(job_id)

    def test_cancel(self):
        """
        Cancel a job
        """
        job_id = self._submit()
        job = self.app.delete(url="/jobs/%s" % job_id, status=200).json

        self.assertEqual(job['job_id'], job_id)
        self.assertEqual(job['job_state'], 'CANCELED')
        self.assertEqual(job['reason'], 'Job canceled by the user')

        # Is it in the database?
        job = Session.query(Job).get(job_id)
        self.assertEqual(job.job_state, 'CANCELED')
        self.assertEqual(job.reuse_job, 'N')

        self.assertNotEqual(None, job.job_finished)
        self.assertNotEqual(None, job.finish_time)
        for f in job.files:
            self.assertEqual(f.file_state, 'CANCELED')
            self.assertNotEqual(None, f.job_finished)
            self.assertNotEqual(None, f.finish_time)

    def test_cancel_running(self):
        """
        Cancel a job, but the transfer is running (pid is set)
        """
        job_id = self._submit()

        # Add pid
        transfer = Session.query(File).filter(File.job_id == job_id).first()
        transfer.pid = 1234
        Session.merge(transfer)
        Session.commit()

        job = self.app.delete(url="/jobs/%s" % job_id, status=200).json

        self.assertEqual(job['job_id'], job_id)
        self.assertEqual(job['job_state'], 'CANCELED')
        self.assertEqual(job['reason'], 'Job canceled by the user')

        # Is it in the database?
        job = Session.query(Job).get(job_id)
        self.assertEqual(job.job_state, 'CANCELED')
        self.assertNotEqual(None, job.job_finished)
        self.assertNotEqual(None, job.finish_time)
        for f in job.files:
            self.assertEqual(f.file_state, 'CANCELED')
            self.assertEqual(None, f.job_finished)
            self.assertNotEqual(None, f.finish_time)

    def test_cancel_terminal(self):
        """
        Cancel a job with files in terminal state
        """
        job_id = self._submit()

        job = Session.query(Job).get(job_id)
        job.job_state = 'FINISHED'
        for f in job.files:
            f.file_state = 'FINISHED'
        Session.merge(job)
        Session.commit()

        job = self.app.delete(url="/jobs/%s" % job_id, status=200).json

        self.assertEqual(job['job_id'], job_id)
        self.assertEqual(job['job_state'], 'FINISHED')
        self.assertNotEqual(job['reason'], 'Job canceled by the user')

        # Is it in the database?
        job = Session.query(Job).get(job_id)
        self.assertEqual(job.job_state, 'FINISHED')
        for f in job.files:
            self.assertEqual(f.file_state, 'FINISHED')

    def test_cancel_some_terminal(self):
        """
        Cancel a job with some files in terminal state
        """
        job_id = self._submit(10)

        job = Session.query(Job).get(job_id)
        job.job_state = 'ACTIVE'
        for f in job.files:
            if f.file_id % 2 == 0:
                f.file_state = 'FINISHED'
        Session.merge(job)
        Session.commit()

        job = self.app.delete(url="/jobs/%s" % job_id, status=200).json

        self.assertEqual(job['job_id'], job_id)
        self.assertEqual(job['job_state'], 'CANCELED')
        self.assertEqual(job['reason'], 'Job canceled by the user')

        # Is it in the database?
        job = Session.query(Job).get(job_id)
        self.assertEqual(job.job_state, 'CANCELED')
        for f in job.files:
            if f.file_id % 2 == 0:
                self.assertEqual(f.file_state, 'FINISHED')
                self.assertNotEqual(f.reason, 'Job canceled by the user')
            else:
                self.assertEqual(f.file_state, 'CANCELED')

    def test_cancel_multiple(self):
        """
        Cancel multiple jobs at once
        """
        job_ids = list()
        for i in range(10):
            job_ids.append(self._submit())

        jobs = self.app.delete(url="/jobs/%s" % ','.join(job_ids), status=200).json

        self.assertEqual(len(jobs), 10)
        for job in jobs:
            self.assertEqual(job['job_state'], 'CANCELED')
            self.assertEqual(job['reason'], 'Job canceled by the user')

        for job_id in job_ids:
            job = Session.query(Job).get(job_id)
            self.assertEqual(job.job_state, 'CANCELED')
            self.assertEqual(job.reason, 'Job canceled by the user')
            for f in job.files:
                self.assertEqual(f.file_state, 'CANCELED')
                self.assertEqual(f.reason, 'Job canceled by the user')

    def test_cancel_multiple_one(self):
        """
        Use multiple cancellation convention but with only one job
        """
        job_id = self._submit()

        jobs = self.app.delete(url="/jobs/%s," % job_id, status=200).json

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]['job_id'], job_id)
        self.assertEqual(jobs[0]['job_state'], 'CANCELED')
        self.assertEqual(jobs[0]['reason'], 'Job canceled by the user')

        job = Session.query(Job).get(job_id)
        self.assertEqual(job.job_state, 'CANCELED')
        self.assertEqual(job.reason, 'Job canceled by the user')

    def test_cancel_multiple_one_wrong(self):
        """
        Cancel multiple jobs, but one does not exist.
        One status per entry
        """
        job_id = self._submit()
        jobs = self.app.delete(url="/jobs/%s,fake-fake-fake" % job_id, status=207).json

        self.assertEqual(len(jobs), 2)

        for job in jobs:
            if job['job_id'] == job_id:
                self.assertEqual(job['job_state'], 'CANCELED')
                self.assertEqual(job['reason'], 'Job canceled by the user')
                self.assertEqual(job['http_status'], '200 Ok')
            else:
                self.assertEqual(job['http_status'], '404 Not Found')

    def _test_cancel_file_asserts(self, job_id, expect_job, expect_files):
        """
        Helper for test_cancel_remaining_file
        """
        job = Session.query(Job).get(job_id)
        self.assertEqual(job.job_state, expect_job)
        if expect_job in JobActiveStates:
            self.assertIsNone(job.job_finished)
        else:
            self.assertIsNotNone(job.job_finished)
        self.assertEqual('CANCELED', job.files[0].file_state)
        self.assertIsNotNone(job.files[0].finish_time)
        self.assertIsNone(job.files[0].job_finished)
        for f in job.files[1:]:
            self.assertEqual(expect_files, f.file_state)
            if expect_job in JobActiveStates:
                self.assertIsNone(f.job_finished)
            else:
                self.assertIsNotNone(f.job_finished)

    def test_cancel_file(self):
        """
        Cancel just one file of a job with multiple files.
        The job and other files must remain unaffected.
        """
        job_id = self._submit(5)
        files = self.app.get(url="/jobs/%s/files" % job_id, status=200).json

        self.app.delete(url="/jobs/%s/files/%s" % (job_id, files[0]['file_id']))
        self._test_cancel_file_asserts(job_id, 'SUBMITTED', 'SUBMITTED')

    def test_cancel_only_file(self):
        """
        Cancel the only file in a job.
        The job must go to CANCELED.
        """
        job_id = self._submit(1)
        files = self.app.get(url="/jobs/%s/files" % job_id, status=200).json

        self.app.delete(url="/jobs/%s/files/%s" % (job_id, files[0]['file_id']))

        job = Session.query(Job).get(job_id)
        self.assertEqual(job.job_state, 'CANCELED')
        self.assertEqual('CANCELED', job.files[0].file_state)

    def _submit_and_mark_all_but_one(self, count, states):
        """
        Helper for test_cancel_remaining_file
        Submit a job, mark all files except the first one with the state 'state'
        state can be a list with count-1 final states
        """
        job_id = self._submit(count)
        files = self.app.get(url="/jobs/%s/files" % job_id, status=200).json

        if isinstance(states, str):
            states = [states] * (count - 1)

        for i in range(1, count):
            fil = Session.query(File).get(files[i]['file_id'])
            fil.file_state = states[i - 1]
            Session.merge(fil)
        Session.commit()

        return job_id, files

    def test_cancel_remaining_file(self):
        """
        Cancel the remaining file of a job.
        Depending on the other file states, the job must go to FAILED, CANCELED or FINISHEDDIRTY
        """
        # Try first all remaining FAILED
        # Final state must be FAILED
        job_id, files = self._submit_and_mark_all_but_one(5, 'FAILED')

        self.app.delete(url="/jobs/%s/files/%s" % (job_id, files[0]['file_id']))
        self._test_cancel_file_asserts(job_id, 'CANCELED', 'FAILED')

        # All remaining FINISHED
        # Final state must be FINISHED
        job_id, files = self._submit_and_mark_all_but_one(5, 'FINISHED')

        self.app.delete(url="/jobs/%s/files/%s" % (job_id, files[0]['file_id']))
        self._test_cancel_file_asserts(job_id, 'CANCELED', 'FINISHED')

        # All remaining CANCELED
        # Final state must be CANCELED
        job_id, files = self._submit_and_mark_all_but_one(5, 'CANCELED')

        self.app.delete(url="/jobs/%s/files/%s" % (job_id, files[0]['file_id']))
        self._test_cancel_file_asserts(job_id, 'CANCELED', 'CANCELED')

    def test_cancel_multiple_files(self):
        """
        Cancel multiple files within a job.
        """
        job_id = self._submit(10)
        files = self.app.get(url="/jobs/%s/files" % job_id, status=200).json

        file_ids = ','.join(map(lambda f: str(f['file_id']), files[0:2]))
        answer = self.app.delete(url="/jobs/%s/files/%s" % (job_id, file_ids), status=200)
        changed_states = answer.json

        self.assertEqual(changed_states, ['CANCELED', 'CANCELED'])

        job = Session.query(Job).get(job_id)
        self.assertEqual(job.job_state, 'SUBMITTED')
        for file in job.files[2:]:
            self.assertEqual(file.file_state, 'SUBMITTED')

    def test_cancel_reuse(self):
        """
        Jobs with reuse or multihop can not be cancelled file per file
        """
        job_id = self._submit(10, reuse=True)
        files = self.app.get(url="/jobs/%s/files" % job_id, status=200).json

        file_ids = ','.join(map(lambda f: str(f['file_id']), files[0:2]))
        self.app.delete(url="/jobs/%s/files/%s" % (job_id, file_ids), status=400)
        
    def test_cancel_reuse_small_files(self):
        """
        Jobs with small files can not be cancelled file per file
        """
        job_id = self._submit_none_reuse(10)
        files = self.app.get(url="/jobs/%s/files" % job_id, status=200).json

        file_ids = ','.join(map(lambda f: str(f['file_id']), files[0:2]))
        self.app.delete(url="/jobs/%s/files/%s" % (job_id, file_ids), status=400)
    
    def test_cancel_reuse_big_files(self):
        """
        Jobs with small files and one big file can not be cancelled file per file
        """
        job_id = self._submit_none_reuse(10, 1)
        files = self.app.get(url="/jobs/%s/files" % job_id, status=200).json

        file_ids = ','.join(map(lambda f: str(f['file_id']), files[0:2]))
        self.app.delete(url="/jobs/%s/files/%s" % (job_id, file_ids), status=400)
    
    def test_cancel_reuse_small_files_and_big_files(self):
        """
        Cancel a job with small files and two big files cannot be reused
        """
        job_id = self._submit_none_reuse(100, 2)
        job = self.app.delete(url="/jobs/%s" % job_id, status=200).json

        self.assertEqual(job['job_id'], job_id)
        self.assertEqual(job['job_state'], 'CANCELED')
        self.assertEqual(job['reason'], 'Job canceled by the user')

        # Is it in the database?
        job = Session.query(Job).get(job_id)
        self.assertEqual(job.job_state, 'CANCELED')
        self.assertEqual(job.reuse_job, 'N')

        self.assertNotEqual(None, job.job_finished)
        self.assertNotEqual(None, job.finish_time)
        for f in job.files:
            self.assertEqual(f.file_state, 'CANCELED')
            self.assertNotEqual(None, f.job_finished)
            self.assertNotEqual(None, f.finish_time)

    def _become_root(self):
        """
        Helper function to become root superuser
        """
        self.app.extra_environ.update({'GRST_CRED_AURI_0': 'dn:/C=CH/O=CERN/OU=hosts/OU=cern.ch/CN=ftsdummyhost.cern.ch'})
        self.app.extra_environ.update({'SSL_SERVER_S_DN': '/C=CH/O=CERN/OU=hosts/OU=cern.ch/CN=ftsdummyhost.cern.ch'})

        creds = self.get_user_credentials()
        delegated = Credential()
        delegated.dlg_id     = creds.delegation_id
        delegated.dn         = '/C=CH/O=CERN/OU=hosts/OU=cern.ch/CN=ftsdummyhost.cern.ch'
        delegated.proxy      = '-NOT USED-'
        delegated.voms_attrs = None
        delegated.termination_time = datetime.utcnow() + timedelta(hours=7)

        Session.merge(delegated)
        Session.commit()

    def _prepare_and_test_created_jobs_to_cancel(self, files_per_job=8):
        """
        Helper function to prepare and test created jobs for cancel tests
        """
        job_ids = list()
        for i in range(len(FileActiveStates) + len(FileTerminalStates)):
            job_ids.append(self._submit(files_per_job))
        i = 0
        for state in FileActiveStates + FileTerminalStates:
            job = Session.query(Job).get(job_ids[i])
            i += 1
            if state == 'STARTED':
                job.job_state = 'STAGING'
            else:
                job.job_state = state
            for f in job.files:
                f.file_state = state
            Session.merge(job)
            Session.commit()

        i = 0
        for state in FileActiveStates + FileTerminalStates:
            job = Session.query(Job).get(job_ids[i])
            state_job = state
            if state == 'STARTED':
                state_job = 'STAGING'
            self.assertEqual(job.job_state, state_job)
            for f in job.files:
                self.assertEqual(f.file_state, state)
            i += 1
        return job_ids

    def _test_canceled_jobs(self, job_ids):
        """
        Helper function to test canceled jobs
        """
        i = 0
        for _ in FileActiveStates:
            job = Session.query(Job).get(job_ids[i])
            self.assertEqual(job.job_state, 'CANCELED')
            for f in job.files:
                self.assertEqual(f.file_state, 'CANCELED')
            i += 1
        for state in FileTerminalStates:
            job = Session.query(Job).get(job_ids[i])
            self.assertEqual(job.job_state, state)
            for f in job.files:
                self.assertEqual(f.file_state, state)
            i += 1


    def test_cancel_all_by_vo(self):
        """
        Cancel all files by vo name.
        """
        self.setup_gridsite_environment()
        creds = self.get_user_credentials()
        if creds.vos:
            vo_name = creds.vos[0]
        else:
            vo_name = "testvo"

        job_ids = self._prepare_and_test_created_jobs_to_cancel(files_per_job=8)
        self.app.delete(url="/jobs/vo/%s" % vo_name, status=403)
        self._become_root()
        response = self.app.delete(url="/jobs/vo/%s" % vo_name, status=200).json
        self._test_canceled_jobs(job_ids)
        self.assertEqual(response['affected_files'], len(FileActiveStates) * 8)
        self.assertEqual(response['affected_dm'], 0)
        self.assertEqual(response['affected_jobs'], len(FileActiveStates))

    def test_cancel_all(self):
        """
        Cancel all files.
        """
        job_ids = self._prepare_and_test_created_jobs_to_cancel(files_per_job=8)
        self.app.delete(url="/jobs/all", status=403) 
        self._become_root()
        response = self.app.delete(url="/jobs/all", status=200).json
        self._test_canceled_jobs(job_ids)
        self.assertEqual(response['affected_files'], len(FileActiveStates) * 8)
        self.assertEqual(response['affected_dm'], 0)
        self.assertEqual(response['affected_jobs'], len(FileActiveStates))

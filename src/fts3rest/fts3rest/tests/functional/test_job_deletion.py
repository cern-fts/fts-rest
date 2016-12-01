#   Copyright notice:
#   Copyright CERN, 2014.
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
from fts3.model import Job, DataManagement


class TestJobDeletion(TestController):
    """
    Test DELETE jobs
    """

    def test_simple_delete(self):
        """
        Simple deletion job
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'delete': [
                'root://source.es/file',
                {'surl': 'root://source.es/file2', 'metadata': {'a': 'b'}}
            ]
        }

        job_id = self.app.put(
            url="/jobs",
            params=json.dumps(job),
            status=200
        ).json['job_id']

        self.assertIsNotNone(job_id)

        job = Session.query(Job).get(job_id)

        self.assertEqual(job.vo_name, 'testvo')
        self.assertEqual(job.user_dn, self.TEST_USER_DN)
        self.assertEqual(job.source_se, 'root://source.es')
        self.assertEqual('DELETE', job.job_state)
        self.assertIsNotNone(job.cred_id)

        dm = Session.query(DataManagement).filter(DataManagement.job_id == job_id).all()
        self.assertEqual(2, len(dm))

        self.assertEqual(dm[0].source_surl, 'root://source.es/file')
        self.assertEqual(dm[1].source_surl, 'root://source.es/file2')

        self.assertEqual(dm[1].file_metadata['a'], 'b')

        self.assertEqual(dm[0].hashed_id, dm[1].hashed_id)

        for d in dm:
            self.assertEqual(d.vo_name, 'testvo')
            self.assertEqual(d.file_state, 'DELETE')
            self.assertEqual(d.source_se, 'root://source.es')

        return str(job_id)

    def test_get_delete_job(self):
        """
        Submit a deletion job, get info via REST
        """
        job_id = self.test_simple_delete()

        job = self.app.get_json(url="/jobs/%s" % job_id, status=200).json
        files = self.app.get_json(url="/jobs/%s/dm" % job_id, status=200).json

        self.assertEqual(job['job_state'], 'DELETE')
        self.assertEqual(files[0]['source_surl'], 'root://source.es/file')
        self.assertEqual(files[1]['source_surl'], 'root://source.es/file2')

    def test_cancel_delete(self):
        """
        Submit deletion job, then cancel
        """
        job_id = self.test_simple_delete()

        self.app.delete(url="/jobs/%s" % job_id,
                        status=200)

        job = Session.query(Job).get(job_id)

        self.assertEqual('CANCELED', job.job_state)
        self.assertEqual(job.reason, 'Job canceled by the user')
        self.assertIsNotNone(job.job_finished)

        dm = Session.query(DataManagement).filter(DataManagement.job_id == job_id).all()
        for d in dm:
            self.assertEqual('CANCELED', d.file_state)
            self.assertIsNotNone(d.finish_time)
            self.assertIsNotNone(d.job_finished)

    def test_delete_repeated(self):
        """
        Submit a deletion job with files repeated multiple times,
        they must land only once in the db
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'delete': [
                'root://source.es/file',
                {'surl': 'root://source.es/file2', 'metadata': {'a': 'b'}},
                'root://source.es/file',
                'root://source.es/file2',
                'root://source.es/file3'
            ]
        }

        job_id = self.app.put(
            url="/jobs",
            params=json.dumps(job),
            status=200
        ).json['job_id']

        self.assertIsNotNone(job_id)

        dm = Session.query(DataManagement).filter(DataManagement.job_id == job_id).all()

        self.assertEqual(3, len(dm))
        registered = set()
        for f in dm:
            registered.add(f.source_surl)
        self.assertEqual(
            set(('root://source.es/file', 'root://source.es/file2', 'root://source.es/file3')),
            registered
        )

    def test_delete_file(self):
        """
        Submit a deletion job with a file:///
        Must be denied
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'delete': [
                'root://source.es/file',
                {'surl': 'root://source.es/file2', 'metadata': {'a': 'b'}},
                'root://source.es/file',
                'root://source.es/file2',
                'file:///etc/passwd'
            ]
        }

        self.app.put(url="/jobs",
                     params=json.dumps(job),
                     status=400)

#   Copyright notice:
#   Copyright © Members of the EMI Collaboration, 2010.
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
from fts3.model import Job


class TestSubmitToStaging(TestController):
    """
    Tests for the job controller
    Focus in staging transfers
    """

    def test_submit_to_staging(self):
        """
        Submit a job into staging
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['root://source.es/file'],
                'destinations': ['root://dest.ch/file'],
                'selection_strategy': 'orderly',
                'checksum': 'adler32:1234',
                'filesize': 1024,
                'metadata': {'mykey': 'myvalue'},
            }],
            'params': {
                'overwrite': True,
                'copy_pin_lifetime': 3600,
                'bring_online': 60,
                'verify_checksum': True
            }
        }

        answer = self.app.post(url="/jobs",
                               content_type='application/json',
                               params=json.dumps(job),
                               status=200)

        # Make sure it was committed to the DB
        job_id = json.loads(answer.body)['job_id']
        self.assertGreater(len(job_id), 0)

        db_job = Session.query(Job).get(job_id)
        self.assertEqual(db_job.job_state, 'STAGING')
        self.assertEqual(db_job.files[0].file_state, 'STAGING')

        return job_id

    def test_submit_to_staging_no_lifetime(self):
        """
        Submit a job into staging, with pin lifetime not set
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['root://source.es/file'],
                'destinations': ['root://dest.ch/file'],
                'selection_strategy': 'orderly',
                'checksum': 'adler32:1234',
                'filesize': 1024,
                'metadata': {'mykey': 'myvalue'},
            }],
            'params': {
                'overwrite': True,
                'bring_online': 60,
                'verify_checksum': True
            }
        }

        answer = self.app.post(url="/jobs",
                               content_type='application/json',
                               params=json.dumps(job),
                               status=200)

        # Make sure it was committed to the DB
        job_id = json.loads(answer.body)['job_id']
        self.assertGreater(len(job_id), 0)

        db_job = Session.query(Job).get(job_id)
        self.assertEqual(db_job.job_state, 'STAGING')
        self.assertEqual(db_job.files[0].file_state, 'STAGING')

        return job_id

    def test_submit_to_staging_no_bring_online(self):
        """
        Submit a job into staging, with bring_online not set
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['root://source.es/file'],
                'destinations': ['root://dest.ch/file'],
                'selection_strategy': 'orderly',
                'checksum': 'adler32:1234',
                'filesize': 1024,
                'metadata': {'mykey': 'myvalue'},
            }],
            'params': {
                'overwrite': True,
                'copy_pin_lifetime': 60,
                'verify_checksum': True
            }
        }

        answer = self.app.post(url="/jobs",
                               content_type='application/json',
                               params=json.dumps(job),
                               status=200)

        # Make sure it was committed to the DB
        job_id = json.loads(answer.body)['job_id']
        self.assertGreater(len(job_id), 0)

        db_job = Session.query(Job).get(job_id)
        self.assertEqual(db_job.job_state, 'STAGING')
        self.assertEqual(db_job.files[0].file_state, 'STAGING')

        return job_id

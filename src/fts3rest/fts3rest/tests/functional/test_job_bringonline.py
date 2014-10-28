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
from fts3.model import Job


class TestJobBringOnline(TestController):
    """
    Test submission of bring online jobs
    """

    def test_simple_bringonline(self):
        """
        Test a regular, one file, bring online job
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['srm://source.es/?SFN=/path/'],
                'destinations': ['srm://dest.ch/file'],
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

    def test_multiple_bringonline(self):
        """
        Test a bring online job, with multiple files
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [
                {
                    'sources': ['srm://source.es/?SFN=/path/'],
                    'destinations': ['srm://dest.ch/file'],
                },
                {
                    'sources': ['srm://source.es/?SFN=/path/file2'],
                    'destinations': ['srm://dest.ch/file2'],
                },
                {
                    'sources': ['srm://source.es/?SFN=/path/file3'],
                    'destinations': ['srm://dest.ch/file3'],
                },
            ],
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

        self.assertEqual(len(db_job.files), 3)

        # "Hashed" id must be equal so bulk bring online calls can be made
        # See https://its.cern.ch/jira/browse/FTS-145
        hid = db_job.files[0].hashed_id
        for f in db_job.files:
            self.assertEqual(f.file_state, 'STAGING')
            self.assertEqual(f.hashed_id, hid)

    def test_staging_no_srm(self):
        """
        Anything that is not SRM should not be allowed to be submitted to STAGING
        Regression for FTS-153
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['root://source.es/file'],
                'destinations': ['root://dest.ch/file'],
                'filesize': 1024,
            }],
            'params': {
                'copy_pin_lifetime': 3600
            }
        }

        answer=  self.app.put(url="/jobs",
                              params=json.dumps(job),
                              status=400)

        error = json.loads(answer.body)
        # SRM has to be mentioned in the error message
        self.assertIn('SRM', error['message'])

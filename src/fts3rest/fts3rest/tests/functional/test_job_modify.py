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
import mock
import socket
from nose.plugins.skip import SkipTest
from sqlalchemy.orm import scoped_session, sessionmaker

from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import File, Job

class TestJobModify(TestController):
    """
    Tests job modification
    """

    def test_job_priority(self):
        """
        Submit a job, change priority later
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {'files': [{
                'sources': ['root://source.es/file'],
                'destinations': ['root://dest.ch/file'],
            }],
            'params': {
                'priority': 2
            }
        }

        job_id = self.app.post_json(
            url="/jobs",
            params=job,
            status=200
        ).json['job_id']

        job = Session.query(Job).get(job_id)
        self.assertEqual(2, job.priority)

        mod = {'params': {
            'priority': 4
        }}

        self.app.post_json(
            url="/jobs/%s" % str(job_id),
            params=mod,
            status=200
        )

        job = Session.query(Job).get(job_id)
        self.assertEqual(4, job.priority)

    def test_job_priority_invalid(self):
        """
        Submit a job, try to change priority to an invalid value later
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {'files': [{
                'sources': ['root://source.es/file'],
                'destinations': ['root://dest.ch/file'],
            }],
            'params': {
                'priority': 2
            }
        }

        job_id = self.app.post_json(
            url="/jobs",
            params=job,
            status=200
        ).json['job_id']

        job = Session.query(Job).get(job_id)
        self.assertEqual(2, job.priority)

        mod = {'params': {
            'priority': 'axxx'
        }}

        self.app.post_json(
            url="/jobs/%s" % str(job_id),
            params=mod,
            status=400
        )

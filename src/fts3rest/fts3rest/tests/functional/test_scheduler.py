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
import datetime
import logging
import time

from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import Job, File, OptimizerEvolution, ActivityShare

log = logging.getLogger(__name__)


class TestScheduler(TestController):

    def tearDown(self):
        Session.query(Job).delete()
        Session.query(File).delete()
        Session.query(OptimizerEvolution).delete()
        Session.query(ActivityShare).delete()
        Session.commit()

    @staticmethod
    def fill_file_queue(self):

        for i in range(0, 15):
            self.app.post(
                url="/jobs",
                content_type='application/json',
                params=json.dumps({
                    'files': [{
                        'sources': ['http://site01.es/file%d' % i],
                        'destinations': ['http://dest.ch/file%d' % i],
                        'selection_strategy': 'orderly',
                        'filesize':4096,
                        'success':90
                    }]
                }),
                status=200
            )

        for i in range(0, 10):
            self.app.post(
                url="/jobs",
                content_type='application/json',
                params=json.dumps({
                    'files': [{
                        'sources': ['http://site02.ch/file%d' % i],
                        'destinations': ['http://dest.ch/file%d' % i],
                        'selection_strategy': 'orderly',
                        'filesize':2048,
                        'success':95
                    }]
                }),
                status=200
            )

        for i in range(0, 5):
            self.app.post(
                url="/jobs",
                content_type='application/json',
                params=json.dumps({
                    'files': [{
                        'sources': ['http://site03.fr/file%d' % i],
                        'destinations': ['http://dest.ch/file%d' % i],
                        'selection_strategy': 'orderly',
                        'filesize':1024,
                        'success':100
                    }]
                }),
                status=200
            )

    @staticmethod
    def fill_optimizer():

        for i in range(10):
            evolution = OptimizerEvolution(
                datetime=datetime.datetime.utcnow(),
                source_se='http://site01.es',
                dest_se='http://dest.ch',
                success=90,
                active=10,
                throughput=10
            )
            Session.add(evolution)

        for i in range(10):
            evolution = OptimizerEvolution(
                datetime=datetime.datetime.utcnow(),
                source_se='http://site02.ch',
                dest_se='http://dest.ch',
                success=95,
                active=10,
                throughput=15
            )
            Session.add(evolution)

        for i in range(10):
            evolution = OptimizerEvolution(
                datetime=datetime.datetime.utcnow(),
                source_se='http://site03.fr',
                dest_se='http://dest.ch',
                success=100,
                active=10,
                throughput=20
            )
            Session.add(evolution)
        Session.commit()

    @staticmethod
    def fill_activities():

        activity = ActivityShare(
          vo='testvo',
          activity_share=json.dumps({
              "data brokering": 0.3,
              "data consolidation": 0.4,
              "default": 0.02,
              "express": 0.4,
              "functional test": 0.2,
              "production": 0.5,
              "production input": 0.25,
              "production output": 0.25,
              "recovery": 0.4,
              "staging": 0.5,
              "t0 export": 0.7,
              "t0 tape": 0.7,
              "user subscriptions": 0.1
          })
        )
        Session.add(activity)
        Session.commit()

    @staticmethod
    def submit_job(self, strategy):
        # Submit job
        job = {
            'files': [
                {
                    'sources': [
                        'http://site01.es/file',
                        'http://site02.ch/file',
                        'http://site03.fr/file'
                        ],
                    'destinations': ['http://dest.ch/file'],
                    'selection_strategy': strategy,
                    'checksum': 'adler32:1234',
                    'filesize': 1024,
                    'metadata': {'mykey': 'myvalue'}
                }
            ],
            'params': {'overwrite': True}
        }
        job_id = self.app.post(
            url="/jobs",
            content_type='application/json',
            params=json.dumps(job),
            status=200
        ).json['job_id']
        return job_id

    @staticmethod
    def validate(job_id, self):
        # site03.fr should be the activated transfer
        db_job = Session.query(Job).get(job_id)

        self.assertEqual(db_job.reuse_job, 'R')

        self.assertEqual(len(db_job.files), 3)

        self.assertEqual(db_job.files[0].file_index, 0)
        self.assertEqual(db_job.files[0].source_surl, 'http://site01.es/file')
        self.assertEqual(db_job.files[0].dest_surl, 'http://dest.ch/file')
        self.assertEqual(db_job.files[0].file_state, 'NOT_USED')

        self.assertEqual(db_job.files[1].file_index, 0)
        self.assertEqual(db_job.files[1].source_surl, 'http://site02.ch/file')
        self.assertEqual(db_job.files[1].dest_surl, 'http://dest.ch/file')
        self.assertEqual(db_job.files[1].file_state, 'NOT_USED')

        self.assertEqual(db_job.files[2].file_index, 0)
        self.assertEqual(db_job.files[2].source_surl, 'http://site03.fr/file')
        self.assertEqual(db_job.files[2].dest_surl, 'http://dest.ch/file')
        self.assertEqual(db_job.files[2].file_state, 'SUBMITTED')

        # Same file index, same hashed id
        uniq_hashes = set(map(lambda f: f.hashed_id, db_job.files))
        self.assertEqual(len(uniq_hashes), 1)

    def test_queue(self):
        self.setup_gridsite_environment()
        self.push_delegation()
        TestScheduler.fill_file_queue(self)
        job_id = TestScheduler.submit_job(self, "queue")
        TestScheduler.validate(job_id, self)
 
        self.setup_gridsite_environment()
        self.push_delegation()
        job_id = TestScheduler.submit_job(self, "queue")
        TestScheduler.validate(job_id, self)
 
        time.sleep(6)

        self.setup_gridsite_environment()
        self.push_delegation()
        job_id = TestScheduler.submit_job(self, "queue")
        TestScheduler.validate(job_id, self)


    def test_success(self):
        self.setup_gridsite_environment()
        self.push_delegation()
        TestScheduler.fill_optimizer()
        job_id = TestScheduler.submit_job(self, "success")
        TestScheduler.validate(job_id, self)

    def test_throughput(self):
        self.setup_gridsite_environment()
        self.push_delegation()
        TestScheduler.fill_optimizer()
        job_id = TestScheduler.submit_job(self, "throughput")
        TestScheduler.validate(job_id, self)

    def test_file_throughput(self):
        self.setup_gridsite_environment()
        self.push_delegation()
        TestScheduler.fill_optimizer()
        job_id = TestScheduler.submit_job(self, "file-throughput")
        TestScheduler.validate(job_id, self)

    def test_pending_data(self):
        self.setup_gridsite_environment()
        self.push_delegation()
        TestScheduler.fill_activities()
        TestScheduler.fill_file_queue(self)
        job_id = TestScheduler.submit_job(self, "pending-data")
        TestScheduler.validate(job_id, self)

    def test_waiting_time(self):
        self.setup_gridsite_environment()
        self.push_delegation()
        TestScheduler.fill_activities()
        TestScheduler.fill_optimizer()
        TestScheduler.fill_file_queue(self)
        job_id = TestScheduler.submit_job(self, "waiting-time")
        TestScheduler.validate(job_id, self)

    def test_waiting_time_with_error(self):
        self.setup_gridsite_environment()
        self.push_delegation()
        TestScheduler.fill_activities()
        TestScheduler.fill_optimizer()
        TestScheduler.fill_file_queue(self)
        job_id = TestScheduler.submit_job(self, "waiting-time-with-error")
        TestScheduler.validate(job_id, self)

    def test_duration(self):
        self.setup_gridsite_environment()
        self.push_delegation()
        TestScheduler.fill_activities()
        TestScheduler.fill_optimizer()
        TestScheduler.fill_file_queue(self)
        job_id = TestScheduler.submit_job(self, "duration")
        TestScheduler.validate(job_id, self)

    def test_auto(self):
        self.test_queue()

    def test_invalid_strategy(self):
        self.setup_gridsite_environment()
        self.push_delegation()
        TestScheduler.fill_file_queue(self)
        job_id = TestScheduler.submit_job(self, "YOLO")
        TestScheduler.validate(job_id, self)

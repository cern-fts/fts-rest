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

from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3rest.lib.scheduler.Cache import ThreadLocalCache
from fts3.model import Job, File, OptimizerEvolution, ActivityShare
import random

log = logging.getLogger(__name__)


class TestScheduler(TestController):
    """
    Test different selection strategies at submission time
    """

    def setUp(self):
        Session.query(OptimizerEvolution).delete()
        Session.commit()

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
                        'destinations': ['http://dest.ch/file%d%d' % (i, random.randint(0, 100))],
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
                        'destinations': ['http://dest.ch/file%d%d' % (i, random.randint(0, 100))],
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
                        'destinations': ['http://dest.ch/file%d%d' % (i, random.randint(0, 100))],
                        'selection_strategy': 'orderly',
                        'filesize':1024,
                        'success':100
                    }]
                }),
                status=200
            )

    @staticmethod
    def fill_optimizer():
        evolution = OptimizerEvolution(
            datetime=datetime.datetime.utcnow(),
            source_se='http://site01.es',
            dest_se='http://dest.ch'+str(random.randint(0, 100)),
            success=90,
            active=10,
            throughput=10
        )
        Session.add(evolution)

        evolution = OptimizerEvolution(
            datetime=datetime.datetime.utcnow(),
            source_se='http://site02.ch',
            dest_se='http://dest.ch'+str(random.randint(0, 100)),
            success=95,
            active=10,
            throughput=15
        )
        Session.add(evolution)

        evolution = OptimizerEvolution(
            datetime=datetime.datetime.utcnow(),
            source_se='http://site03.fr',
            dest_se='http://dest.ch'+str(random.randint(0, 100)),
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

    def submit_job(self, strategy):
        job = {
            'files': [
                {
                    'sources': [
                        'http://site01.es/file',
                        'http://site02.ch/file',
                        'http://site03.fr/file'
                        ],

                    'destinations': ['http://dest.ch/file'+str(random.randint(0, 100)]),
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

    def validate(self, job_id, expected_submitted='http://site03.fr/file'):
        db_job = Session.query(Job).get(job_id)

        self.assertEqual(db_job.job_type, 'R')
        self.assertEqual(len(db_job.files), 3)

        for f in db_job.files:
            self.assertEqual(f.file_index, 0)
            
            if f.source_surl == expected_submitted:
                self.assertEqual(f.file_state, 'SUBMITTED')
            else:
                self.assertEqual(f.file_state, 'NOT_USED')
            self.assertEqual(db_job.files[0].source_surl, 'http://site01.es/file')

        # Same file index, same hashed id
        uniq_hashes = set(map(lambda f: f.hashed_id, db_job.files))
        self.assertEqual(len(uniq_hashes), 1)

    def test_queue(self):
        """
        Test the 'queue' algorithm
        This algorithm must choose the pair with lest pending transfers
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        TestScheduler.fill_file_queue(self)

        job_id = self.submit_job("queue")
        self.validate(job_id)

        job_id = self.submit_job("queue")
        self.validate(job_id)

        # Trigger a cache expiration
        ThreadLocalCache.cache_cleanup()

        job_id = self.submit_job("queue")
        self.validate(job_id)

    def test_success(self):
        """
        Test the 'success' algorithm
        This algorithm must choose the pair with highest success rate
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        TestScheduler.fill_optimizer()
        job_id = self.submit_job("success")
        self.validate(job_id)

    def test_throughput(self):
        """
        Test the 'throughput' algorithm
        This algorithm must choose the pair with highest total throughput
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        TestScheduler.fill_optimizer()
        job_id = self.submit_job("throughput")
        self.validate(job_id)

    def test_file_throughput(self):
        """
        Test the 'file-throughput algorithm
        This algorithm must choose the pair with highest throughput _per file_
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        TestScheduler.fill_optimizer()
        job_id = self.submit_job("file-throughput")
        self.validate(job_id)

    def test_pending_data(self):
        """
        Test the 'pending-data' algorihtm
        This algorithm must choose the pair with less data to be transferred
        (sum of the file sizes of the queued transfers)
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        TestScheduler.fill_activities()
        TestScheduler.fill_file_queue(self)
        job_id = self.submit_job("pending-data")
        self.validate(job_id)

    def test_waiting_time(self):
        """
        Test the 'waiting-time' algorithm
        This algorithm must choose the pair with less estimated waiting time
        (pending data / total throughput)
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        TestScheduler.fill_activities()
        TestScheduler.fill_optimizer()
        TestScheduler.fill_file_queue(self)
        job_id = self.submit_job("waiting-time")
        self.validate(job_id)

    def test_waiting_time_with_error(self):
        """
        Test the 'waiting-time-with-error' algorihtm
        This algorithm must choose the pair with less estimated waiting time,
        penalized by its failure rate
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        TestScheduler.fill_activities()
        TestScheduler.fill_optimizer()
        TestScheduler.fill_file_queue(self)
        job_id = self.submit_job("waiting-time-with-error")
        self.validate(job_id)

    def test_duration(self):
        """
        Test the 'duration' algorithm
        Similar to the 'waiting-time-with-error', but accounting for the file size
        of the submitted transfer
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        TestScheduler.fill_activities()
        TestScheduler.fill_optimizer()
        TestScheduler.fill_file_queue(self)
        job_id = self.submit_job("duration")
        self.validate(job_id)

    def test_invalid_strategy(self):
        """
        Test a random strategy name, which must fail
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        job = {
            'files': [
                {
                    'sources': [
                        'http://site01.es/file',
                        'http://site02.ch/file',
                        'http://site03.fr/file'
                        ],
                    'destinations': ['http://dest.ch/file'+str(random.randint(0, 100)],
                    'selection_strategy': "YOLO",
                    'checksum': 'adler32:1234',
                    'filesize': 1024,
                    'metadata': {'mykey': 'myvalue'}
                }
            ],
            'params': {'overwrite': True}
        }
        self.app.post(
            url="/jobs",
            content_type='application/json',
            params=json.dumps(job),
            status=400
        )

    def test_orderly(self):
        """
        Test the 'orderly' algorithm
        This isn't really an algorithm. Just choose the first pair as submitted.
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        TestScheduler.fill_activities()
        TestScheduler.fill_optimizer()
        TestScheduler.fill_file_queue(self)
        job_id = self.submit_job("orderly")
        self.validate(job_id, expected_submitted='http://site01.es/file')

    def test_orderly_same_sources(self):
        """
        Test the 'orderly' algorithm, but the same source appears more than once
        This is a regression for FTS-323
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        TestScheduler.fill_activities()
        TestScheduler.fill_optimizer()
        TestScheduler.fill_file_queue(self)
        job = {
            'files': [
                {
                    'sources': [
                        'http://site01.es/file',
                        'http://site02.ch/file',
                        'http://site01.es/file'
                        ],
                    'destinations': ['http://dest.ch/file'+str(random.randint(0, 100)],
                    'selection_strategy': 'orderly',
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

        files = Session.query(File).filter(File.job_id == job_id)
        self.assertEqual('SUBMITTED', files[0].file_state)
        self.assertEqual('NOT_USED', files[1].file_state)
        self.assertEqual('NOT_USED', files[2].file_state)

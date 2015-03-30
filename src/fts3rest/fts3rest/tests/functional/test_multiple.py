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
from fts3.model import Job, File


class TestMultiple(TestController):
    """
    Test the submission of jobs with multiple files
    """

    def test_submit_with_alternatives(self):
        """
        Submit one transfer with multiple sources and multiple destinations.
        It must be treated as a transfer with alternatives
        For REST <= 3.2.3, usually only matching pairs would be picked, but this
        limitation was later removed
        https://its.cern.ch/jira/browse/FTS-97
        Because of this, we get a product between sources and destinations
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [
                {
                    'sources': ['http://source.es:8446/file', 'root://source.es/file'],
                    'destinations': ['http://dest.ch:8447/file', 'root://dest.ch/file'],
                    'selection_strategy': 'orderly',
                    'checksum': 'adler32:1234',
                    'filesize': 1024,
                    'metadata': {'mykey': 'myvalue'},
                }
            ],
            'params': {'overwrite': True}
        }

        answer = self.app.post(url="/jobs",
                               content_type='application/json',
                               params=json.dumps(job),
                               status=200)

        # Validate job in the database
        job_id = json.loads(answer.body)['job_id']
        db_job = Session.query(Job).get(job_id)

        self.assertEqual(db_job.reuse_job, 'R')

        self.assertEqual(len(db_job.files), 4)

        self.assertEqual(db_job.files[0].file_index, 0)
        self.assertEqual(db_job.files[0].source_surl, 'http://source.es:8446/file')
        self.assertEqual(db_job.files[0].dest_surl, 'http://dest.ch:8447/file')
        self.assertEqual(db_job.files[0].file_metadata['mykey'], 'myvalue')

        self.assertEqual(db_job.files[1].file_index, 0)
        self.assertEqual(db_job.files[1].source_surl, 'http://source.es:8446/file')
        self.assertEqual(db_job.files[1].dest_surl, 'root://dest.ch/file')
        self.assertEqual(db_job.files[1].file_metadata['mykey'], 'myvalue')

        self.assertEqual(db_job.files[2].file_index, 0)
        self.assertEqual(db_job.files[2].source_surl, 'root://source.es/file')
        self.assertEqual(db_job.files[2].dest_surl, 'http://dest.ch:8447/file')
        self.assertEqual(db_job.files[2].file_metadata['mykey'], 'myvalue')

        self.assertEqual(db_job.files[3].file_index, 0)
        self.assertEqual(db_job.files[3].source_surl, 'root://source.es/file')
        self.assertEqual(db_job.files[3].dest_surl, 'root://dest.ch/file')
        self.assertEqual(db_job.files[3].file_metadata['mykey'], 'myvalue')

        # Same file index, same hashed id
        uniq_hashes = set(map(lambda f: f.hashed_id, db_job.files))
        self.assertEqual(len(uniq_hashes), 1)

    def test_submit_multiple_transfers(self):
        """
        Submit one job with multiple independent transfers
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [
                {
                    'sources': ['srm://source.es:8446/file'],
                    'destinations': ['srm://dest.ch:8447/file'],
                    'selection_strategy': 'orderly',
                    'checksum': 'adler32:1234',
                    'filesize': 1024,
                    'metadata': {'mykey': 'myvalue'},
                },
                {
                    'sources': ['https://host.com/another/file'],
                    'destinations': ['https://dest.net/another/destination'],
                    'selection_strategy': 'whatever',
                    'checksum': 'adler32:56789',
                    'filesize': 512,
                    'metadata': {'flag': True}
                }
            ],
            'params': {'overwrite': True, 'verify_checksum': True}
        }

        answer = self.app.post(url="/jobs",
                               content_type='application/json',
                               params=json.dumps(job),
                               status=200)

        # Validate job in the database
        job_id = json.loads(answer.body)['job_id']
        db_job = Session.query(Job).get(job_id)

        self.assertNotEqual(db_job.reuse_job, 'R')

        self.assertEqual(len(db_job.files), 2)

        self.assertEqual(db_job.verify_checksum, True)

        self.assertEqual(db_job.files[0].file_index, 0)
        self.assertEqual(db_job.files[0].source_surl, 'srm://source.es:8446/file')
        self.assertEqual(db_job.files[0].dest_surl, 'srm://dest.ch:8447/file')
        self.assertEqual(db_job.files[0].checksum, 'adler32:1234')
        self.assertEqual(db_job.files[0].user_filesize, 1024)
        self.assertEqual(db_job.files[0].file_metadata['mykey'], 'myvalue')

        self.assertEqual(db_job.files[1].file_index, 1)
        self.assertEqual(db_job.files[1].source_surl, 'https://host.com/another/file')
        self.assertEqual(db_job.files[1].dest_surl, 'https://dest.net/another/destination')
        self.assertEqual(db_job.files[1].checksum, 'adler32:56789')
        self.assertEqual(db_job.files[1].user_filesize, 512)
        self.assertEqual(db_job.files[1].file_metadata['flag'], True)

        # Hashed ids must be all different
        uniq_hashes = set(map(lambda f: f.hashed_id, db_job.files))
        self.assertEqual(len(uniq_hashes), 2)

    def test_submit_combination(self):
        """
        Submit a job with two related transfers (alternatives) and
        a third independent one.
        This was originally allowed, but starting with 3.2.33 it was decided to be dropped, as it gives
        more trouble than it solves.
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [
                {
                    'sources': ['srm://source.es:8446/file', 'srm://source.fr:8443/file'],
                    'destinations': ['srm://dest.ch:8447/file'],
                    'selection_strategy': 'orderly',
                    'checksum': 'adler32:1234',
                    'filesize': 1024,
                    'metadata': {'mykey': 'myvalue'},
                },
                {
                    'sources': ['https://host.com/another/file'],
                    'destinations': ['https://dest.net/another/destination'],
                    'selection_strategy': 'whatever',
                    'checksum': 'adler32:56789',
                    'filesize': 512,
                    'metadata': {'flag': True}
                }
            ],
            'params': {'overwrite': True, 'verify_checksum': True}
        }

        self.app.post(url="/jobs",
                      content_type='application/json',
                      params=json.dumps(job),
                      status=400)

    def test_submit_alternatives_with_reuse(self):
        """
        One job with alternatives, and reuse set.
        This combination must be denied!
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['http://source.es:8446/file', 'root://source.es/file'],
                'destinations': ['http://dest.ch:8447/file', 'root://dest.ch/file'],
                'selection_strategy': 'orderly',
                'checksum': 'adler32:1234',
                'filesize': 1024,
                'metadata': {'mykey': 'myvalue'},
            }],
            'params': {'overwrite': True, 'reuse': True}
        }

        self.app.post(url="/jobs",
                      content_type='application/json',
                      params=json.dumps(job),
                      status=400)

    def test_submit_reuse(self):
        """
        Submit a reuse job
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [
                {
                    'sources': ['http://source.es:8446/file'],
                    'destinations': ['http://dest.ch:8447/file'],
                },
                {
                    'sources': ['http://source.es:8446/otherfile'],
                    'destinations': ['http://dest.ch:8447/otherfile']
                }
            ],
            'params': {'overwrite': True, 'reuse': True}
        }

        answer = self.app.post(url="/jobs",
                               content_type='application/json',
                               params=json.dumps(job),
                               status=200)

        job_id = json.loads(answer.body)['job_id']

        job = Session.query(Job).get(job_id)
        self.assertEqual(job.reuse_job, 'Y')

        # In a reuse job, the hashed ID must be the same for all files!
        # Regression for FTS-20
        files = Session.query(File).filter(File.job_id == job_id)
        hashed = files[0].hashed_id
        for f in files:
            self.assertEqual(hashed, f.hashed_id)

    def test_multihop(self):
        """
        Submit a multihop transfer
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [
                {
                    'sources': ['http://source.es:8446/file'],
                    'destinations': ['http://intermediate.ch:8447/file'],
                },
                {
                    'sources': ['http://intermediate.ch:8447/file'],
                    'destinations': ['http://dest.ch:8447/otherfile']
                }
            ],
            'params': {'overwrite': True, 'multihop': True}
        }

        answer = self.app.post(url="/jobs",
                               content_type='application/json',
                               params=json.dumps(job),
                               status=200)

        job_id = json.loads(answer.body)['job_id']

        # The hashed ID must be the same for all files!
        # Also, the reuse flag must be 'H' in the database
        job = Session.query(Job).get(job_id)

        self.assertEqual(job.reuse_job, 'H')

        files = Session.query(File).filter(File.job_id == job_id).all()
        self.assertEquals(2, len(files))
        hashed = files[0].hashed_id
        for f in files:
            self.assertEqual(hashed, f.hashed_id)

    def test_multihop_lfc(self):
        """
        Submit a multihop transfer with a final LFC hop
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [
                {
                    'sources': ['http://source.es:8446/file'],
                    'destinations': ['http://intermediate.ch:8447/file'],
                },
                {
                    'sources': ['http://intermediate.ch:8447/file'],
                    'destinations': ['lfc://lfc.ch/lfn']
                }
            ],
            'params': {'overwrite': True, 'multihop': True}
        }

        answer = self.app.post(url="/jobs",
                               content_type='application/json',
                               params=json.dumps(job),
                               status=200)

        job_id = json.loads(answer.body)['job_id']

        # The hashed ID must be the same for all files!
        # Also, the reuse flag must be 'H' in the database
        job = Session.query(Job).get(job_id)

        self.assertEqual(job.reuse_job, 'H')

        files = Session.query(File).filter(File.job_id == job_id).all()
        self.assertEquals(2, len(files))
        hashed = files[0].hashed_id
        for f in files:
            self.assertEqual(hashed, f.hashed_id)

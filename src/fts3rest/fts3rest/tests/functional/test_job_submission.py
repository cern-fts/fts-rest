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
import scipy.stats
import socket
from nose.plugins.skip import SkipTest

from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import File, Job, OptimizerActive


class TestJobSubmission(TestController):
    """
    Tests job submission
    """

    def _validate_submitted(self, job, no_vo=False):
        self.assertNotEqual(job, None)
        files = job.files
        self.assertNotEqual(files, None)

        self.assertEqual(job.user_dn, '/DC=ch/DC=cern/CN=Test User')
        if no_vo:
            self.assertEqual(job.vo_name, 'TestUser@cern.ch')
        else:
            self.assertEqual(job.vo_name, 'testvo')
        self.assertEqual(job.job_state, 'SUBMITTED')

        self.assertEqual(job.source_se, 'root://source.es')
        self.assertEqual(job.dest_se, 'root://dest.ch')
        self.assertEqual(job.overwrite_flag, True)
        self.assertEqual(job.verify_checksum, True)
        self.assertEqual(job.reuse_job, 'N')

        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].file_state, 'SUBMITTED')
        self.assertEqual(files[0].source_surl, 'root://source.es/file')
        self.assertEqual(files[0].dest_surl, 'root://dest.ch/file')
        self.assertEqual(files[0].source_se, 'root://source.es')
        self.assertEqual(files[0].dest_se, 'root://dest.ch')
        self.assertEqual(files[0].file_index, 0)
        self.assertEqual(files[0].selection_strategy, 'orderly')
        self.assertEqual(files[0].user_filesize, 1024)
        self.assertEqual(files[0].checksum, 'adler32:1234')
        self.assertEqual(files[0].file_metadata['mykey'], 'myvalue')
        if no_vo:
            self.assertEqual(files[0].vo_name, 'TestUser@cern.ch')
        else:
            self.assertEqual(files[0].vo_name, 'testvo')

        self.assertEquals(files[0].activity, 'default')

        # Validate optimizer too
        oa = Session.query(OptimizerActive).get(('root://source.es', 'root://dest.ch'))
        self.assertIsNotNone(oa)
        self.assertGreater(oa.active, 0)
        self.assertIsNotNone(oa.datetime)
        self.assertEqual(0, oa.ema)

        # Validate submitter
        self.assertEqual(socket.getfqdn(), job.submit_host)
        self.assertEqual('rest', job.agent_dn)

    def test_submit(self):
        """
        Submit a valid job
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
            'params': {'overwrite': True, 'verify_checksum': True}
        }

        answer = self.app.put(url="/jobs",
                              params=json.dumps(job),
                              status=200)

        # Make sure it was committed to the DB
        job_id = json.loads(answer.body)['job_id']
        self.assertGreater(job_id, 0)

        self._validate_submitted(Session.query(Job).get(job_id))

        return str(job_id)

    def test_submit_reuse(self):
        """
        Submit a valid reuse job
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
            'params': {'overwrite': True, 'verify_checksum': True, 'reuse': True}
        }

        answer = self.app.put(url="/jobs",
                              params=json.dumps(job),
                              status=200)

        # Make sure it was commited to the DB
        job_id = json.loads(answer.body)['job_id']
        self.assertGreater(len(job_id), 0)

        job = Session.query(Job).get(job_id)
        self.assertEqual(job.reuse_job, 'Y')

        return job_id

    def test_submit_Y(self):
        """
        Submit a valid reuse job, using 'Y' instead of True
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
            'params': {'overwrite': 'Y', 'verify_checksum': 'Y', 'reuse': 'Y'}
        }

        answer = self.app.put(url="/jobs",
                              params=json.dumps(job),
                              status=200)

        # Make sure it was commited to the DB
        job_id = json.loads(answer.body)['job_id']
        self.assertGreater(len(job_id), 0)

        job = Session.query(Job).get(job_id)
        self.assertEqual(job.reuse_job, 'Y')

    def test_submit_post(self):
        """
        Submit a valid job using POST instead of PUT
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
            'params': {'overwrite': True, 'verify_checksum': True}
        }

        answer = self.app.post(url="/jobs",
                               content_type='application/json',
                               params=json.dumps(job),
                               status=200)

        # Make sure it was committed to the DB
        job_id = json.loads(answer.body)['job_id']
        self.assertGreater(len(job_id), 0)

        self._validate_submitted(Session.query(Job).get(job_id))

        return job_id

    def test_submit_with_port(self):
        """
        Submit a valid job where the port is explicit in the url.
        source_se and dest_se must exclude this port
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['srm://source.es:8446/file'],
                'destinations': ['srm://dest.ch:8447/file'],
                'selection_strategy': 'orderly',
                'checksum': 'adler32:1234',
                'filesize': 1024,
                'metadata': {'mykey': 'myvalue'},
            }],
            'params': {'overwrite': True, 'verify_checksum': True}
        }

        answer = self.app.post(url="/jobs",
                               content_type='application/json',
                               params=json.dumps(job),
                               status=200)

        # Make sure it was committed to the DB
        job_id = json.loads(answer.body)['job_id']
        self.assertGreater(len(job_id), 0)

        db_job = Session.query(Job).get(job_id)

        self.assertEqual(db_job.source_se, 'srm://source.es')
        self.assertEqual(db_job.dest_se, 'srm://dest.ch')

        self.assertEqual(db_job.files[0].source_se, 'srm://source.es')
        self.assertEqual(db_job.files[0].dest_se, 'srm://dest.ch')

        return job_id

    def test_submit_only_query(self):
        """
        Submit a valid job, without a path, but with a query in the url.
        This is valid for some protocols (i.e. srm)
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['srm://source.es/?SFN=/path/'],
                'destinations': ['http://dest.ch/file'],
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

    def test_null_checksum(self):
        """
        Valid job, with checksum explicitly set to null
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['root://source.es/file'],
                'destinations': ['root://dest.ch/file'],
                'selection_strategy': 'orderly',
                'checksum': None,
                'filesize': 1024,
                'metadata': {'mykey': 'myvalue'},
            }],
            'params': {'overwrite': True, 'verify_checksum': True}
        }

        answer = self.app.post(url="/jobs",
                               content_type='application/json',
                               params=json.dumps(job),
                               status=200)

        # Make sure it was committed to the DB
        job_id = json.loads(answer.body)['job_id']
        self.assertGreater(len(job_id), 0)

        job = Session.query(Job).get(job_id)
        self.assertEqual(job.files[0].checksum, None)

        return job_id

    def test_checksum_no_verify(self):
        """
        Valid job, with checksum, but verify_checksum is not set
        In the DB, it must end as 'r' (compatibility with FTS3 behaviour)
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['root://source.es/file'],
                'destinations': ['root://dest.ch/file'],
                'selection_strategy': 'orderly',
                'checksum': '1234F',
                'filesize': 1024,
                'metadata': {'mykey': 'myvalue'},
            }],
            'params': {'overwrite': True}
        }

        answer = self.app.post(url="/jobs",
                               content_type='application/json',
                               params=json.dumps(job),
                               status=200)

        # Make sure it was committed to the DB
        job_id = json.loads(answer.body)['job_id']
        self.assertGreater(len(job_id), 0)

        job = Session.query(Job).get(job_id)
        self.assertEqual(job.files[0].checksum, '1234F')
        self.assertEqual(job.verify_checksum, 'r')

        return job_id

    def test_null_user_filesize(self):
        """
        Valid job, with filesize explicitly set to null
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['root://source.es/file'],
                'destinations': ['root://dest.ch/file'],
                'selection_strategy': 'orderly',
                'filesize': None,
                'metadata': {'mykey': 'myvalue'},
            }],
            'params': {'overwrite': True, 'verify_checksum': True}
        }

        answer = self.app.post(url="/jobs",
                               content_type='application/json',
                               params=json.dumps(job),
                               status=200)

        # Make sure it was committed to the DB
        job_id = json.loads(answer.body)['job_id']
        self.assertGreater(len(job_id), 0)

        job = Session.query(Job).get(job_id)
        self.assertEqual(job.files[0].user_filesize, 0)

        return job_id

    def test_no_vo(self):
        """
        Submit a valid job with no VO data in the credentials (could happen with plain SSL!)
        The job must be accepted, but assigned to the user's 'virtual' vo.
        """
        self.setup_gridsite_environment(no_vo=True)
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
            'params': {'overwrite': True, 'verify_checksum': True}
        }

        answer = self.app.put(url="/jobs",
                              params=json.dumps(job),
                              status=200)

        # Make sure it was commited to the DB
        job_id = json.loads(answer.body)['job_id']
        self.assertGreater(len(job_id), 0)

        self._validate_submitted(Session.query(Job).get(job_id), no_vo=True)

    def test_retry(self):
        """
        Submit with a specific retry value
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
            'params': {'overwrite': True, 'verify_checksum': True, 'retry': 42}
        }

        answer = self.app.put(url="/jobs",
                              params=json.dumps(job),
                              status=200)

        # Make sure it was commited to the DB
        job_id = json.loads(answer.body)['job_id']
        self.assertGreater(len(job_id), 0)

        job = Session.query(Job).get(job_id)
        self._validate_submitted(job)
        self.assertEqual(job.retry, 42)

    def test_optimizer_respected(self):
        """
        Submitting a job with an existing OptimizerActive entry must respect
        the existing value
        """
        self.test_submit()
        # Set active to 20
        oa = Session.query(OptimizerActive).get(('root://source.es', 'root://dest.ch'))
        oa.active = 20
        Session.merge(oa)
        Session.flush()
        Session.commit()
        # Submit a job
        self.test_submit()
        # Make sure it is still 20!
        oa2 = Session.query(OptimizerActive).get(('root://source.es', 'root://dest.ch'))
        self.assertEqual(20, oa2.active)

    def test_with_activity(self):
        """
        Submit a job specifiying activities for the files
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {'files': [
            {
                'sources': ['root://source.es/file'],
                'destinations': ['root://dest.ch/file'],
                'activity': 'my-activity'
            },
            {
                'sources': ['https://source.es/file2'],
                'destinations': ['https://dest.ch/file2'],
                'activity': 'my-second-activity'
            }]
        }

        answer = self.app.put(url="/jobs",
                              params=json.dumps(job),
                              status=200)

        # Make sure it was commited to the DB
        job_id = json.loads(answer.body)['job_id']
        self.assertGreater(len(job_id), 0)

        job = Session.query(Job).get(job_id)
        self.assertEqual(job.files[0].activity, 'my-activity')
        self.assertEqual(job.files[1].activity, 'my-second-activity')

    def test_surl_with_spaces(self):
        """
        Submit a job where the surl has spaces at the beginning and at the end
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['root://source.es/file\n \r '],
                'destinations': ['\r\n root://dest.ch/file\n\n \n'],
                'selection_strategy': 'orderly',
                'checksum': 'adler32:1234',
                'filesize': 1024.0,
                'metadata': {'mykey': 'myvalue'},
            }],
            'params': {'overwrite': True, 'verify_checksum': True}
        }

        answer = self.app.put(url="/jobs",
                              params=json.dumps(job),
                              status=200)

        # Make sure it was commited to the DB
        job_id = json.loads(answer.body)['job_id']
        self.assertGreater(len(job_id), 0)

        job = Session.query(Job).get(job_id)
        self._validate_submitted(job)

    def test_submit_different_protocols(self):
        """
        Source and destination protocol mismatch
        For REST <= 3.2.3, this used to be forbidden, but it was decided to allow it
        https://its.cern.ch/jira/browse/FTS-97
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['http://source.es:8446/file'],
                'destinations': ['root://dest.ch:8447/file'],
                'selection_strategy': 'orderly',
                'checksum': 'adler32:1234',
                'filesize': 1024,
                'metadata': {'mykey': 'myvalue'},
            }],
            'params': {'overwrite': True, 'verify_checksum': True}
        }

        response = self.app.post(
            url="/jobs",
            content_type='application/json',
            params=json.dumps(job),
            status=200
        )

        self.assertEquals(response.content_type, 'application/json')

        job_id = json.loads(response.body)['job_id']

        job = Session.query(Job).get(job_id)
        self.assertEqual(1, len(job.files))
        self.assertEqual('http://source.es:8446/file', job.files[0].source_surl)
        self.assertEqual('root://dest.ch:8447/file', job.files[0].dest_surl)

    def test_submit_with_cloud_cred(self):
        """
        Submit a job specifying cloud credentials
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['dropbox://dropbox.com/file'],
                'destinations': ['root://dest.ch:8447/file'],
                'selection_strategy': 'orderly',
                'checksum': 'adler32:1234',
                'filesize': 1024,
                'metadata': {'mykey': 'myvalue'},
            }],
            'params': {'overwrite': True, 'verify_checksum': True, 'credential': 'dropbox'}
        }

        response = self.app.post(
            url="/jobs",
            content_type='application/json',
            params=json.dumps(job),
            status=200
        )

        self.assertEquals(response.content_type, 'application/json')

        job_id = json.loads(response.body)['job_id']

        job = Session.query(Job).get(job_id)
        self.assertEqual(1, len(job.files))
        self.assertEqual('dropbox://dropbox.com/file', job.files[0].source_surl)
        self.assertEqual('root://dest.ch:8447/file', job.files[0].dest_surl)
        self.assertEqual('dropbox', job.user_cred)

    def test_submit_protocol_params(self):
        """
        Submit a transfer specifying some protocol parameters
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['http://source.es:8446/file'],
                'destinations': ['root://dest.ch:8447/file'],
                'selection_strategy': 'orderly',
                'checksum': 'adler32:1234',
                'filesize': 1024,
                'metadata': {'mykey': 'myvalue'},
            }],
            'params': {
                'overwrite': True,
                'verify_checksum': True,
                'timeout': 1234,
                'nostreams': 42,
                'buffer_size': 1025,
                'strict_copy': True
            }
        }
        response = self.app.post(
            url="/jobs",
            content_type='application/json',
            params=json.dumps(job),
            status=200
        )

        self.assertEquals(response.content_type, 'application/json')

        job_id = json.loads(response.body)['job_id']

        job = Session.query(Job).get(job_id)
        self.assertTrue(job.internal_job_params is not None)
        params = job.internal_job_params.split(',')
        self.assertIn('timeout:1234', params)
        self.assertIn('nostreams:42', params)
        self.assertIn('buffersize:1025', params)
        self.assertIn('strict', params)

    def test_files_balanced(self):
        """
        Checks the distribution of the file 'hashed ids' is reasonably uniformely distributed.
        hashed_id is a legacy name, its purpose is balance the transfers between hosts
        regardless of the number running in a giving moment
        """
        raise SkipTest('Disabled as it is not very reliable')
        self.setup_gridsite_environment()
        self.push_delegation()

        files = []
        for r in xrange(5000):
            files.append({
                'sources': ["root://source.es/file%d" % r],
                'destinations': ["root://dest.ch/file%d" % r]
            })

        job = {'files': files}

        answer = self.app.put(url="/jobs",
                              params=json.dumps(job),
                              status=200)

        job_id = json.loads(answer.body)['job_id']

        files = Session.query(File.hashed_id).filter(File.job_id == job_id)
        hashed_ids = map(lambda f: f.hashed_id, files)

        # Null hypothesis: the distribution of hashed_ids is uniform
        histogram, min_value, binsize, outsiders = scipy.stats.histogram(hashed_ids, defaultlimits=(0, 2 ** 16 - 1))
        chisq, pvalue = scipy.stats.chisquare(histogram)

        self.assertGreater(min_value, -1)
        self.assertEqual(outsiders, 0)
        self.assertGreater(pvalue, 0.1)

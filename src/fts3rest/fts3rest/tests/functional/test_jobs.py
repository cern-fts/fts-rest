from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import Job, File, OptimizerActive
import hashlib
from routes import url_for
import json


class TestJobs(TestController):
    """
    Tests for the job controller
    The focus is in submissions, since it is the one that modifies the database
    """

    def _hashedId(self, id):
        digest = hashlib.md5(str(id)).digest()
        b16digest = digest.encode('hex')
        return int(b16digest[:4], 16)


    def _validateSubmitted(self, job, noVo=False):
        self.assertNotEqual(job, None)
        files = job.files
        self.assertNotEqual(files, None)
        
        self.assertEqual(job.user_dn, '/DC=ch/DC=cern/OU=Test User')
        if noVo:
            self.assertEqual(job.vo_name, 'nil')
        else:
            self.assertEqual(job.vo_name, 'testvo')
        self.assertEqual(job.job_state, 'SUBMITTED')
        
        self.assertEqual(job.source_se, 'root://source.es') 
        self.assertEqual(job.dest_se, 'root://dest.ch') 
        self.assertEqual(job.overwrite_flag, True)
        self.assertEqual(job.verify_checksum, True)
        self.assertEqual(job.reuse_job, False)

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
        if noVo:
            self.assertEqual(files[0].vo_name, 'nil')
        else:
            self.assertEqual(files[0].vo_name, 'testvo')

        self.assertEquals(self._hashedId(files[0].file_id), files[0].hashed_id)
        self.assertEquals(files[0].activity, 'default')
        
        # Validate optimizer too
        oa = Session.query(OptimizerActive).get(('root://source.es', 'root://dest.ch'))
        self.assertTrue(oa is not None)
        self.assertTrue(oa.active > 0) 


    def test_submit(self):
        """
        Submit a valid job
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['root://source.es/file'],
                          'destinations': ['root://dest.ch/file'],
                          'selection_strategy': 'orderly',
                          'checksum':   'adler32:1234',
                          'filesize':    1024,
                          'metadata':    {'mykey': 'myvalue'},
                          }],
              'params': {'overwrite': True, 'verify_checksum': True}}
        
        answer = self.app.put(url = url_for(controller = 'jobs', action = 'submit'),
                              params = json.dumps(job),
                              status = 200)
        
        # Make sure it was commited to the DB
        jobId = json.loads(answer.body)['job_id']
        self.assertTrue(len(jobId) > 0)
        
        self._validateSubmitted(Session.query(Job).get(jobId))
        
        return jobId

    
    def test_submit_reuse(self):
        """
        Submit a valid reuse job
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['root://source.es/file'],
                          'destinations': ['root://dest.ch/file'],
                          'selection_strategy': 'orderly',
                          'checksum':   'adler32:1234',
                          'filesize':    1024,
                          'metadata':    {'mykey': 'myvalue'},
                          }],
              'params': {'overwrite': True, 'verify_checksum': True, 'reuse': True}}
        
        answer = self.app.put(url = url_for(controller = 'jobs', action = 'submit'),
                              params = json.dumps(job),
                              status = 200)
        
        # Make sure it was commited to the DB
        jobId = json.loads(answer.body)['job_id']
        self.assertTrue(len(jobId) > 0)
        
        job = Session.query(Job).get(jobId)
        self.assertEqual(job.reuse_job, True)
        
        return jobId
    
    
    def test_submit_post(self):
        """
        Submit a valid job using POST instead of PUT
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['root://source.es/file'],
                          'destinations': ['root://dest.ch/file'],
                          'selection_strategy': 'orderly',
                          'checksum':   'adler32:1234',
                          'filesize':    1024,
                          'metadata':    {'mykey': 'myvalue'},
                          }],
              'params': {'overwrite': True, 'verify_checksum': True}}
        
        answer = self.app.post(url = url_for(controller = 'jobs', action = 'submit'),
                               content_type = 'application/json',
                               params = json.dumps(job),
                               status = 200)
        
        # Make sure it was committed to the DB
        jobId = json.loads(answer.body)['job_id']
        self.assertTrue(len(jobId) > 0)
        
        self._validateSubmitted(Session.query(Job).get(jobId))
        
        return jobId


    def test_submit_with_port(self):
        """
        Submit a valid job where the port is explicit in the url.
        source_se and dest_se must exclude this port
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['srm://source.es:8446/file'],
                          'destinations': ['srm://dest.ch:8447/file'],
                          'selection_strategy': 'orderly',
                          'checksum':    'adler32:1234',
                          'filesize':    1024,
                          'metadata':    {'mykey': 'myvalue'},
                          }],
              'params': {'overwrite': True, 'verify_checksum': True}}
        
        answer = self.app.post(url = url_for(controller = 'jobs', action = 'submit'),
                               content_type = 'application/json',
                               params = json.dumps(job),
                               status = 200)
        
        # Make sure it was committed to the DB
        jobId = json.loads(answer.body)['job_id']
        self.assertTrue(len(jobId) > 0)
        
        dbJob = Session.query(Job).get(jobId)
        
        self.assertEqual(dbJob.source_se, 'srm://source.es')
        self.assertEqual(dbJob.dest_se, 'srm://dest.ch') 
        
        self.assertEqual(dbJob.files[0].source_se, 'srm://source.es') 
        self.assertEqual(dbJob.files[0].dest_se, 'srm://dest.ch') 
        
        return jobId
  
    
    def test_submit_only_query(self):
        """
        Submit a valid job, without a path, but with a query in the url.
        This is valid for some protocols (i.e. srm)
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['http://source.es/?SFN=/path/'],
                          'destinations': ['http://dest.ch/file'],
                          'selection_strategy': 'orderly',
                          'checksum':    'adler32:1234',
                          'filesize':    1024,
                          'metadata':    {'mykey': 'myvalue'},
                          }],
              'params': {'overwrite': True, 'copy_pin_lifetime': 3600, 'bring_online': 60,
                         'verify_checksum': True}}
        
        answer = self.app.post(url = url_for(controller = 'jobs', action = 'submit'),
                               content_type = 'application/json',
                               params = json.dumps(job),
                               status = 200)
        
        # Make sure it was committed to the DB
        jobId = json.loads(answer.body)['job_id']
        self.assertTrue(len(jobId) > 0)
        
        dbJob = Session.query(Job).get(jobId)
        self.assertEqual(dbJob.job_state, 'STAGING') 
        self.assertEqual(dbJob.files[0].file_state, 'STAGING') 
        
        return jobId


    def test_cancel(self):
        """
        Cancel a job
        """
        jobId = self.test_submit()
        answer = self.app.delete(url = url_for(controller = 'jobs', action = 'cancel', id = jobId),
                                 status = 200)
        job = json.loads(answer.body)
        
        self.assertEqual(job['job_id'], jobId) 
        self.assertEqual(job['job_state'], 'CANCELED') 
        for f in job['files']:
            self.assertEqual(f['file_state'], 'CANCELED') 
        
        # Is it in the database?
        job = Session.query(Job).get(jobId)
        self.assertEqual(job.job_state,'CANCELED')
        for f in job.files:
            self.assertEqual(f.file_state, 'CANCELED')


    def test_show_job(self):
        """
        Get information about a job
        """
        jobId = self.test_submit()
        answer = self.app.get(url = url_for(controller = 'jobs', action = 'show', id = jobId),
                              status = 200)
        job = json.loads(answer.body)
        
        self.assertEqual(job['job_id'], jobId) 
        self.assertEqual(job['job_state'], 'SUBMITTED') 


    def test_null_checksum(self):
        """
        Valid job, with checksum explicitly set to null
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['root://source.es/file'],
                          'destinations': ['root://dest.ch/file'],
                          'selection_strategy': 'orderly',
                          'checksum':   None,
                          'filesize':    1024,
                          'metadata':    {'mykey': 'myvalue'},
                          }],
              'params': {'overwrite': True, 'verify_checksum': True}}
        
        answer = self.app.post(url = url_for(controller = 'jobs', action = 'submit'),
                               content_type = 'application/json',
                               params = json.dumps(job),
                               status = 200)
        
        # Make sure it was committed to the DB
        jobId = json.loads(answer.body)['job_id']
        self.assertTrue(len(jobId) > 0)
        
        job = Session.query(Job).get(jobId)
        self.assertEqual(job.files[0].checksum, None)
        
        return jobId


    def test_checksum_no_verify(self):
        """
        Valid job, with checksum, but verify_checksum is not set
        In the DB, it must end as 'r' (compatibility with FTS3 behaviour)
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()

        job = {'files': [{'sources':      ['root://source.es/file'],
                          'destinations': ['root://dest.ch/file'],
                          'selection_strategy': 'orderly',
                          'checksum':   '1234F',
                          'filesize':    1024,
                          'metadata':    {'mykey': 'myvalue'},
                          }],
              'params': {'overwrite': True}}

        answer = self.app.post(url = url_for(controller = 'jobs', action = 'submit'),
                               content_type = 'application/json',
                               params = json.dumps(job),
                               status = 200)

        # Make sure it was committed to the DB
        jobId = json.loads(answer.body)['job_id']
        self.assertTrue(len(jobId) > 0)

        job = Session.query(Job).get(jobId)
        self.assertEqual(job.files[0].checksum, '1234F')
        self.assertEqual(job.verify_checksum, 'r')

        return jobId
    
    
    def test_null_user_filesize(self):
        """
        Valid job, with filesize explicitly set to null
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['root://source.es/file'],
                          'destinations': ['root://dest.ch/file'],
                          'selection_strategy': 'orderly',
                          'filesize':    None,
                          'metadata':    {'mykey': 'myvalue'},
                          }],
              'params': {'overwrite': True, 'verify_checksum': True}}
        
        answer = self.app.post(url = url_for(controller = 'jobs', action = 'submit'),
                               content_type = 'application/json',
                               params = json.dumps(job),
                               status = 200)
        
        # Make sure it was committed to the DB
        jobId = json.loads(answer.body)['job_id']
        self.assertTrue(len(jobId) > 0) 
        
        job = Session.query(Job).get(jobId)
        self.assertEqual(job.files[0].user_filesize, 0)
        
        return jobId
        
        
    def test_no_vo(self):
        """
        Submit a valid job with no VO data in the credentials (could happen with plain SSL!)
        The job must be accepted, but assigned to the 'nil' vo.
        """
        self.setupGridsiteEnvironment(noVo = True)
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['root://source.es/file'],
                          'destinations': ['root://dest.ch/file'],
                          'selection_strategy': 'orderly',
                          'checksum':   'adler32:1234',
                          'filesize':    1024,
                          'metadata':    {'mykey': 'myvalue'},
                          }],
              'params': {'overwrite': True, 'verify_checksum': True}}
        
        answer = self.app.put(url = url_for(controller = 'jobs', action = 'submit'),
                              params = json.dumps(job),
                              status = 200)
        
        # Make sure it was commited to the DB
        jobId = json.loads(answer.body)['job_id']
        self.assertTrue(len(jobId) > 0)
        
        self._validateSubmitted(Session.query(Job).get(jobId), noVo = True)


    def test_retry(self):
        """
        Submit with a specific retry value
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['root://source.es/file'],
                          'destinations': ['root://dest.ch/file'],
                          'selection_strategy': 'orderly',
                          'checksum':   'adler32:1234',
                          'filesize':    1024,
                          'metadata':    {'mykey': 'myvalue'},
                          }],
              'params': {'overwrite': True, 'verify_checksum': True, 'retry': 42}}
        
        answer = self.app.put(url = url_for(controller = 'jobs', action = 'submit'),
                              params = json.dumps(job),
                              status = 200)
        
        # Make sure it was commited to the DB
        jobId = json.loads(answer.body)['job_id']
        self.assertTrue(len(jobId) > 0)
        
        job = Session.query(Job).get(jobId)
        self._validateSubmitted(job)
        self.assertEqual(job.retry, 42)


    def test_optimizer_respected(self):
        """
        Submitting a job with an existing OptimizerActive entry must respect
        the existing value
        """
        # Set active to 20
        oa = Session.query(OptimizerActive).get(('root://source.es', 'root://dest.ch'))
        oa.active = 20
        Session.merge(oa)
        Session.flush()
        Session.commit()
        # Submit a job
        jobId = self.test_submit()
        # Make sure it is still 20!
        oa2 = Session.query(OptimizerActive).get(('root://source.es', 'root://dest.ch'))
        self.assertEqual(20, oa2.active)


    def test_with_activity(self):
        """
        Submit a job specifiying activities for the files
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['root://source.es/file'],
                          'destinations': ['root://dest.ch/file'],
                          'activity':    'my-activity'
                          },
                         {'sources':      ['https://source.es/file2'],
                          'destinations': ['https://dest.ch/file2'],
                          'activity':     'my-second-activity'
                          }]
               }
        
        answer = self.app.put(url = url_for(controller = 'jobs', action = 'submit'),
                              params = json.dumps(job),
                              status = 200)
        
        # Make sure it was commited to the DB
        jobId = json.loads(answer.body)['job_id']
        self.assertTrue(len(jobId) > 0)
        
        job = Session.query(Job).get(jobId)
        self.assertEqual(job.files[0].activity, 'my-activity')
        self.assertEqual(job.files[1].activity, 'my-second-activity')


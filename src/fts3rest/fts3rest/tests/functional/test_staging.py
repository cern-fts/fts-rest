from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import Job, File, OptimizerActive
import hashlib
import json


class TestSubmitToStaging(TestController):
    """
    Tests for the job controller
    Focus in staging transfers
    """

    def test_submit_to_staging(self):
        """
        Submit a job into staging
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['root://source.es/file'],
                          'destinations': ['root://dest.ch/file'],
                          'selection_strategy': 'orderly',
                          'checksum':    'adler32:1234',
                          'filesize':    1024,
                          'metadata':    {'mykey': 'myvalue'},
                          }],
              'params': {'overwrite': True, 'copy_pin_lifetime': 3600, 'bring_online': 60,
                         'verify_checksum': True}}
        
        answer = self.app.post(url = "/jobs",
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

  
    def test_submit_to_staging_no_lifetime(self):
        """
        Submit a job into staging, with pin lifetime not set
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['root://source.es/file'],
                          'destinations': ['root://dest.ch/file'],
                          'selection_strategy': 'orderly',
                          'checksum':    'adler32:1234',
                          'filesize':    1024,
                          'metadata':    {'mykey': 'myvalue'},
                          }],
              'params': {'overwrite': True, 'bring_online': 60,
                         'verify_checksum': True}}
        
        answer = self.app.post(url = "/jobs",
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


    def test_submit_to_staging_no_bring_online(self):
        """
        Submit a job into staging, with bring_online not set
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['root://source.es/file'],
                          'destinations': ['root://dest.ch/file'],
                          'selection_strategy': 'orderly',
                          'checksum':    'adler32:1234',
                          'filesize':    1024,
                          'metadata':    {'mykey': 'myvalue'},
                          }],
              'params': {'overwrite': True, 'copy_pin_lifetime': 60,
                         'verify_checksum': True}}
        
        answer = self.app.post(url = "/jobs",
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

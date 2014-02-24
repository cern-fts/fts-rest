from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import Job, File, OptimizerActive
import hashlib
import json

class TestListJobs(TestController):
    """
    Tests for the job controller, listing method
    """
    
    def _submit(self):
        job = {'files': [{'sources':      ['root://source.es/file'],
                          'destinations': ['root://dest.ch/file'],
                          'selection_strategy': 'orderly',
                          'checksum':   'adler32:1234',
                          'filesize':    1024,
                          'metadata':    {'mykey': 'myvalue'},
                          }],
              'params': {'overwrite': True, 'verify_checksum': True}}
        
        answer = self.app.put(url = "/jobs",
                              params = json.dumps(job),
                              status = 200)
        
        # Make sure it was commited to the DB
        jobId = json.loads(answer.body)['job_id']
        self.assertTrue(len(jobId) > 0)
        return jobId


    def test_list_job_default(self):
        """
        List active jobs
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        jobId = self._submit()

        answer = self.app.get(url = "/jobs",
                              status = 200)
        jobList = json.loads(answer.body)
        self.assertTrue(jobId in map(lambda j: j['job_id'], jobList))


    def test_list_with_dlg_id(self):
        """
        List active jobs with the right delegation id
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        creds = self.getUserCredentials()

        jobId = self._submit()

        answer = self.app.get(url = "/jobs",
                              params = {'dlg_id': creds.delegation_id},
                              status = 200)
        jobList = json.loads(answer.body)
        self.assertTrue(jobId in map(lambda j: j['job_id'], jobList))


    def test_list_bad_dlg_id(self):
        """
        Trying to list jobs belonging to a different delegation id
        must be forbidden
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        creds = self.getUserCredentials()

        answer = self.app.get(url = "/jobs",
                              params = {'dlg_id': creds.delegation_id + '1234'},
                              status = 403)


    def test_list_bad_dn(self):
        """
        Trying to list with the right delegation id mismatched bad DN is a bad
        request
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        creds = self.getUserCredentials()

        answer = self.app.get(url = "/jobs",
                              params = {'dlg_id': creds.delegation_id, 'user_dn': '/CN=1234'},
                              status = 400)


    def test_list_with_state_empty(self):
        """
        Filter by state (no match)
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        creds = self.getUserCredentials()

        jobId = self._submit()

        answer = self.app.get(url = "/jobs",
                              params = {'dlg_id': creds.delegation_id, 'state_in': 'FINISHED,FAILED,CANCELED'},
                              status = 200)
        jobList = json.loads(answer.body)
        self.assertFalse(jobId in map(lambda j: j['job_id'], jobList))


    def test_list_with_state_match(self):
        """
        Filter by state (match)
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        creds = self.getUserCredentials()

        jobId = self._submit()

        answer = self.app.get(url = "/jobs",
                              params = {'dlg_id': creds.delegation_id, 'state_in': 'ACTIVE,SUBMITTED'},
                              status = 200)
        jobList = json.loads(answer.body)
        self.assertTrue(jobId in map(lambda j: j['job_id'], jobList))


    def test_list_with_state_no_dlg_id(self):
        """
        When specifying the statuses in the query, dlg_id is mandatory
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        creds = self.getUserCredentials()

        answer = self.app.get(url = "/jobs",
                              params = {'state_in': 'SUBMITTED,ACTIVE'},
                              status = 403)


    def test_list_no_vo(self):
        """
        Submit a valid job with no VO data in the credentials. Listing it should be possible
        afterwards (regression test for FTS-18)
        """
        self.setupGridsiteEnvironment(noVo = True)
        self.pushDelegation()
        
        jobId = self._submit()
        
        # Must be in the listings!
        answer = self.app.get(url = "/jobs",
                              status = 200)
        jobList = json.loads(answer.body)
        self.assertTrue(jobId in map(lambda j: j['job_id'], jobList))


    def test_get_no_vo(self):
        """
        Submit a valid job with no VO data in the credentials. Stating it should be possible
        afterwards (regression test for FTS-18)
        """
        self.setupGridsiteEnvironment(noVo = True)
        self.pushDelegation()
        
        jobId = self._submit()
        
        # Must be in the listings!
        answer = self.app.get(url = "/jobs/%s" % (jobId),
                              status = 200)
        jobInfo = json.loads(answer.body)
        self.assertEqual(jobId, jobInfo['job_id'])
        self.assertEqual('nil', jobInfo['vo_name'])


    def test_get_field(self):
        """
        Request a field from a job  
        """
        self.setupGridsiteEnvironment(noVo = True)
        self.pushDelegation()

        jobId = self._submit()
        
        answer = self.app.get(url = "/jobs/%s/job_state" % (jobId),
                              status = 200)
        state = json.loads(answer.body)
        self.assertEqual(state, 'SUBMITTED')

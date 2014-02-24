from datetime import timedelta
from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import Job, File
import json


class TestInvalidSubmits(TestController):
    """
    Collection of invalid submissions. Intended to check if the
    job controller filters properly malformed and/or invalid requests.
    """
    
    def test_submit_malformed(self):
        """
        Submit a piece of data that is not well-formed json
        """
        self.assertFalse('GRST_CRED_AURI_0' in self.app.extra_environ)
        self.setupGridsiteEnvironment()
        self.assertTrue('GRST_CRED_AURI_0' in self.app.extra_environ)
        self.app.put(url = "/jobs",
                     params = 'thisXisXnotXjson',
                     status = 400)


    def test_submit_no_transfers(self):
        """
        Submit valid json data, but without actual transfers
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        job = {'parameters': {}}
        
        answer = self.app.put(url = "/jobs",
                              params = json.dumps(job),
                              status = 400)


    def test_submit_different_protocols(self):
        """
        Source and destination protocol mismatch
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['http://source.es:8446/file'],
                          'destinations': ['root://dest.ch:8447/file'],
                          'selection_strategy': 'orderly',
                          'checksum':    'adler32:1234',
                          'filesize':    1024,
                          'metadata':    {'mykey': 'myvalue'},
                          }],
              'params': {'overwrite': True, 'verify_checksum': True}}
        
        answer = self.app.post(url = "/jobs",
                               content_type = 'application/json',
                               params = json.dumps(job),
                               status = 400)


    def test_missing_job(self):
        """
        Request an invalid job
        """
        self.setupGridsiteEnvironment()
        self.app.get(url = "/jobs/1234x",
                     status = 404)


    def test_no_protocol(self):
        """
        Submit a valid transfer, but with urls with no protocol
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['/etc/passwd'],
                          'destinations': ['/srv/pub'],
                          }]}
        
        answer = self.app.post(url = "/jobs",
                               content_type = 'application/json',
                               params = json.dumps(job),
                               status = 400)
        
    def test_no_file(self):
        """
        Submit a valid transfer, but using file://
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['file:///etc/passwd'],
                          'destinations': ['file:///srv/pub'],
                          }]}
        
        answer = self.app.post(url = "/jobs",
                               content_type = 'application/json',
                               params = json.dumps(job),
                               status = 400)


    def test_one_single_slash(self):
        """
        Well-formed json, but source url is malformed
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['gsiftp:/source.es:8446/file'],
                          'destinations': ['gsiftp://dest.ch:8446/file'],
                          'selection_strategy': 'orderly',
                          'checksum':    'adler32:1234',
                          'filesize':    1024,
                          'metadata':    {'mykey': 'myvalue'},
                          }],
              'params': {'overwrite': True, 'verify_checksum': True}}

        answer = self.app.post(url = "/jobs",
                               content_type = 'application/json',
                               params = json.dumps(job),
                               status = 400)
        
    def test_empty_path(self):
        """
        Well-formed json, but source path is missing
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['gsiftp://source.es:8446/'],
                          'destinations': ['gsiftp://dest.ch:8446/file'],
                          'selection_strategy': 'orderly',
                          'checksum':    'adler32:1234',
                          'filesize':    1024,
                          'metadata':    {'mykey': 'myvalue'},
                          }],
              'params': {'overwrite': True, 'verify_checksum': True}}

        answer = self.app.post(url = "/jobs",
                               content_type = 'application/json',
                               params = json.dumps(job),
                               status = 400)


    def test_submit_missing_surl(self):
        """
        Well-formed json, but source url is missing
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        job = {'transfers': [{'destinations': ['root://dest.ch/file']}]}
        
        answer = self.app.put(url = "/jobs",
                              params = json.dumps(job),
                              status = 400)
        
        job = {'transfers': [{'source': 'root://source.es/file'}]}
        
        answer = self.app.put(url = "/jobs",
                              params = json.dumps(job),
                              status = 400)


    def test_invalid_surl(self):
        """
        Well-formed json, but the urls are malformed
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        job = {'files': [{'sources':      ['http: //source.es/file'], # Note the space!
                          'destinations': ['http: //dest.ch/file'],
                          'selection_strategy': 'orderly',
                          'checksum':   'adler32:1234',
                          'filesize':    1024,
                          'metadata':    {'mykey': 'myvalue'},
              }]}
        
        answer = self.app.put(url = "/jobs",
                              params = json.dumps(job),
                              status = 400)


    def test_submit_no_creds(self):
        """
        Submission without valid credentials is forbidden
        """
        self.assertFalse('GRST_CRED_AURI_0' in self.app.extra_environ)
        self.app.put(url = "/jobs",
                     params = 'thisXisXnotXjson',
                     status = 403)


    def test_submit_no_delegation(self):
        """
        Submission with valid credentials, but without a delegated proxy,
        must request a delegation
        """
        self.setupGridsiteEnvironment()
        
        job = {'Files': [{'sources': ['root://source/file'],
                          'destinations': ['root://dest/file'],
                         }]}
        
        self.app.put(url = "/jobs",
                     params = json.dumps(job),
                     status = 419)

    def test_submit_expired_credentials(self):
        """
        Submission with an expired proxy must request a delegation
        """
        self.setupGridsiteEnvironment()
        self.pushDelegation(lifetime = timedelta(hours=-1))

        job = {'Files': [{'sources': ['root://source/file'],
                  'destinations': ['root://dest/file'],
                 }]}
        
        self.app.put(url = "/jobs",
                     params = json.dumps(job),
                     status = 419)

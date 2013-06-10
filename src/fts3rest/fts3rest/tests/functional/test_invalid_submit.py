from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import Job, File
from routes import url_for
import json


class TestInvalidSubmits(TestController):
    
    def test_submit_malformed(self):
        assert 'GRST_CRED_AURI_0' not in self.app.extra_environ
        self.setupGridsiteEnvironment()
        assert 'GRST_CRED_AURI_0' in self.app.extra_environ
        self.app.put(url = url_for(controller = 'jobs', action = 'submit'),
                     params = 'thisXisXnotXjson',
                     status = 400)


    def test_submit_no_transfers(self):
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        job = {'parameters': {}}
        
        answer = self.app.put(url = url_for(controller = 'jobs', action = 'submit'),
                              params = json.dumps(job),
                              status = 400)


    def test_submit_different_protocols(self):
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['http://source.es:8446/file'],
                          'destinations': ['root://dest.ch:8447/file'],
                          'selection_strategy': 'orderly',
                          'checksums':   'adler32:1234',
                          'filesize':    1024,
                          'metadata':    {'mykey': 'myvalue'},
                          }],
              'params': {'overwrite': True, 'verify_checksum': True}}
        
        answer = self.app.post(url = url_for(controller = 'jobs', action = 'submit'),
                               content_type = 'application/json',
                               params = json.dumps(job),
                               status = 400)


    def test_missing_job(self):
        self.setupGridsiteEnvironment()
        self.app.get(url = url_for(controller = 'jobs', action = 'show', id = '1234x'),
                      status = 404)


    def test_no_protocol(self):
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['/etc/passwd'],
                          'destinations': ['/srv/pub'],
                          }]}
        
        answer = self.app.post(url = url_for(controller = 'jobs', action = 'submit'),
                               content_type = 'application/json',
                               params = json.dumps(job),
                               status = 400)
        
    def test_no_file(self):
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['file:///etc/passwd'],
                          'destinations': ['file:///srv/pub'],
                          }]}
        
        answer = self.app.post(url = url_for(controller = 'jobs', action = 'submit'),
                               content_type = 'application/json',
                               params = json.dumps(job),
                               status = 400)


    def test_one_single_slash(self):
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['gsiftp:/source.es:8446/file'],
                          'destinations': ['gsiftp://dest.ch:8446/file'],
                          'selection_strategy': 'orderly',
                          'checksums':   'adler32:1234',
                          'filesize':    1024,
                          'metadata':    {'mykey': 'myvalue'},
                          }],
              'params': {'overwrite': True, 'verify_checksum': True}}

        answer = self.app.post(url = url_for(controller = 'jobs', action = 'submit'),
                               content_type = 'application/json',
                               params = json.dumps(job),
                               status = 400)
        
    def test_empty_path(self):
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['gsiftp://source.es:8446/'],
                          'destinations': ['gsiftp://dest.ch:8446/file'],
                          'selection_strategy': 'orderly',
                          'checksums':   'adler32:1234',
                          'filesize':    1024,
                          'metadata':    {'mykey': 'myvalue'},
                          }],
              'params': {'overwrite': True, 'verify_checksum': True}}

        answer = self.app.post(url = url_for(controller = 'jobs', action = 'submit'),
                               content_type = 'application/json',
                               params = json.dumps(job),
                               status = 400)

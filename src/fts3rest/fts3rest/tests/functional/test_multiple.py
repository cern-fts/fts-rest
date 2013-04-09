from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import Job, File
from routes import url_for
import json


class TestMultiple(TestController):
    
    def test_submit_multiple_sources(self):
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['http://source.es:8446/file',
                                           'root://source.es/file'],
                          'destinations': ['http://dest.ch:8447/file',
                                           'root://dest.ch/file'],
                          'selection_strategy': 'orderly',
                          'checksum':   'adler32:1234',
                          'filesize':    1024,
                          'metadata':    {'mykey': 'myvalue'},
                          }],
              'params': {'overwrite': True}}
        
        answer = self.app.post(url = url_for(controller = 'jobs', action = 'submit'),
                               content_type = 'application/json',
                               params = json.dumps(job),
                               status = 200)
        
        # Validate job in the database
        jobId = json.loads(answer.body)['job_id']
        dbJob = Session.query(Job).get(jobId)
        
        assert len(dbJob.files) == 2
        
        assert dbJob.files[0].file_index  == 0
        assert dbJob.files[0].source_surl == 'http://source.es:8446/file'
        assert dbJob.files[0].dest_surl   == 'http://dest.ch:8447/file'
        metadata = json.loads(dbJob.files[0].file_metadata)
        assert metadata['mykey'] == 'myvalue'
        
        assert dbJob.files[1].file_index  == 0
        assert dbJob.files[1].source_surl == 'root://source.es/file'
        assert dbJob.files[1].dest_surl   == 'root://dest.ch/file'
        metadata = json.loads(dbJob.files[1].file_metadata)
        assert metadata['mykey'] == 'myvalue'
        


    def test_submit_multiple_transfers(self):
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['srm://source.es:8446/file'],
                          'destinations': ['srm://dest.ch:8447/file'],
                          'selection_strategy': 'orderly',
                          'checksum':     'adler32:1234',
                          'filesize':     1024,
                          'metadata':     {'mykey': 'myvalue'},
                          },
                         {'sources':      ['https://host.com/another/file'],
                          'destinations': ['https://dest.net/another/destination'],
                          'selection_strategy': 'whatever',
                          'checksum':     'adler32:56789',
                          'filesize':     512,
                          'metadata':     {'flag': True}
                          }],
              'params': {'overwrite': True, 'verify_checksum': True}}
        
        answer = self.app.post(url = url_for(controller = 'jobs', action = 'submit'),
                               content_type = 'application/json',
                               params = json.dumps(job),
                               status = 200)
        
        # Validate job in the database
        jobId = json.loads(answer.body)['job_id']
        dbJob = Session.query(Job).get(jobId)
        
        assert len(dbJob.files) == 2
        
        assert dbJob.verify_checksum == 'Y'
        
        assert dbJob.files[0].file_index    == 0
        assert dbJob.files[0].source_surl   == 'srm://source.es:8446/file'
        assert dbJob.files[0].dest_surl     == 'srm://dest.ch:8447/file'
        assert dbJob.files[0].checksum      == 'adler32:1234'
        assert dbJob.files[0].user_filesize == 1024
        metadata = json.loads(dbJob.files[0].file_metadata)
        assert metadata['mykey'] == 'myvalue'
        
        assert dbJob.files[1].file_index    == 1
        assert dbJob.files[1].source_surl   == 'https://host.com/another/file'
        assert dbJob.files[1].dest_surl     == 'https://dest.net/another/destination'
        assert dbJob.files[1].checksum      == 'adler32:56789'
        assert dbJob.files[1].user_filesize == 512
        metadata = json.loads(dbJob.files[1].file_metadata)
        assert metadata['flag'] == True


    def test_submit_combination(self):
        self.setupGridsiteEnvironment()
        self.pushDelegation()
        
        job = {'files': [{'sources':      ['srm://source.es:8446/file',
                                           'srm://source.fr:8443/file'],
                          'destinations': ['srm://dest.ch:8447/file'],
                          'selection_strategy': 'orderly',
                          'checksum':     'adler32:1234',
                          'filesize':     1024,
                          'metadata':     {'mykey': 'myvalue'},
                          },
                         {'sources':      ['https://host.com/another/file'],
                          'destinations': ['https://dest.net/another/destination'],
                          'selection_strategy': 'whatever',
                          'checksum':    'adler32:56789',
                          'filesize':     512,
                          'metadata':     {'flag': True}
                          }],
              'params': {'overwrite': True, 'verify_checksum': True}}
        
        answer = self.app.post(url = url_for(controller = 'jobs', action = 'submit'),
                               content_type = 'application/json',
                               params = json.dumps(job),
                               status = 200)
        
        # Validate job in the database
        jobId = json.loads(answer.body)['job_id']
        dbJob = Session.query(Job).get(jobId)
        
        assert len(dbJob.files) == 3
        
        assert dbJob.files[0].file_index    == 0
        assert dbJob.files[0].source_surl   == 'srm://source.es:8446/file'
        assert dbJob.files[0].dest_surl     == 'srm://dest.ch:8447/file'
        assert dbJob.files[0].checksum      == 'adler32:1234'
        assert dbJob.files[0].user_filesize == 1024
        metadata = json.loads(dbJob.files[0].file_metadata)
        assert metadata['mykey'] == 'myvalue'
        
        assert dbJob.files[1].file_index    == 0
        assert dbJob.files[1].source_surl   == 'srm://source.fr:8443/file'
        assert dbJob.files[1].dest_surl     == 'srm://dest.ch:8447/file'
        assert dbJob.files[1].checksum      == 'adler32:1234'
        assert dbJob.files[1].user_filesize == 1024
        metadata = json.loads(dbJob.files[0].file_metadata)
        assert metadata['mykey'] == 'myvalue'
        
        assert dbJob.files[2].file_index    == 1
        assert dbJob.files[2].source_surl   == 'https://host.com/another/file'
        assert dbJob.files[2].dest_surl     == 'https://dest.net/another/destination'
        assert dbJob.files[2].checksum      == 'adler32:56789'
        assert dbJob.files[2].user_filesize == 512
        metadata = json.loads(dbJob.files[2].file_metadata)
        assert metadata['flag'] == True

from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import ArchivedJob, ArchivedFile
from routes import url_for
import json


class TestArchive(TestController):
    
    def _insertJob(self):
        job = ArchivedJob()
        
        job.job_id    = '111-222-333'
        job.job_state = 'CANCELED'
        
        file = ArchivedFile()
        file.job_id     = job.job_id
        file.file_id    = 1234
        file.file_state = 'CANCELED'
        file.source_se  = 'srm://source'
        file.dest_se    = 'srm://dest'        
        
        Session.merge(job)
        Session.merge(file)
        Session.commit()
        return job.job_id
        
        
    def testGetFromArchive(self):
        self.setupGridsiteEnvironment()
        
        job_id = self._insertJob()
        answer = self.app.get(url = url_for(controller = 'archive', action = 'show', id = job_id),
                              status = 200)
        job = json.loads(answer.body)
        
        assert job['job_id']    == job_id
        assert job['job_state'] == 'CANCELED'
        
        assert len(job['files']) == 1
        
        assert job['files'][0]['file_state'] == 'CANCELED'
        assert job['files'][0]['source_se']  == 'srm://source'
        assert job['files'][0]['dest_se']  == 'srm://dest'
        assert job['files'][0]['file_id']  == 1234

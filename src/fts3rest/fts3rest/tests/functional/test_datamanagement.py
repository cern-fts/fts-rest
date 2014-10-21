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
from datetime import datetime

from fts3rest.lib.base import Session
from fts3rest.tests import TestController
from fts3rest.controllers.datamanagement import DatamanagementController


class TestDatamanagement(TestController):
    """
    Tests for the job rename, mkdir,unlink, rmdir.
    """
     
    def test_reame_post(self):
        """
        Rename a file or folder.
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        rename_path = {"old":"root://source.es/file","new":"root://source.es/File"}
        answer = self.app.post(url="/dm/rename", content_type='application/json', params=json.dumps(rename_path),status = 200)
        
        job_list= json.loads(answer.body)
        self.assertEqual(job_list['old'], 'root://source.es/file')
        self.assertEqual(job_list['new'], 'root://source.es/File')


    def test_mkdir_post(self):
        """
        Create a folder.
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        mkdir_path = {"surl":"root://source.es/file"}
        answer = self.app.post(url="/dm/mkdir", content_type='application/json', params=json.dumps(mkdir_path),status = 200)

        job_list= json.loads(answer.body)
        self.assertEqual(job_list['surl'], 'root://source.es/file')

    def test_rmdir_post(self):
        """
        Remove a folder.
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        rmdir_path = {"surl":"root://source.es/file"}
        answer = self.app.post(url="/dm/rmdir", content_type='application/json', params=json.dumps(rmdir_path),status = 200)

        job_list= json.loads(answer.body)
        self.assertEqual(job_list['surl'], 'root://source.es/file')

     def test_unlink_post(self):
        """
        Remove a file.
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        unlink_path = {"surl":"root://source.es/file"}
        answer = self.app.post(url="/dm/unlink", content_type='application/json', params=json.dumps(unlink_path),status = 200)

        job_list= json.loads(answer.body)
        self.assertEqual(job_list['surl'], 'root://source.es/file')

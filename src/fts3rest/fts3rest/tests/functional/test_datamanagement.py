#   Copyright notice:
#   Copyright CERN, 2014.
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


from fts3rest.tests import TestController


class TestDatamanagement(TestController):
    """
    Tests for user and storage banning
    """

    def setUp(self):
        super(TestDatamanagement, self).setUp()
        self.setup_gridsite_environment()

    def test_get_list(self):
        """
        Try list the content of a remote directory
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        response = self.app.get(
            url="/dm/list",
            params={
                'surl': 'mock://destination.es/file?list=a:1755:0,b:0755:123,c:000:0,d:0444:1234',
                'size': 1,
                'mode': 0775,
                'mtime': 5
            },
            status=200
        ).json
        self.assertIn('a', response)
        self.assertIn('b', response)
        self.assertIn('c', response)
        self.assertIn('d', response)
        self.assertEqual(123, response['b']['size'])

    def test_missing_surl(self):
        """
        Try list the content of a remote directory
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        self.app.get(url="/dm/list?size=1&mode=0755&mtime=5", status=400)

    def test_get_stat(self):
        """
        Try stat a remote file
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        self.app.get(
            url="/dm/stat",
            params={
                'surl': 'mock://destination.es/file',
                'mode': 1,
                'nlink': 1,
                'size': 1,
                'atime': 1,
                'mtime': 1,
                'ctime': 1
            },
            status=200
        )

    def test_rename(self):
        """
        Try to rename
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        self.app.post(
            url="/dm/rename",
            params={
                'surl': 'mock://destination.es/file3',
                'mode': 0775,
                'nlink': 1,
                'size': 1,
                'atime': 1,
                'mtime': 1,
                'ctime': 1},
            status=400
        )

    def test_unlink(self):
        """
        Try to unlink
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        self.app.post(
            url="/dm/unlink",
            params={
                'surl': 'mock://destination.es/file3',
                'size': 1,
                'mode': 5,
                'mtime': 5
            },
            status=400
        )

    def test_rmdir(self):
        """
        Try to rmdir
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        self.app.post(
            url="/dm/rmdir",
            params={
                'surl': 'mock://destination.es/file3',
                'mode': 0775,
                'nlink': 1,
                'size': 1,
                'atime': 1,
                'mtime': 1,
                'ctime': 1
            },
            status=400
        )

    def test_mkdir(self):
        """
        Try to mkdir
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        self.app.post(
            url="/dm/mkdir",
            params={
                'surl': 'mock://destination.es/file3',
                'mode': 0775,
                'nlink': 1,
                'size': 1,
                'atime': 1,
                'mtime': 1,
                'ctime': 1
            },
            status=400
        )

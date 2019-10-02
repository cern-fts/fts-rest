#   Copyright notice:
#   Copyright CERN, 2015.
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
from fts3rest.lib.base import Session
from fts3.model import CloudStorage, CloudStorageUser


class TestConfigCloud(TestController):

    def setUp(self):
        super(TestConfigCloud, self).setUp()
        self.setup_gridsite_environment()
        Session.query(CloudStorage).delete()
        Session.query(CloudStorageUser).delete()
        Session.commit()

    def test_add_s3(self):
        """
        Add credentials for a S3 storage
        """
        self.app.post_json(
            url="/config/cloud_storage",
            params={
                'storage_name': 'S3:host',
                'service_api_url': 'cs3.cern.ch'
            },
            status=201
        )
        storage = Session.query(CloudStorage).get('S3:host')

    def test_add_dropbox(self):
        """
        Add credentials for a Dropbox storage
        """
        self.app.post_json(
            url="/config/cloud_storage",
            params={
                'storage_name': 'dropbox',
                'app_key': 'dropbox_app_key',
                'app_secret': 'dropbox_app_secret',
                'service_api_url': 'https://www.dropbox.com/1'
            },
            status=201
        )
        storage = Session.query(CloudStorage).get('dropbox')
        self.assertEqual('dropbox_app_key', storage.app_key)
        self.assertEqual('dropbox_app_secret', storage.app_secret)
        self.assertEqual('https://www.dropbox.com/1', storage.service_api_url)

    def test_list_cloud_storages(self):
        """
        Add both, list them
        """
        self.test_add_s3()
        self.test_add_dropbox()

        storages = self.app.get_json(url="/config/cloud_storage", status=200).json

        self.assertEqual(2, len(storages))

    def test_remove_storage(self):
        """
        Remove an entry
        """
        self.test_add_s3()
        self.app.delete(url="/config/cloud_storage/S3:host", status=204)
        storage = Session.query(CloudStorage).get('S3:host')
        self.assertIsNone(storage)

    def test_modify_credentials(self):
        """
        Modify an entry
        """
        self.test_add_dropbox()
        self.app.post_json(
            url="/config/cloud_storage",
            params={
                'storage_name': 'dropbox',
                'app_key': 'new_app_key',
                'app_secret': 'new_app_secret',
                'service_api_url': 'https://www.dropbox.com/1'
            },
            status=201
        )
        storage = Session.query(CloudStorage).get('dropbox')
        self.assertEqual('new_app_key', storage.app_key)
        self.assertEqual('new_app_secret', storage.app_secret)
        self.assertEqual('https://www.dropbox.com/1', storage.service_api_url)

    def test_add_vo_s3(self):
        """
        Add the keys for an S3 endpoint for a given VO
        """
        self.test_add_s3()
        self.app.post_json(
            url="/config/cloud_storage/S3:host",
            params={
                'vo_name': 'testvo',
                'access_key': '1234',
                'secret_key': 'abcd',
            },
            status=201
        )
        user = Session.query(CloudStorageUser).get(('', 'S3:host', 'testvo'))
        self.assertEqual('1234', user.access_token)
        self.assertEqual('abcd', user.access_token_secret)

        users = self.app.get_json(url="/config/cloud_storage/S3:host", status=200).json
        self.assertEqual(1, len(users))
        self.assertEqual('testvo', users[0]['vo_name'])

    def test_add_vo_no_s3(self):
        """
        Try to add the keys, but the storage is not registered
        """
        self.app.post_json(
            url="/config/cloud_storage/S3:host",
            params={
                'vo_name': 'dteam',
                'access_key': '1234',
                'secret_key': 'abcd',
            },
            status=404
        )

    def test_delete_s3_rights(self):
        """
        Remove VO entry
        """
        self.test_add_vo_s3()
        self.app.delete(url="/config/cloud_storage/S3:host/testvo", status=204)
        user = Session.query(CloudStorageUser).get(('', 'S3:host', 'testvo'))
        self.assertIsNone(user)

    def test_missing_storage_name(self):
        """
        Missing storage name
        """
        self.app.post_json(
            url="/config/cloud_storage",
            params={
                'app_key': 'dropbox_app_key',
                'app_secret': 'dropbox_app_secret',
                'service_api_url': 'https://www.dropbox.com/1'
            },
            status=400
        )

    def test_remove_storage_wrong(self):
        """
        The storage does not exist
        """
        self.app.delete(url="/config/cloud_storage/dsfsd:host", status=404)

    def test_add_wrong(self):
        """
        One of user_dn or vo_name must be specified
        """
        self.test_add_s3()
        self.app.post_json(
            url="/config/cloud_storage/S3:host",
            params={'access_key': '1234', 'secret_key': 'abcd',}, status=400)

    def test_delete_wrong(self):
        """
        Try to delete the storage does not exist (wrong storage name)
        """
        self.app.delete(url="/config/cloud_storage/:host/testvo", status=404)

    def test_add_wrong(self):
        """
        Try to add the storage does not exist
        """
        self.app.get(url="/config/cloud_storage/:host", status=404)
        self.app.get(url="/config/cloud_storage/dfsdf:host", status=404)

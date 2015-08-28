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

import json

from fts3rest.lib.base import Session
from fts3rest.tests import TestController
from fts3rest.controllers.CSdropbox import DropboxConnector
from fts3.model import CloudStorage, CloudStorageUser


def _oauth_header_dict(raw_header):
    parts = [h.strip() for h in raw_header[6:].split(',')]
    d = dict()
    for p in parts:
        k, v = p.split('=', 2)
        d[k] = v
    return d


def _mocked_dropbox_make_call(self, command_url, auth_headers, parameters):
    assert command_url.startswith('https://api.dropbox.com/')
    assert auth_headers.startswith('OAuth ')

    oauth_headers = _oauth_header_dict(auth_headers)

    command_path = command_url[23:]
    if command_path == '/1/oauth/request_token':
        assert oauth_headers['oauth_consumer_key'] == '"1234"'
        assert oauth_headers['oauth_signature'] == '"sssh&"'
        return 'oauth_token_secret=1234&oauth_token=abcd'
    elif command_path == '/1/oauth/access_token':
        assert oauth_headers['oauth_consumer_key'] == '"1234"'
        assert oauth_headers['oauth_signature'] == '"sssh&1234"'
        return 'oauth_token_secret=blahblahsecret&oauth_token=cafesilvousplait'
    else:
        return '404 Not Found'


class TestDropbox(TestController):
    """
    Tests dropbox api
    """

    def __init__(self, *args, **kwargs):
        """
        Set up the environment
        """
        super(TestDropbox, self).__init__(*args, **kwargs)
        # Monkey-patch the controller as to be us who answer :)
        DropboxConnector._make_call = _mocked_dropbox_make_call

    def setUp(self):
        # Inject a Dropbox app
        cs = CloudStorage(
                storage_name='DROPBOX',
                app_key='1234',
                app_secret='sssh',
                service_api_url='https://api.dropbox.com'
        )
        Session.merge(cs)
        Session.commit()

        self.setup_gridsite_environment()

    def tearDown(self):
        Session.query(CloudStorageUser).delete()
        Session.query(CloudStorage).delete()
        Session.commit()

    def test_loaded(self):
        """
        Just test if the Dropbox plugin has been loaded
        Should be, in a development environment!
        """
        is_registered = self.app.get(url="/cs/registered/dropbox", status=200).json
        self.assertFalse(is_registered)

    def test_request_access(self):
        """
        Request a 'request' token
        """
        self.app.get(url="/cs/access_request/dropbox", status=404)

        response = self.app.get(url="/cs/access_request/dropbox/request", status=200)
        self.assertEqual('oauth_token_secret=1234&oauth_token=abcd', response.body)

        csu = Session.query(CloudStorageUser).get(('/DC=ch/DC=cern/CN=Test User', 'DROPBOX', ''))
        self.assertTrue(csu is not None)
        self.assertEqual('abcd', csu.request_token)
        self.assertEqual('1234', csu.request_token_secret)

    def test_access_granted_no_request(self):
        """
        Access grant without a request must fail
        """
        self.app.get(url="/cs/access_grant/dropbox", status=400)

    def test_access_granted(self):
        """
        Get a request token and grant access
        """
        self.test_request_access()
        self.app.get(url="/cs/access_grant/dropbox", status=200)

        csu = Session.query(CloudStorageUser).get(('/DC=ch/DC=cern/CN=Test User', 'DROPBOX', ''))
        self.assertTrue(csu is not None)
        self.assertEqual('cafesilvousplait', csu.access_token)
        self.assertEqual('blahblahsecret', csu.access_token_secret)

    def test_delete_token(self):
        """
        Remove the stored token
        """
        self.test_access_granted()
        self.app.delete(url="/cs/access_grant/dropbox", status=204)

        csu = Session.query(CloudStorageUser).get(('/DC=ch/DC=cern/CN=Test User', 'DROPBOX', ''))
        self.assertTrue(csu is None)

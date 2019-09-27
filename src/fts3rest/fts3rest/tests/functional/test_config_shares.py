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
from fts3rest.lib.base import Session
from fts3.model.config import ConfigAudit, ServerConfig, OperationConfig, ShareConfig

class TestConfigShares(TestController):

    def setUp(self):
        super(TestConfigShares, self).setUp()
        self.setup_gridsite_environment()
        Session.query(ServerConfig).delete()
        Session.query(ConfigAudit).delete()
        Session.query(OperationConfig).delete()
        Session.commit()

    def test_set_share(self):
        """
        Set up shares config
        """
        self.app.post_json(url="/config/shares",
                           params=dict(
                               source='gsiftp://source',
                               destination='gsiftp://nowhere',
                               vo='dteam',
                               share=80
                           ),
                           status=200
                           )

    def test_wrong_config_shares0(self):
        """
        Test wrong value for share in params
        """
        self.app.post_json(url="/config/shares",
                           params=dict(
                               source='gsiftp://source',
                               destination='gsiftp://nowhere',
                               vo='dteam',
                               share='dfdf'
                           ),
                           status=400
                           )

    def test_wrong_config_shares1(self):
        """
        Test missing one of params
        """
        config = {'source': 'gsiftp://source', 'destination': 'gsiftp://nowhere', 'vo': 'dteam', 'share': 80}

        for i in config:
            k = config
            k[i] = ''
            print k
            self.app.post_json(url="/config/shares", params=k, status=400)
            return config

    def test_wrong_config_shares2(self):
        """
        Test wrong source or destination
        """
        self.app.post_json(url="/config/shares",
                           params=dict(
                               source='dfgsdfsg',
                               destination='gsiftp://nowhere',
                               vo='dteam',
                               share=80
                           ),
                           status=400
                           )

        self.app.post_json(url="/config/shares",
                           params=dict(
                               source='gsiftp://source',
                               destination='klhjkhjk',
                               vo='dteam',
                               share=80
                           ),
                           status=400
                           )

    def test_get_share_config(self):
        """
        Get shares config
        """
        self.test_set_share()
        self.app.get(url="/config/shares", status=200)

    def test_remove_share(self):
        """
        Try to remove shares
        """
        self.app.delete(url="/config/shares?share=80&destination=gsiftp://nowhere&vo=dteam", status=400)
        self.app.delete(url="/config/shares?share=80&destination=gsiftp://nowhere&vo=dteam&source=gsiftp://source", status=204)

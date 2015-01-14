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
from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import ConfigAudit, AuthorizationByDn


class TestConfigAuthz(TestController):

    def setUp(self):
        super(TestConfigAuthz, self).setUp()
        self.setup_gridsite_environment()
        Session.query(AuthorizationByDn).delete()
        Session.query(ConfigAudit).delete()
        Session.commit()

    def test_add_authz(self):
        """
        Add a new operation for a new dn
        """
        self.app.post_json("/config/authorize", params={
            'dn': '/DN=a.test.user',
            'operation': 'config'
        }, status=200)

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(1, len(audits))

        authz = Session.query(AuthorizationByDn).get(('/DN=a.test.user', 'config'))
        self.assertIsNotNone(authz)

    def test_remove_authz(self):
        """
        Remove a operation for a dn
        """
        self.test_add_authz()
        self.app.delete("/config/authorize?dn=/DN=a.test.user&operation=config",
            status = 204
        )

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(2, len(audits))

        authz = Session.query(AuthorizationByDn).get(('/DN=a.test.user', 'config'))
        self.assertEqual(None, authz)

    def test_list_authz(self):
        """
        List special authorizations
        """
        self.test_add_authz()
        response = self.app.get("/config/authorize", status=200)
        authz = json.loads(response.body)

        self.assertEqual(1, len(authz))
        self.assertEqual(authz[0]['dn'], '/DN=a.test.user')
        self.assertEqual(authz[0]['operation'], 'config')

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

import unittest
from fts3rest.lib.middleware import fts3auth
from fts3rest.lib.base import Session
from fts3.model import AuthorizationByDn
from webob.exc import HTTPForbidden


class TestAuthorization(unittest.TestCase):
    """
    Tests for the authorization code.
    The environment is initialized with the DN and FQANS bellow,
    and uses the configuration specified by ROLES.
    """
    DN = '/DC=ch/DC=cern/CN=Test User'
    FQANS = ['/testvo/Role=NULL/Capability=NULL',
             '/testvo/group/Role=NULL/Capability=NULL',
             '/testvo/Role=myrole/Capability=NULL']

    # Any user can handle his/her own transfers, and vo transfers
    # Any user can delegate
    # No user can run configuration actions
    ROLES = {
             'public': {'transfer': 'vo', 'deleg': 'all'}
            }

    def setUp(self):
        env = dict()
        env['GRST_CRED_AURI_0'] = 'dn:' + TestAuthorization.DN
        env['GRST_CRED_AURI_1'] = 'fqan:' + TestAuthorization.FQANS[0]
        env['GRST_CRED_AURI_2'] = 'fqan:' + TestAuthorization.FQANS[1]
        env['GRST_CRED_AURI_3'] = 'fqan:' + TestAuthorization.FQANS[2]

        self.creds = fts3auth.UserCredentials(env, TestAuthorization.ROLES)

        env['fts3.User.Credentials'] = self.creds
        self.env = env

    def tearDown(self):
        Session.query(AuthorizationByDn).delete()

    def test_authorized_base(self):
        """
        Try to perform an action that is not configured (must be denied), and another
        one that is allowed for everyone
        """
        self.assertFalse(fts3auth.authorized(fts3auth.CONFIG, env = self.env))
        self.assertTrue(fts3auth.authorized(fts3auth.DELEGATION, env = self.env))

    def test_authorized_vo(self):
        """
        Try to perform an action that is allowed only for users belonging to the same
        vo as the resource
        """
        # The user is the owner, so it must be allowed
        self.assertTrue(fts3auth.authorized(fts3auth.TRANSFER,
                                            resource_owner = TestAuthorization.DN, env = self.env))
        # The user belongs to the same vo, and transfer is set to vo, so it
        # must be allowed
        self.assertTrue(fts3auth.authorized(fts3auth.TRANSFER,
                                            resource_owner = 'someone', resource_vo = 'testvo',
                                            env = self.env))
        # The resource belongs to a different user and vo, so it must
        # be forbidden
        self.assertFalse(fts3auth.authorized(fts3auth.TRANSFER,
                                             resource_owner = 'someone', resource_vo = 'othervo',
                                             env = self.env))

    def test_authorized_all(self):
        """
        Try to perform an action that is configured to be executed by anyone (all)
        """
        self.assertTrue(fts3auth.authorized(fts3auth.DELEGATION,
                                            resource_owner = TestAuthorization.DN, env = self.env))
        self.assertTrue(fts3auth.authorized(fts3auth.DELEGATION,
                                            resource_owner = 'someone', resource_vo = 'testvo',
                                            env = self.env))
        self.assertTrue(fts3auth.authorized(fts3auth.DELEGATION,
                                            resource_owner = 'someone', resource_vo = 'othervo',
                                            env = self.env))

    def test_authorize_decorator(self):
        """
        Make sure the decorators work
        """
        @fts3auth.authorize(fts3auth.TRANSFER, env = self.env)
        def func_allowed(a, b):
            return a == b

        @fts3auth.authorize(fts3auth.CONFIG, env = self.env)
        def func_forbidden(a, b):
            return a != b

        self.assertTrue(func_allowed(1, 1))
        self.assertRaises(HTTPForbidden, func_forbidden, 0, 1)

    def test_authorize_config_via_db(self):
        """
        Credentials with no vo extensions, if the DN is in the database as authorized,
        configuration should be allowed
        """
        del self.creds
        del self.env['fts3.User.Credentials']

        env = dict(GRST_CRED_AURI_0='dn:' + TestAuthorization.DN)
        self.creds = fts3auth.UserCredentials(env, TestAuthorization.ROLES)
        self.env['fts3.User.Credentials'] = self.creds

        self.assertFalse(fts3auth.authorized(fts3auth.CONFIG, env = self.env))

        authz = AuthorizationByDn(dn=TestAuthorization.DN, operation=fts3auth.CONFIG)
        Session.merge(authz)
        Session.commit()

        self.assertTrue(fts3auth.authorized(fts3auth.CONFIG, env = self.env))

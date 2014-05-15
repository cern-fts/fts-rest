#!/usr/bin/env python

#   Copyright notice:
#   Copyright © Members of the EMI Collaboration, 2010.
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

from fts3rest.lib.middleware import fts3auth
import unittest


class TestUserCredentials(unittest.TestCase):
    """
    Given a set of Gridsite environment variables, check the user
    credentials are being set correctly.
    """
    DN = '/DC=ch/DC=cern/CN=Test User'
    FQANS = ['/testvo/Role=NULL/Capability=NULL',
             '/testvo/group/Role=NULL/Capability=NULL',
             '/testvo/Role=myrole/Capability=NULL',
             '/testvo/Role=admin/Capability=NULL']

    ROLES = {
             'public': {'transfer': 'vo', 'deleg': ''},
             'admin': {'config': 'all'}
            }

    def test_basic_ssl(self):
        """
        Plain mod_ssl must work. No VO, though.
        """
        creds = fts3auth.UserCredentials({'SSL_CLIENT_S_DN': TestUserCredentials.DN})

        self.assertEqual(TestUserCredentials.DN, creds.user_dn)
        self.assertEqual([], creds.voms_cred)
        self.assertEqual(['TestUser@cern.ch'], creds.vos)


    def test_gridsite(self):
        """
        Set environment as mod_gridsite would do, and check the vos,
        roles and so on are set up properly.
        """
        env = {}
        env['GRST_CRED_AURI_0'] = 'dn:' + TestUserCredentials.DN
        env['GRST_CRED_AURI_1'] = 'fqan:' + TestUserCredentials.FQANS[0]
        env['GRST_CRED_AURI_2'] = 'fqan:' + TestUserCredentials.FQANS[1]
        env['GRST_CRED_AURI_3'] = 'fqan:' + TestUserCredentials.FQANS[2]
        env['GRST_CRED_AURI_4'] = 'fqan:' + TestUserCredentials.FQANS[3]

        creds = fts3auth.UserCredentials(env)

        self.assertEqual(TestUserCredentials.DN, creds.user_dn)
        self.assertEqual(['testvo', 'testvo/group'], creds.vos)
        self.assertEqual(TestUserCredentials.FQANS, creds.voms_cred)

        self.assertEqual(['myrole', 'admin'], creds.roles)


    def test_default_roles(self):
        """
        Set environment as mod_gridsite would do, but with no roles
        present.
        """
        env = {}
        env['GRST_CRED_AURI_0'] = 'dn:' + TestUserCredentials.DN
        env['GRST_CRED_AURI_1'] = 'fqan:' + TestUserCredentials.FQANS[0]

        creds = fts3auth.UserCredentials(env, TestUserCredentials.ROLES)

        self.assertEqual(fts3auth.VO,      creds.get_granted_level_for(fts3auth.TRANSFER))
        self.assertEqual(fts3auth.PRIVATE, creds.get_granted_level_for(fts3auth.DELEGATION))
        self.assertEqual(fts3auth.NONE,    creds.get_granted_level_for(fts3auth.CONFIG))


    def test_roles(self):
        """
        Set environment as mod_gridsite would do, and then check that
        the granted levels are set up properly.
        """
        env = {}
        env['GRST_CRED_AURI_0'] = 'dn:' + TestUserCredentials.DN
        env['GRST_CRED_AURI_1'] = 'fqan:' + TestUserCredentials.FQANS[0]
        env['GRST_CRED_AURI_2'] = 'fqan:' + TestUserCredentials.FQANS[1]
        env['GRST_CRED_AURI_3'] = 'fqan:' + TestUserCredentials.FQANS[2]
        env['GRST_CRED_AURI_4'] = 'fqan:' + TestUserCredentials.FQANS[3]

        creds = fts3auth.UserCredentials(env, TestUserCredentials.ROLES)

        self.assertEqual(fts3auth.ALL,     creds.get_granted_level_for(fts3auth.CONFIG))
        self.assertEqual(fts3auth.VO,      creds.get_granted_level_for(fts3auth.TRANSFER))
        self.assertEqual(fts3auth.PRIVATE, creds.get_granted_level_for(fts3auth.DELEGATION))

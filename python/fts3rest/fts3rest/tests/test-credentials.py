#!/usr/bin/env python
import common
from fts3rest.lib.credentials import UserCredentials
import unittest



class TestUserCredentials(unittest.TestCase):
    DN    = '/DC=ch/DC=cern/OU=Test User'
    FQANS = ['/testvo/Role=NULL/Capability=NULL',
             '/testvo/group/Role=NULL/Capability=NULL',
             '/testvo/Role=myrole/Capability=NULL',
             '/testvo/Role=admin/Capability=NULL']
    
    def test_basic_ssl(self):
        creds = UserCredentials({'SSL_CLIENT_S_DN': TestUserCredentials.DN})
        
        self.assertEqual(TestUserCredentials.DN, creds.user_dn)
        self.assertListEqual([], creds.voms_cred)
        self.assertListEqual([], creds.vos)



    def test_gridsite(self):
        env = {}
        env['GRST_CRED_AURI_0'] = 'dn:' + TestUserCredentials.DN
        env['GRST_CRED_AURI_1'] = 'fqan:' + TestUserCredentials.FQANS[0]
        env['GRST_CRED_AURI_2'] = 'fqan:' + TestUserCredentials.FQANS[1]
        env['GRST_CRED_AURI_3'] = 'fqan:' + TestUserCredentials.FQANS[2]
        env['GRST_CRED_AURI_4'] = 'fqan:' + TestUserCredentials.FQANS[3]
        
        creds = UserCredentials(env)
        
        self.assertEqual(TestUserCredentials.DN, creds.user_dn)
        self.assertListEqual(['testvo', 'testvo/group'], creds.vos)
        self.assertListEqual(TestUserCredentials.FQANS, creds.voms_cred)
        
        self.assertListEqual(['myrole', 'admin'], creds.roles)


if __name__ == '__main__':
    unittest.main()

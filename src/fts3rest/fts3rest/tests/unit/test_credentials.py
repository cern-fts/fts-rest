#!/usr/bin/env python
from fts3rest.lib.middleware import fts3auth
import unittest



class TestUserCredentials(unittest.TestCase):
    DN = '/DC=ch/DC=cern/OU=Test User'
    FQANS = ['/testvo/Role=NULL/Capability=NULL',
             '/testvo/group/Role=NULL/Capability=NULL',
             '/testvo/Role=myrole/Capability=NULL',
             '/testvo/Role=admin/Capability=NULL']
    
    ROLES = {
             'public': {'transfer': 'vo', 'deleg': ''},
             'admin': {'config': 'all'}
            }
    
    def test_basic_ssl(self):
        creds = fts3auth.UserCredentials({'SSL_CLIENT_S_DN': TestUserCredentials.DN})
        
        self.assertEqual(TestUserCredentials.DN, creds.user_dn)
        self.assertEqual([], creds.voms_cred)
        self.assertEqual([], creds.vos)


    def test_gridsite(self):
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
        env = {}
        env['GRST_CRED_AURI_0'] = 'dn:' + TestUserCredentials.DN
        env['GRST_CRED_AURI_1'] = 'fqan:' + TestUserCredentials.FQANS[0]
        
        creds = fts3auth.UserCredentials(env, TestUserCredentials.ROLES)
        
        self.assertEqual(fts3auth.VO,      creds.getGrantedLevelFor(fts3auth.TRANSFER))
        self.assertEqual(fts3auth.PRIVATE, creds.getGrantedLevelFor(fts3auth.DELEGATION))
        self.assertEqual(fts3auth.NONE,    creds.getGrantedLevelFor(fts3auth.CONFIG))


    def test_roles(self):
        env = {}
        env['GRST_CRED_AURI_0'] = 'dn:' + TestUserCredentials.DN
        env['GRST_CRED_AURI_1'] = 'fqan:' + TestUserCredentials.FQANS[0]
        env['GRST_CRED_AURI_2'] = 'fqan:' + TestUserCredentials.FQANS[1]
        env['GRST_CRED_AURI_3'] = 'fqan:' + TestUserCredentials.FQANS[2]
        env['GRST_CRED_AURI_4'] = 'fqan:' + TestUserCredentials.FQANS[3]
        
        creds = fts3auth.UserCredentials(env, TestUserCredentials.ROLES)
        
        self.assertEqual(fts3auth.ALL,     creds.getGrantedLevelFor(fts3auth.CONFIG))
        self.assertEqual(fts3auth.VO,      creds.getGrantedLevelFor(fts3auth.TRANSFER))
        self.assertEqual(fts3auth.PRIVATE, creds.getGrantedLevelFor(fts3auth.DELEGATION))

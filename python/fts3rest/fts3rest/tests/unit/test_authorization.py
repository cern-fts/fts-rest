import unittest
from fts3rest.lib.middleware import fts3auth
from webob.exc import HTTPForbidden


class TestAuthorization(unittest.TestCase):
	DN = '/DC=ch/DC=cern/OU=Test User'
	FQANS = ['/testvo/Role=NULL/Capability=NULL',
			 '/testvo/group/Role=NULL/Capability=NULL',
			 '/testvo/Role=myrole/Capability=NULL']
	
	ROLES = {
			 'public': {'transfer': 'vo', 'deleg': 'all'}
			}
	
	def setUp(self):
		env = {}
		env['GRST_CRED_AURI_0'] = 'dn:' + TestAuthorization.DN
		env['GRST_CRED_AURI_1'] = 'fqan:' + TestAuthorization.FQANS[0]
		env['GRST_CRED_AURI_2'] = 'fqan:' + TestAuthorization.FQANS[1]
		env['GRST_CRED_AURI_3'] = 'fqan:' + TestAuthorization.FQANS[2]
        
		self.creds = fts3auth.UserCredentials(env, TestAuthorization.ROLES)
		
		env['fts3.User.Credentials'] = self.creds
		self.env = env


	def test_authorized_base(self):
		self.assertFalse(fts3auth.authorized(fts3auth.CONFIG, env = self.env))
		self.assertTrue(fts3auth.authorized(fts3auth.DELEGATION, env = self.env))


	def test_authorized_vo(self):
		self.assertTrue(fts3auth.authorized(fts3auth.TRANSFER,
										    resource_owner = TestAuthorization.DN, env = self.env))
		
		self.assertTrue(fts3auth.authorized(fts3auth.TRANSFER,
										    resource_owner = 'someone', resource_vo = 'testvo',
										    env = self.env))
		
		self.assertFalse(fts3auth.authorized(fts3auth.TRANSFER,
										     resource_owner = 'someone', resource_vo = 'othervo',
										     env = self.env))
		
	def test_authorized_all(self):
		self.assertTrue(fts3auth.authorized(fts3auth.DELEGATION,
										    resource_owner = TestAuthorization.DN, env = self.env))
		
		self.assertTrue(fts3auth.authorized(fts3auth.DELEGATION,
										    resource_owner = 'someone', resource_vo = 'testvo',
										    env = self.env))
		
		self.assertTrue(fts3auth.authorized(fts3auth.DELEGATION,
										    resource_owner = 'someone', resource_vo = 'othervo',
									        env = self.env))



	def test_authorize_decorator(self):
		@fts3auth.authorize(fts3auth.TRANSFER, env = self.env)
		def func_allowed(a, b):
			return a == b
		
		@fts3auth.authorize(fts3auth.CONFIG, env = self.env)
		def func_forbidden(a, b):
			return a != b
		
		self.assertTrue(func_allowed(1, 1))
		
		self.assertRaises(HTTPForbidden, func_forbidden, 0, 1)

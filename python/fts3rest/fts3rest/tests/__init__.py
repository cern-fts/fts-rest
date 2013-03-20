"""Pylons application test package

This package assumes the Pylons environment is already loaded, such as
when this script is imported from the `nosetests --with-pylons=test.ini`
command.

This module initializes the application via ``websetup`` (`paster
setup-app`) and provides the base testing objects.
"""
from datetime import datetime, timedelta
from unittest import TestCase

from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from pylons import url
from routes.util import URLGenerator
from webtest import TestApp

import pylons.test

from fts3rest.lib.middleware import fts3auth
from fts3rest.lib.base import Session
from fts3.model import Credential

__all__ = ['environ', 'url', 'TestController']

# Invoke websetup with the current config file
SetupCommand('setup-app').run([pylons.test.pylonsapp.config['__file__']])

environ = {}

class TestController(TestCase):

	def __init__(self, *args, **kwargs):
		wsgiapp = pylons.test.pylonsapp
		config = wsgiapp.config
		self.app = TestApp(wsgiapp)
		url._push_object(URLGenerator(config['routes.map'], environ))
		TestCase.__init__(self, *args, **kwargs)


	def setupGridsiteEnvironment(self):
		env = {'GRST_CRED_AURI_0': 'dn:/DC=ch/DC=cern/OU=Test User',
			   'GRST_CRED_AURI_1': 'fqan:/testvo/Role=NULL/Capability=NULL',
			   'GRST_CRED_AURI_2': 'fqan:/testvo/Role=myrole/Capability=NULL'
			  }
		self.app.extra_environ.update(env)


	def getUserCredentials(self):
		return fts3auth.UserCredentials(self.app.extra_environ, {'public': {'*': 'all'}})

	def pushDelegation(self, lifetime = timedelta(hours = 7)):
		creds = self.getUserCredentials()
		delegated = Credential()
		delegated.dlg_id     = creds.delegation_id
		delegated.dn         = creds.user_dn
		delegated.proxy      = '-NOT USED-'
		delegated.voms_attrs = None
		delegated.termination_time = datetime.now() + lifetime
		
		Session.merge(delegated)
		Session.commit()
		
	
	def popDelegation(self):
		cred = self.getUserCredentials()
		if cred and cred.delegation_id:
			delegated = Session.query(Credential).get((cred.delegation_id, cred.user_dn))
			if delegated:
				Session.delete(delegated)
				Session.commit()
	
	def tearDown(self):
		self.popDelegation()

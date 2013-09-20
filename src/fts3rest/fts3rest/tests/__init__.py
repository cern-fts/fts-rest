"""Pylons application test package

This package assumes the Pylons environment is already loaded, such as
when this script is imported from the `nosetests --with-pylons=test.ini`
command.

This module initializes the application via ``websetup`` (`paster
setup-app`) and provides the base testing objects.
"""
import time

from datetime import datetime, timedelta
from unittest import TestCase
from M2Crypto import ASN1, X509, RSA, EVP, BIO

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
        self.x509_proxy = None

    def setupGridsiteEnvironment(self, noVo=False):
        env = {'GRST_CRED_AURI_0': 'dn:/DC=ch/DC=cern/OU=Test User'}

        if not noVo:
            env.update({
               'GRST_CRED_AURI_1': 'fqan:/testvo/Role=NULL/Capability=NULL',
               'GRST_CRED_AURI_2': 'fqan:/testvo/Role=myrole/Capability=NULL'
              })
        self.app.extra_environ.update(env)

    def getUserCredentials(self):
        return fts3auth.UserCredentials(self.app.extra_environ, {'public': {'*': 'all'}})

    def pushDelegation(self, lifetime=timedelta(hours=7)):
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

    def _populatedName(self, components):
        x509Name = X509.X509_Name()
        for (field, value) in components:
            x509Name.add_entry_by_txt(field, 0x1000, value,
                                      len=-1, loc=-1, set=0)
        return x509Name

    def _generateX509Proxy(self, subject):
        # Public key
        key = RSA.gen_key(512, 65537)
        pkey = EVP.PKey()
        pkey.assign_rsa(key)
        # Expiration
        start = ASN1.ASN1_UTCTIME()
        start.set_time(int(time.time()))
        expire = ASN1.ASN1_UTCTIME()
        expire.set_time(int(time.time()) + 60 * 60)
        # Certificate
        cert = X509.X509()
        cert.set_pubkey(pkey)
        name = self._populatedName(subject)
        cert.set_subject(name)
        cert.set_issuer_name(name)
        cert.set_not_before(start)
        cert.set_not_after(expire)
        # Sign
        cert.sign(pkey, md='md5')
        # Create a string concatenating both
        proxy = cert.as_pem()
        proxy += pkey.as_pem(None)
        return proxy

    def getX509Proxy(self, subject=
                    [('DC', 'ch'), ('DC', 'cern'), ('OU', 'Test User'), ('CN', 'proxy')]):
        if not self.x509_proxy:
            self.x509_proxy = self._generateX509Proxy(subject)
        return self.x509_proxy

    def tearDown(self):
        self.popDelegation()

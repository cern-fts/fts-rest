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
from M2Crypto import ASN1, X509, RSA, EVP, BIO, m2
import os

from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from pylons import url
from routes.util import URLGenerator
from webtest import TestApp

import pylons.test
import pytz

from fts3rest.lib.middleware import fts3auth
from fts3rest.lib.base import Session
from fts3.model import Credential


__all__ = ['environ', 'url', 'TestController']

# Invoke websetup with the current config file
SetupCommand('setup-app').run([pylons.test.pylonsapp.config['__file__']])

environ = {}


class TestController(TestCase):
    """
    Base class for the tests
    """

    def __init__(self, *args, **kwargs):
        wsgiapp = pylons.test.pylonsapp
        config = wsgiapp.config
        self.app = TestApp(wsgiapp)
        url._push_object(URLGenerator(config['routes.map'], environ))
        TestCase.__init__(self, *args, **kwargs)
        
        key = RSA.gen_key(512, 65537)
        self.pkey = EVP.PKey()
        self.pkey.assign_rsa(key)


    def setupGridsiteEnvironment(self, noVo=False):
        """
        Add to the test environment mock values of the variables
        set by mod_gridsite.
        
        Args:
            noVo: If True, no VO attributes will be set
        """
        env = {'GRST_CRED_AURI_0': 'dn:/DC=ch/DC=cern/OU=Test User'}

        if not noVo:
            env.update({
               'GRST_CRED_AURI_1': 'fqan:/testvo/Role=NULL/Capability=NULL',
               'GRST_CRED_AURI_2': 'fqan:/testvo/Role=myrole/Capability=NULL'
              })
        self.app.extra_environ.update(env)

    def getUserCredentials(self):
        """
        Get the user credentials from the environment
        """
        return fts3auth.UserCredentials(self.app.extra_environ, {'public': {'*': 'all'}})

    def pushDelegation(self, lifetime=timedelta(hours=7)):
        """
        Push into the database a mock delegated credential
        
        Args:
            lifetime: The mock credential lifetime
        """
        creds = self.getUserCredentials()
        delegated = Credential()
        delegated.dlg_id     = creds.delegation_id
        delegated.dn         = creds.user_dn
        delegated.proxy      = '-NOT USED-'
        delegated.voms_attrs = None
        delegated.termination_time = datetime.utcnow() + lifetime

        Session.merge(delegated)
        Session.commit()

    def popDelegation(self):
        """
        Remove the mock proxy from the database
        """
        cred = self.getUserCredentials()
        if cred and cred.delegation_id:
            delegated = Session.query(Credential).get((cred.delegation_id, cred.user_dn))
            if delegated:
                Session.delete(delegated)
                Session.commit()

    def getX509Proxy(self, requestPEM,
                     issuer = [('DC', 'ch'), ('DC', 'cern'), ('OU', 'Test User')],
                     subject = None,
                     private_key = None):
        """
        Generate a X509 proxy based on the request

        Args:
            requestPEM: The request PEM encoded
            issuer:     The issuer user
            subject:    The subject of the proxy. If None, issuer/CN=proxy will be  used

        Returns:
            A X509 proxy PEM encoded
        """
        if subject is None:
            subject = issuer + [('CN', 'proxy')]
            
        x509Request = X509.load_request_string(str(requestPEM))
        
        notBefore = ASN1.ASN1_UTCTIME()
        notBefore.set_datetime(datetime.now(pytz.UTC))
        notAfter = ASN1.ASN1_UTCTIME()
        notAfter.set_datetime(datetime.now(pytz.UTC) + timedelta(hours = 3))

        issuerSubject = X509.X509_Name()
        for c in issuer:
            issuerSubject.add_entry_by_txt(c[0], 0x1000, c[1], -1, -1, 0)
        
        proxySubject = X509.X509_Name()
        for c in subject:
            proxySubject.add_entry_by_txt(c[0], 0x1000, c[1], -1, -1, 0)

        proxy = X509.X509()
        proxy.set_version(2)
        proxy.set_subject(proxySubject)
        proxy.set_serial_number(long(time.time()))
        proxy.set_version(x509Request.get_version())
        proxy.set_issuer(issuerSubject)
        proxy.set_pubkey(x509Request.get_pubkey())

        proxy.set_not_after(notAfter)
        proxy.set_not_before(notBefore)

        if not private_key:
            proxy.sign(self.pkey, 'sha1')
        else:
            proxy.sign(private_key, 'sha1')

        return proxy.as_pem()

    def getRealX509Proxy(self):
        """
        Get a real X509 proxy

        Returns:
            The content of the file pointed by X509_USER_PROXY,
            None otherwise
        """
        proxy_path = os.environ.get('X509_USER_PROXY', None)
        if not proxy_path:
            return None
        return open(proxy_path).read()

    def tearDown(self):
        """
        Called by the test framework at the end of each test
        """
        self.popDelegation()

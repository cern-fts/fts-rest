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

"""Pylons application test package

This package assumes the Pylons environment is already loaded, such as
when this script is imported from the `nosetests --with-pylons=test.ini`
command.

This module initializes the application via ``websetup`` (`paster
setup-app`) and provides the base testing objects.
"""
import os
import pylons.test
import time

from datetime import datetime, timedelta
from unittest import TestCase
from M2Crypto import ASN1, X509, RSA, EVP
from M2Crypto.ASN1 import UTC
from paste.script.appinstall import SetupCommand
from pylons import url
from routes.util import URLGenerator
from webtest import TestApp

from fts3rest.lib.middleware import fts3auth
from fts3rest.lib.base import Session
from fts3.model import Credential, CredentialCache, Job, File, FileRetryLog, OptimizerActive


__all__ = ['environ', 'url', 'TestController']

# Invoke websetup with the current config file
#SetupCommand('setup-app').run([pylons.test.pylonsapp.config['__file__']])

environ = {}


def _generate_mock_cert():
    rsa_key = RSA.gen_key(512, 65537)
    pkey = EVP.PKey()
    pkey.assign_rsa(rsa_key)

    cert = X509.X509()
    cert.set_pubkey(pkey)
    not_before = ASN1.ASN1_UTCTIME()
    not_before.set_datetime(datetime.now(UTC))
    not_after = ASN1.ASN1_UTCTIME()
    not_after.set_datetime(datetime.now(UTC) + timedelta(hours=24))
    cert.set_not_before(not_before)
    cert.set_not_after(not_after)
    cert.sign(pkey, 'md5')

    return pkey, cert


class TestController(TestCase):
    """
    Base class for the tests
    """

    TEST_USER_DN = '/DC=ch/DC=cern/CN=Test User'

    def __init__(self, *args, **kwargs):
        wsgiapp = pylons.test.pylonsapp
        config = wsgiapp.config
        self.app = TestApp(wsgiapp)
        url._push_object(URLGenerator(config['routes.map'], environ))
        TestCase.__init__(self, *args, **kwargs)

        self.pkey, self.cert = _generate_mock_cert()

    def setup_gridsite_environment(self, no_vo=False):
        """
        Add to the test environment mock values of the variables
        set by mod_gridsite.

        Args:
            noVo: If True, no VO attributes will be set
        """
        env = {'GRST_CRED_AURI_0': 'dn:' + TestController.TEST_USER_DN}

        if not no_vo:
            env.update({
                'GRST_CRED_AURI_1': 'fqan:/testvo/Role=NULL/Capability=NULL',
                'GRST_CRED_AURI_2': 'fqan:/testvo/Role=myrole/Capability=NULL'
            })
        self.app.extra_environ.update(env)

    def get_user_credentials(self):
        """
        Get the user credentials from the environment
        """
        return fts3auth.UserCredentials(self.app.extra_environ, {'public': {'*': 'all'}})

    def push_delegation(self, lifetime=timedelta(hours=7)):
        """
        Push into the database a mock delegated credential

        Args:
            lifetime: The mock credential lifetime
        """
        creds = self.get_user_credentials()
        delegated = Credential()
        delegated.dlg_id     = creds.delegation_id
        delegated.dn         = creds.user_dn
        delegated.proxy      = '-NOT USED-'
        delegated.voms_attrs = None
        delegated.termination_time = datetime.utcnow() + lifetime

        Session.merge(delegated)
        Session.commit()

    def pop_delegation(self):
        """
        Remove the mock proxy from the database
        """
        cred = self.get_user_credentials()
        if cred and cred.delegation_id:
            delegated = Session.query(Credential).get((cred.delegation_id, cred.user_dn))
            if delegated:
                Session.delete(delegated)
                Session.commit()

    def get_x509_proxy(self, request_pem, issuer=None, subject=None, private_key=None):
        """
        Generate a X509 proxy based on the request

        Args:
            requestPEM: The request PEM encoded
            issuer:     The issuer user
            subject:    The subject of the proxy. If None, issuer/CN=proxy will be  used

        Returns:
            A X509 proxy PEM encoded
        """
        if issuer is None:
            issuer = [('DC', 'ch'), ('DC', 'cern'), ('CN', 'Test User')]
        if subject is None:
            subject = issuer + [('CN', 'proxy')]

        x509_request = X509.load_request_string(str(request_pem))

        not_before = ASN1.ASN1_UTCTIME()
        not_before.set_datetime(datetime.now(UTC))
        not_after = ASN1.ASN1_UTCTIME()
        not_after.set_datetime(datetime.now(UTC) + timedelta(hours=3))

        issuer_subject = X509.X509_Name()
        for c in issuer:
            issuer_subject.add_entry_by_txt(c[0], 0x1000, c[1], -1, -1, 0)

        proxy_subject = X509.X509_Name()
        for c in subject:
            proxy_subject.add_entry_by_txt(c[0], 0x1000, c[1], -1, -1, 0)

        proxy = X509.X509()
        proxy.set_version(2)
        proxy.set_subject(proxy_subject)
        proxy.set_serial_number(int(time.time()))
        proxy.set_version(x509_request.get_version())
        proxy.set_issuer(issuer_subject)
        proxy.set_pubkey(x509_request.get_pubkey())

        proxy.set_not_after(not_after)
        proxy.set_not_before(not_before)

        if not private_key:
            proxy.sign(self.pkey, 'sha1')
        else:
            proxy.sign(private_key, 'sha1')

        return proxy.as_pem() + self.cert.as_pem()

    def get_real_x509_proxy(self):
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
        Session.query(Credential).delete()
        Session.query(CredentialCache).delete()
        Session.query(FileRetryLog).delete()
        Session.query(File).delete()
        Session.query(Job).delete()
        Session.query(OptimizerActive).delete()
        Session.commit()

    # Handy asserts not available in the EPEL-6 version
    def assertGreater(self, a, b):
        if not a > b:
            standardMsg = "%s not greater than %s" % (repr(a), repr(b))
            self.fail(standardMsg)

    def assertIn(self, member, container):
        if member not in container:
            standardMsg = "%s not in %s" % (member, str(container))
            self.fail(standardMsg)

    def assertNotIn(self, member, container):
        if member in container:
            standardMsg = "%s in %s" % (member, str(container))
            self.fail(standardMsg)

    def assertIsNotNone(self, obj):
        if obj is None:
            standardMsg = "Unexpected None"
            self.fail(standardMsg)

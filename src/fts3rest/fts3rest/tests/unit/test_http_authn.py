#!/usr/bin/env python

#   Copyright notice:
#   Copyright CERN, 2016.
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

import M2Crypto
import hashlib
import os
import time
import unittest
from base64 import b64encode
from datetime import datetime, timedelta

from fts3rest.lib.middleware.fts3auth.methods.http import do_authentication, set_capath
from fts3rest.lib.middleware.fts3auth import UserCredentials, InvalidCredentials


def empty_callback():
    pass


class TestHttpAuthn(unittest.TestCase):
    """
    Authenticate the user based on a certificate sent via HTTP header.
    This method is used by WebFTS with on-the-fly cert generation.
    """

    SUBJECT = "/CN=fake fakeson"
    HASH = "e151403e"

    def _generate_subject(self):
        x509_name = M2Crypto.X509.X509_Name()
        x509_name.add_entry_by_txt(field='O', type=0x1001, entry='Fake LT', len=-1, loc=-1, set=-1)
        x509_name.add_entry_by_txt(field='CN', type=0x1001, entry='Fake Fakeson Jr.', len=-1, loc=-1, set=-1)
        return x509_name

    def _generate_cert(self, rsa):
        """
        Generate a certificate/private key on the fly
        """
        x509_name = self._generate_subject()
        self.pkey = M2Crypto.EVP.PKey()
        self.pkey.assign_rsa(rsa)
        cert = M2Crypto.X509.X509()
        cert.set_pubkey(self.pkey)
        cert.set_subject_name(x509_name)
        cert.set_issuer_name(x509_name)

        timestamp = M2Crypto.ASN1.ASN1_UTCTIME()
        timestamp.set_time(int(time.mktime(datetime.utcnow().utctimetuple())))
        cert.set_not_before(timestamp)
        timestamp.set_time(int(time.mktime((datetime.utcnow() + timedelta(hours=12)).utctimetuple())))
        cert.set_not_after(timestamp)

        cert.sign(self.pkey, 'sha256')

        return cert

    def _store_ca(self):
        """
        Store the generated cert as CA in /tmp, so we can get the implementation to correctly verify
        """
        path = os.path.join("/tmp", "%s.0" % self.HASH)
        open(path, 'w').write(self.cert.as_pem())
        return path

    def setUp(self):
        set_capath('/tmp')

        self.creds = UserCredentials(dict())
        self.key_pair = M2Crypto.RSA.gen_key(1024, 65537, empty_callback)
        self.cert = self._generate_cert(self.key_pair)
        self.ca_path = self._store_ca()

    def tearDown(self):
        if os.path.exists(self.ca_path):
            os.remove(self.ca_path)

    def _prepare_auth_values(self):
        """
        Prepare the values for the auth header
        """
        ts = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        b64cert = b64encode(self.cert.as_der())

        hash = hashlib.sha256()
        hash.update(self.cert.as_der())
        hash.update(ts)
        digest = hash.digest()

        signature = self.key_pair.sign(digest, 'sha256')

        return dict(
            hash='sha256',
            ts=ts,
            cert=b64cert,
            sign=b64encode(signature)
        )

    def _get_auth_header(self, values=None):
        """
        Build the Authorization header
        """
        if values is None:
            values = self._prepare_auth_values()
        return "Signed-Cert " + " ".join(map(lambda (k, v): "%s=\"%s\"" % (k, v), values.iteritems()))

    def test_http_authn(self):
        """
        Basic test. Valid certificate on the header.
        """
        ret = do_authentication(self.creds, dict(HTTP_AUTHORIZATION=self._get_auth_header()))
        self.assertTrue(ret)

    def test_http_missing(self):
        """
        Missing header
        """
        ret = do_authentication(self.creds, dict())
        self.assertFalse(ret)

    def test_http_bad_cert(self):
        """
        Bad certificate
        """
        values = self._prepare_auth_values()
        values["cert"] = "XXXX"
        self.assertRaises(
            InvalidCredentials,
            do_authentication, self.creds, dict(HTTP_AUTHORIZATION=self._get_auth_header(values))
        )

    def test_http_bad_signature(self):
        """
        Invalid signature
        """
        values = self._prepare_auth_values()

        hash = hashlib.sha256()
        hash.update("DIFFERENT THING HERE")
        hash.update(values["ts"])
        digest = hash.digest()

        values["sign"] = self.key_pair.sign(digest, 'sha256')

        self.assertRaises(
            InvalidCredentials,
            do_authentication, self.creds, dict(HTTP_AUTHORIZATION=self._get_auth_header(values))
        )

    def test_http_invalid_ca(self):
        """
        All good, but root CA is not installed
        """
        os.unlink(self.ca_path)
        self.assertRaises(
            InvalidCredentials,
            do_authentication, self.creds, dict(HTTP_AUTHORIZATION=self._get_auth_header())
        )
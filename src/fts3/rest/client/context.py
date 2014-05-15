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

from datetime import datetime
from M2Crypto import X509, RSA, EVP, BIO
from M2Crypto.ASN1 import UTC
import getpass
import json
import logging
import os
import sys

from exceptions import *
from request import RequestFactory

log = logging.getLogger(__name__)


# Return a list of certificates from the file
def _get_x509_list(cert):
    x509_list = []
    fd = BIO.openfile(cert, 'rb')
    cert = X509.load_cert_bio(fd)
    try:
        while True:
            x509_list.append(cert)
            log.debug("Loaded " + cert.get_subject().as_text())
            cert = X509.load_cert_bio(fd)
    except X509.X509Error:
        # When there are no more certs, this is what we get, so it is fine
        pass

    del fd
    return x509_list


# Base class for actors
class Context(object):

    def _read_passwd_from_stdin(self, *args, **kwargs):
        if not self.passwd:
            self.passwd = getpass.getpass('Private key password: ')
        return self.passwd

    def _set_x509(self, ucert, ukey):
        if not ukey:
            if ucert:
                ukey = ucert
            elif 'X509_USER_PROXY' in os.environ:
                ukey = os.environ['X509_USER_PROXY']
            elif 'X509_USER_KEY' in os.environ:
                ukey = os.environ['X509_USER_KEY']

        if not ucert:
            if 'X509_USER_PROXY' in os.environ:
                ucert = os.environ['X509_USER_PROXY']
            elif 'X509_USER_CERT' in os.environ:
                ucert = os.environ['X509_USER_CERT']

        if ucert and ukey:
            self.x509_list = _get_x509_list(ucert)
            self.x509 = self.x509_list[0]
            not_after = self.x509.get_not_after()
            if not_after.get_datetime() < datetime.now(UTC):
                raise Exception("Proxy expired!")

            try:
                self.rsa_key = RSA.load_key(ukey, self._read_passwd_from_stdin)
            except RSA.RSAError, e:
                raise RSA.RSAError("Could not load %s: %s" % (ukey, str(e)))
            except Exception, e:
                raise Exception("Could not load %s: %s" % (ukey, str(e)))

            self.evp_key = EVP.PKey()
            self.evp_key.assign_rsa(self.rsa_key)

            self.ucert = ucert
            self.ukey = ukey
        else:
            self.ucert = self.ukey = None

        if not self.ucert and not self.ukey:
            logging.warning("No user certificate given!")
        else:
            logging.debug("User certificte: %s" % self.ucert)
            logging.debug("User private key: %s" % self.ukey)

    def _set_endpoint(self, endpoint):
        self.endpoint = endpoint
        if self.endpoint.endswith('/'):
            self.endpoint = self.endpoint[:-1]

    def _validate_endpoint(self):
        try:
            endpoint_info = json.loads(self.get('/'))
            endpoint_info['url'] = self.endpoint
        except FTS3ClientException:
            raise
        except Exception, e:
            raise BadEndpoint("%s (%s)" % (self.endpoint, str(e))), None, sys.exc_info()[2]
        return endpoint_info

    def __init__(self, endpoint, ucert=None, ukey=None):
        self.passwd = None

        self._set_endpoint(endpoint)
        self._set_x509(ucert, ukey)
        self._requester = RequestFactory(self.ucert, self.ukey, passwd=self.passwd)
        self.endpoint_info = self._validate_endpoint()
        # Log obtained information
        log.debug("Using endpoint: %s" % self.endpoint_info['url'])
        log.debug("REST API version: %(major)d.%(minor)d.%(patch)d" % self.endpoint_info['api'])
        log.debug("Schema version: %(major)d.%(minor)d.%(patch)d" % self.endpoint_info['schema'])
        log.debug("Delegation version: %(major)d.%(minor)d.%(patch)d" % self.endpoint_info['delegation'])

    def get_endpoint_info(self):
        return self.endpoint_info

    def get(self, path):
        return self._requester.method('GET',
                                      "%s/%s" % (self.endpoint, path))

    def put(self, path, body):
        return self._requester.method('PUT',
                                      "%s/%s" % (self.endpoint, path),
                                      body)

    def delete(self, path):
        return self._requester.method('DELETE',
                                      "%s/%s" % (self.endpoint, path))

    def post_json(self, path, body):
        return self._requester.method('POST',
                                      "%s/%s" % (self.endpoint, path),
                                      body,
                                      headers={'Content-Type': 'text/json'})

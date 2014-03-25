from datetime import datetime
from M2Crypto import X509, RSA, EVP, BIO
import getpass
import json
import logging
import os
import pytz
import sys

from exceptions import *
from request import RequestFactory


# Return a list of certificates from the file
def _get_x509_list(cert, logger):
    x509_list = []
    fd = BIO.openfile(cert, 'rb')
    cert = X509.load_cert_bio(fd)
    try:
        while True:
            x509_list.append(cert)
            logger.debug("Loaded " + cert.get_subject().as_text())
            cert = X509.load_cert_bio(fd)
    except X509.X509Error:
        # When there are no more certs, this is what we get, so it is fine
        pass

    del fd
    return x509_list


# Base class for actors
class Context(object):

    def _set_logger(self, logger):
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger()

    def _read_passwd_from_stdin(self, *args, **kwargs):
        if not self.passwd:
            self.passwd = getpass.getpass('Private key password: ')
        return self.passwd

    def _set_x509(self, ucert, ukey):
        if not ucert:
            if 'X509_USER_PROXY' in os.environ:
                ucert = os.environ['X509_USER_PROXY']
            elif 'X509_USER_CERT' in os.environ:
                ucert = os.environ['X509_USER_CERT']

        if not ukey:
            if 'X509_USER_PROXY' in os.environ:
                ukey = os.environ['X509_USER_PROXY']
            elif 'X509_USER_KEY' in os.environ:
                ukey = os.environ['X509_USER_KEY']

        if ucert and ukey:
            self.x509_list = _get_x509_list(ucert, self.logger)
            self.x509 = self.x509_list[0]
            not_after = self.x509.get_not_after()
            if not_after.get_datetime() < datetime.now(pytz.UTC):
                raise Exception("Proxy expired!")

            self.rsa_key = RSA.load_key(ukey, self._read_passwd_from_stdin)
            self.evp_key = EVP.PKey()
            self.evp_key.assign_rsa(self.rsa_key)

            self.ucert = ucert
            self.ukey = ukey
        else:
            self.ucert = self.ukey = None

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

    def __init__(self, endpoint, ucert=None, ukey=None, logger=None):
        self.passwd = None

        self._set_logger(logger)
        self._set_endpoint(endpoint)
        self._set_x509(ucert, ukey)
        self._requester = RequestFactory(self.ucert, self.ukey, passwd=self.passwd)
        self.endpoint_info = self._validate_endpoint()
        # Log obtained information
        self.logger.debug("Using endpoint: %s" % self.endpoint_info['url'])
        self.logger.debug("REST API version: %(major)d.%(minor)d.%(patch)d" % self.endpoint_info['api'])
        self.logger.debug("Schema version: %(major)d.%(minor)d.%(patch)d" % self.endpoint_info['schema'])
        self.logger.debug("Delegation version: %(major)d.%(minor)d.%(patch)d" % self.endpoint_info['delegation'])

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

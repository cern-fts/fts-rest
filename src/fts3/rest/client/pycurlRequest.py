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
try:
    import simplejson as json
except:
    import json
import logging
import pycurl
import tempfile
from exceptions import *
import os


_PYCURL_SSL = pycurl.version_info()[5].split('/')[0]


log = logging.getLogger(__name__)


class PycurlRequest(object):

    def _set_ssl(self):
        self.curl_handle.setopt(pycurl.SSL_VERIFYPEER, self.verify)
        if self.verify:
            self.curl_handle.setopt(pycurl.SSL_VERIFYHOST, 2)
        else:
            self.curl_handle.setopt(pycurl.SSL_VERIFYHOST, 0)
        if self.ucert:
            self.curl_handle.setopt(pycurl.SSLCERT, self.ucert)
        if self.ukey:
            self.curl_handle.setopt(pycurl.SSLKEY, self.ukey)
        if self.capath:
            self.curl_handle.setopt(pycurl.CAPATH, self.capath)
        if self.passwd:
            self.curl_handle.setopt(pycurl.SSLKEYPASSWD, self.passwd)
        if self.connectTimeout:
            self.curl_handle.setopt(pycurl.CONNECTTIMEOUT, self.connectTimeout)
        if self.timeout:
            self.curl_handle.setopt(pycurl.TIMEOUT, self.timeout)

        if _PYCURL_SSL == 'GnuTL':
            pass
        elif _PYCURL_SSL == 'NSS':
            if self.ucert:
                self.curl_handle.setopt(pycurl.CAINFO, self.ucert)
        else:
            pass

    def __init__(self, ucert, ukey, capath=None, passwd=None, verify=True, access_token=None, connectTimeout=30, timeout=30):
        self.ucert = ucert
        self.ukey  = ukey
        self.passwd = passwd
        self.access_token = access_token
        self.verify = verify
        self.connectTimeout = connectTimeout
        self.timeout = timeout

        if capath:
            self.capath = capath
        elif 'X509_CERT_DIR' in os.environ:
            self.capath = os.environ['X509_CERT_DIR']
        else:
            self.capath = '/etc/grid-security/certificates'

        self.curl_handle = pycurl.Curl()
        self._set_ssl()

    def _handle_error(self, url, code, response_body=None):
        # Try parsing the response, maybe we can get the error message
        message = None
        response = None
        if response_body:
            try:
                response = json.loads(response_body)
                if 'message' in response:
                    message = response['message']
                else:
                    message = response_body
            except:
                message = response_body

        if code == 207:
            try:
                raise ClientError('\n'.join(map(lambda m: m['http_message'], response)))
            except (KeyError, TypeError):
                raise ClientError(message)
        elif code == 400:
            if message:
                raise ClientError('Bad request: ' + message)
            else:
                raise ClientError('Bad request')
        elif 401 <= code <= 403:
            raise Unauthorized("Credentials not valid")
        elif code == 404:
            raise NotFound(url, message)
        elif code == 419:
            raise NeedDelegation('Need delegation')
        elif code == 424:
            raise FailedDependency('Failed dependency')
        elif 404 < code < 500:
            raise ClientError(str(code))
        elif code == 503:
            raise TryAgain(str(code))
        elif code >= 500:
            raise ServerError(str(code))

    def method(self, method, url, body=None, headers=None):
        self.curl_handle.setopt(pycurl.CUSTOMREQUEST, method)
        if method == 'GET':
            self.curl_handle.setopt(pycurl.HTTPGET, True)
        elif method == 'HEAD':
            self.curl_handle.setopt(pycurl.NOBODY, True)
        elif method == 'POST':
            self.curl_handle.setopt(pycurl.POST, True)
        elif method == 'PUT':
            self.curl_handle.setopt(pycurl.UPLOAD, True)

        _headers = {'Accept': 'application/json'}
        if headers:
            _headers.update(headers)
        if self.access_token:
            _headers['Authorization'] = 'Bearer ' + self.access_token
        if len(_headers) > 0:
            self.curl_handle.setopt(pycurl.HTTPHEADER, map(lambda (k, v): "%s: %s" % (k, v), _headers.iteritems()))

        self.curl_handle.setopt(pycurl.URL, str(url))
        #self.curl_handle.setopt(pycurl.VERBOSE, 1)

        # Callback methods produce leaks in EL6, so better avoid them
        response_file = tempfile.TemporaryFile()
        self.curl_handle.setopt(pycurl.WRITEDATA, response_file)

        if body is not None:
            input_file = tempfile.TemporaryFile()
            input_file.write(body)
            input_file.seek(0)
            self.curl_handle.setopt(pycurl.INFILESIZE, len(body))
            self.curl_handle.setopt(pycurl.POSTFIELDSIZE, len(body))
            self.curl_handle.setopt(pycurl.READDATA, input_file)
        else:
            self.curl_handle.setopt(pycurl.INFILESIZE, 0)
            self.curl_handle.setopt(pycurl.POSTFIELDSIZE, 0)

        self.curl_handle.perform()
        response_file.seek(0)
        response_str = response_file.read()
        #log.debug(response_str)

        self._handle_error(url, self.curl_handle.getinfo(pycurl.HTTP_CODE), response_str)

        return response_str


__all__ = ['PycurlRequest']

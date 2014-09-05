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

import json
import pycurl
from exceptions import *
from StringIO import StringIO


class RequestFactory(object):

    def __init__(self, ucert, ukey, cafile=None, capath=None, passwd=None, verify=True, access_token=None):
        self.ucert = ucert
        self.ukey  = ukey
        self.passwd = passwd
        self.access_token = access_token

        self.verify = verify

        if cafile:
            self.cafile = cafile
        else:
            self.cafile = ucert

        if capath:
            self.capath = capath
        else:
            self.capath = '/etc/grid-security/certificates'

        self.curl_handle = pycurl.Curl()
        self.curl_handle.setopt(pycurl.SSL_VERIFYPEER, self.verify)
        if self.verify:
            self.curl_handle.setopt(pycurl.SSL_VERIFYHOST, 2)
        if self.ucert:
            self.curl_handle.setopt(pycurl.SSLCERT, self.ucert)
        if self.ukey:
            self.curl_handle.setopt(pycurl.SSLKEY, self.ukey)
        if self.capath:
            self.curl_handle.setopt(pycurl.CAPATH, self.capath)
        if self.cafile:
            self.curl_handle.setopt(pycurl.CAINFO, self.cafile)
        if self.passwd:
            self.curl_handle.setopt(pycurl.SSLKEYPASSWD, self.passwd)

    def _handle_error(self, url, code, response_body=None):
        # Try parsing the response, maybe we can get the error message
        message = None
        if response_body:
            try:
                message = json.loads(response_body)['message']
            except:
                pass

        if code == 400:
            raise ClientError('Bad request: ' + message)
        elif 401 <= code <= 403:
            raise Unauthorized()
        elif code == 404:
            raise NotFound(url)
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

    def _receive(self, data):
        self._response += data
        return len(data)

    def _send(self, length):
        return self._input.read(length)

    def _ioctl(self, cmd):
        if cmd == pycurl.IOCMD_RESTARTREAD:
            self._input.seek(0)

    def method(self, method, url, body=None, headers=None):
        if method == 'GET':
            self.curl_handle.setopt(pycurl.HTTPGET, True)
        elif method == 'HEAD':
            self.curl_handle.setopt(pycurl.NOBODY, True)
        elif method == 'POST':
            self.curl_handle.setopt(pycurl.POST, True)
        elif method == 'PUT':
            self.curl_handle.setopt(pycurl.UPLOAD, True)
        else:
            self.curl_handle.setopt(pycurl.CUSTOMREQUEST, method)

        _headers = {}
        if headers:
            _headers.update(headers)
        if self.access_token:
            _headers['Authorization'] = 'Bearer ' + self.access_token
        if len(_headers) > 0:
            self.curl_handle.setopt(pycurl.HTTPHEADER, map(lambda (k, v): "%s: %s" % (k, v), _headers.iteritems()))

        self.curl_handle.setopt(pycurl.URL, str(url))
        #self.curl_handle.setopt(pycurl.VERBOSE, 1)

        self._response = ''
        self.curl_handle.setopt(pycurl.WRITEFUNCTION, self._receive)

        if body is not None:
            self._input = StringIO(body)
            self.curl_handle.setopt(pycurl.INFILESIZE, len(body))
            self.curl_handle.setopt(pycurl.POSTFIELDSIZE, len(body))
            self.curl_handle.setopt(pycurl.READFUNCTION, self._send)
            self.curl_handle.setopt(pycurl.IOCTLFUNCTION, self._ioctl)

        self.curl_handle.perform()

        self._handle_error(url, self.curl_handle.getinfo(pycurl.HTTP_CODE), self._response)

        return self._response

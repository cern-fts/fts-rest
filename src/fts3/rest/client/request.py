import pycurl
from exceptions import *
from StringIO import StringIO


class RequestFactory(object):

    def __init__(self, ucert, ukey, cafile=None, capath=None, passwd=None, verify=False):
        self.ucert = ucert
        self.ukey  = ukey
        self.passwd = passwd

        self.verify = verify

        if cafile:
            self.cafile = cafile
        else:
            self.cafile = ucert

        if capath:
            self.capath = capath
        else:
            self.capath = '/etc/grid-security/certificates'

    def _handle_error(self, url, code):
        if code == 400:
            raise ClientError('Bad request')
        elif code >= 401 and code <= 403:
            raise Unauthorized()
        elif code == 404:
            raise NotFound(url)
        elif code > 404 and code < 500:
            raise ClientError(str(code))
        elif code >= 500:
            raise ServerError(str(code))

    def _receive(self, data):
        self._response += data
        return len(data)

    def _send(self, len):
        return self._input.read(len)

    def _ioctl(self, cmd):
        if cmd == pycurl.IOCMD_RESTARTREAD:
            self._input.seek(0)

    def method(self, method, url, body=None, headers=None):
        handle = pycurl.Curl()
        handle.setopt(pycurl.SSL_VERIFYPEER, self.verify)
        handle.setopt(pycurl.SSL_VERIFYHOST, self.verify)
        handle.setopt(pycurl.CAPATH, self.capath)
        handle.setopt(pycurl.CAINFO, self.cafile)
        handle.setopt(pycurl.SSLCERT, self.ucert)
        handle.setopt(pycurl.SSLKEY, self.ukey)
        if self.passwd:
            handle.setopt(pycurl.SSLKEYPASSWD, self.passwd)

        if method == 'GET':
            handle.setopt(pycurl.HTTPGET, True)
        elif method == 'HEAD':
            handle.setopt(pycurl.NOBODY, True)
        elif method == 'POST':
            handle.setopt(pycurl.POST, True)
        elif method == 'PUT':
            handle.setopt(pycurl.UPLOAD, True)
        else:
            handle.setopt(pycurl.CUSTOMREQUEST, method)
        if headers:
            handle.setopt(pycurl.HTTPHEADER, map(lambda (k, v): "%s: %s" % (k, v), headers.iteritems()))

        handle.setopt(pycurl.URL, str(url))

        self._response = ''
        handle.setopt(pycurl.WRITEFUNCTION, self._receive)

        if body is not None:
            self._input = StringIO(body)
            handle.setopt(pycurl.INFILESIZE, len(body))
            handle.setopt(pycurl.POSTFIELDSIZE, len(body))
            handle.setopt(pycurl.READFUNCTION, self._send)
            handle.setopt(pycurl.IOCTLFUNCTION, self._ioctl)

        handle.perform()

        self._handle_error(url, handle.getinfo(pycurl.HTTP_CODE))

        return self._response

import httplib
import sys
import urllib2
from exceptions import *


class HTTPSWithCertHandler(urllib2.HTTPSHandler):
	def __init__(self, cert, key):
		urllib2.HTTPSHandler.__init__(self)
		self.cert = cert
		self.key  = key
		
	def https_open(self, req):
		return self.do_open(self.getConnection, req)
	
	def getConnection(self, host, timeout = 1000):
		return httplib.HTTPSConnection(host, cert_file = self.cert, key_file = self.key)
	


class RequestFactory(object):
	
	def __init__(self, ucert, ukey, cafile = None, capath = None, verify = False):
		self.ucert = ucert
		self.ukey  = ukey
		
		self.verify = verify
		
		if cafile:
			self.cafile = cafile
		else:
			self.cafile = ucert
		
		if capath:
			self.capath = capath
		else:
			self.capath = '/etc/grid-security/certificates'


	def _handleException(self, e):		
		if e.code == 400:
			raise ClientError(e.reason)
		elif e.code >= 401 and e.code <= 403:
			raise Unauthorized()
		elif e.code == 404:
			raise NotFound(url)
		elif e.code > 404 and e.code < 500:
			raise ClientError(e.reason)
		elif e.code >= 500:
			raise ServerError(e.reason)


	def get(self, url, headers = {}):
		opener = urllib2.build_opener(HTTPSWithCertHandler(self.ucert, self.ukey))
		
		try:
			request = urllib2.Request(url, headers = headers)
			response = opener.open(request)
			return response.read()
		except urllib2.HTTPError, e:
			self._handleException(e)
			
	def put(self, url, body, headers = {}):
		opener = urllib2.build_opener(HTTPSWithCertHandler(self.ucert, self.ukey))
		
		try:
			request = urllib2.Request(url, data = body, headers = headers)
			request.get_method = lambda: 'PUT'
			response = opener.open(request)
			return response.read()
		except urllib2.HTTPError, e:
			self._handleException(e)


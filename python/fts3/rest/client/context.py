from datetime import datetime, timedelta
from exceptions import *
from M2Crypto import X509, RSA, EVP, ASN1, BIO
from request import RequestFactory
import json
import logging
import os
import pytz
import sys


# Return a list of certificates from the file
def getX509List(file, logger):
	x509List = []
	
	fd = BIO.openfile(file, 'rb')
	cert = X509.load_cert_bio(fd)
	try:
		while True:
			x509List.append(cert)
			logger.debug("Loaded " + cert.get_subject().as_text())
			cert = X509.load_cert_bio(fd)
	except X509.X509Error:
		pass # When there are no more certs, this is what we get, so it is fine
				
	del fd	
	return x509List



# Base class for actors
class Context(object):
	
	def _setLogger(self, logger):
		if logger:
			self.logger = logger
		else:
			self.logger = logging.getLogger()


	def _setX509(self, ucert, ukey):
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
			self.x509List = getX509List(ucert, self.logger)
			self.x509     = self.x509List[0]
			if self.x509.get_not_after().get_datetime() < datetime.now(pytz.UTC):
				raise Exception("Proxy expired!")
			
			self.rsaKey = RSA.load_key(ukey)
			self.evpKey = EVP.PKey()
			self.evpKey.assign_rsa(self.rsaKey)
			
			self.ucert = ucert
			self.ukey  = ukey


	def _setEndpoint(self, endpoint):
		self.endpoint = endpoint
		if self.endpoint.endswith('/'):
			self.endpoint = self.endpoint[:-1]
			
			
	def _validateEndpoint(self):
		try:
			endpointInfo = json.loads(self.get('/'))
			endpointInfo['url'] = self.endpoint
			
			if endpointInfo['api'] != 'Mk.1':
				raise ValueError("Wrong API version")
		
		except FTS3ClientException:
			raise
		except Exception, e:
			raise BadEndpoint, "%s (%s)" % (self.endpoint, str(e)), sys.exc_info()[2]
		
		return endpointInfo
		
	
	def __init__(self, endpoint, ucert = None, ukey = None, logger = None, **kwargs):
		self._setLogger(logger)
		self._setEndpoint(endpoint)
		self._setX509(ucert, ukey)
		self._requester = RequestFactory(self.ucert, self.ukey)
		self.endpointInfo = self._validateEndpoint()
		
		# Log obtained information
		self.logger.debug("Using endpoint: %s" % self.endpointInfo['url'])
		self.logger.debug("REST API version: %s" % self.endpointInfo['api'])
		self.logger.debug("Schema version: %(major)d.%(minor)d.%(patch)d" % self.endpointInfo['schema'])
		self.logger.debug("Delegation version: %(major)d.%(minor)d.%(patch)d" % self.endpointInfo['delegation'])

		
	def getEndpointInfo(self):		
		return self.endpointInfo
	
	
	def get(self, path):
		return self._requester.method('GET', "%s/%s" % (self.endpoint, path))
	
	
	def put(self, path, body):
		return self._requester.method('PUT', "%s/%s" % (self.endpoint, path), body)
	
	
	def delete(self, path):
		return self._requester.method('DELETE', "%s/%s" % (self.endpoint, path))

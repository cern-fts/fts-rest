import json
import logging
import os
import pytz
import sys
import pycurl
from datetime import datetime, timedelta
from M2Crypto import X509, RSA, EVP, ASN1
from request import RequestFactory
from exceptions import *



def setDefaultLogging():
	logging.basicConfig(format='# %(message)s', level = logging.INFO)



# Return a list of certificates from the file
def getX509List(file, logger):
	SEEKING_CERT = 0
	LOADING_CERT = 1

	buffer = ""
	x509List = []
	
	fd = open(file, 'r')	
	status = SEEKING_CERT
	for line in fd:
		if line == '-----BEGIN CERTIFICATE-----\n':
			status = LOADING_CERT
		elif line == '-----END CERTIFICATE-----\n':
			buffer += line
			x509 = X509.load_cert_string(buffer, X509.FORMAT_PEM)
			x509List.append(x509)
			
			logger.debug("Loaded " + x509.get_subject().as_text())
			
			buffer = ""
			status = SEEKING_CERT
			
		if status == LOADING_CERT:
			buffer += line
				
	del fd
	
	return x509List



class Client(object):
	
	def __init__(self, endpoint, ucert = None, ukey = None, logger = None):
		if logger:
			self.logger = logger
		else:
			self.logger = logging.getLogger()
		
		self.endpoint = endpoint
		if self.endpoint.endswith('/'):
			self.endpoint = self.endpoint[:-1]
		
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
			
		if ucert:
			self.x509List = getX509List(ucert, self.logger)
			self.x509     = self.x509List[0]
			if self.x509.get_not_after().get_datetime() < datetime.now(pytz.UTC):
				raise Exception("Proxy expired!")
			
		if ukey:
			self.rsaKey = RSA.load_key(ukey)
			self.evpKey = EVP.PKey()
			self.evpKey.assign_rsa(self.rsaKey)
			
		self.requester = RequestFactory(ucert, ukey)
		
		# Validate the endpoint
		try:
			self.endpointInfo = json.loads(self.requester.get(self.endpoint))
			self.endpointInfo['url'] = self.endpoint
			
			if self.endpointInfo['api'] != 'Mk.1':
				raise ValueError("Wrong API version")
			
		except Exception, e:
			raise BadEndpoint, "%s (%s)" % (self.endpoint, str(e)), sys.exc_info()[2]
		
		
		self.logger.info("Using endpoint: %s" % self.endpointInfo['url'])
		self.logger.info("REST API version: %s" % self.endpointInfo['api'])
		self.logger.info("Schema version: %(major)d.%(minor)d.%(patch)d" % self.endpointInfo['schema'])
		self.logger.info("Delegation version: %(major)d.%(minor)d.%(patch)d" % self.endpointInfo['delegation'])



	def getEndpointInfo(self):		
		return self.endpointInfo
		
	
		
	def getJobStatus(self, jobId):
		url = "%s/jobs/%s" % (self.endpoint, jobId)
		
		try:
			return json.loads(self.requester.get(url))
		except NotFound:
			raise NotFound(jobId)

		
		
	def delegate(self):
		whoami         = "%s/whoami" % self.endpoint
		delegationRoot = "%s/delegation" % self.endpoint
				
		try:
			r = json.loads(self.requester.get(whoami))
			delegationId = r['delegation_id']
			
			self.logger.debug("Delegation ID: " + delegationId)
			
			r = json.loads(self.requester.get(delegationRoot + '/' + delegationId))
			
			if r is not None:
				expirationTime = datetime.strptime(r['termination_time'], '%Y-%m-%dT%H:%M:%S%z')
				if expiratiomTime > datetime.now() + timedelta(hours = 1):
					self.logger.info("Not bothering doing the delegation")
					return delegationId
				else:
					self.logger.info("Expiration time passed:  " + str(expirationTime))
			else:
				self.logger.info("No previous delegation found")
				
			self.logger.info("Delegating")
			
			requestPEM = self.requester.get(delegationRoot + '/' + delegationId + '/request')
			
			x509Request = X509.load_request_string(requestPEM)
			self.logger.debug("Signing request for %s" % x509Request.get_subject().as_text())
			
			notBefore = ASN1.ASN1_UTCTIME()
			notBefore.set_datetime(datetime.now(pytz.UTC))
			notAfter  = ASN1.ASN1_UTCTIME()
			notAfter.set_datetime(datetime.now(pytz.UTC) + timedelta(hours = 7))
			
			cert = X509.X509()
			cert.set_subject(x509Request.get_subject())
			cert.set_serial_number(x509Request.get_subject().as_hash())
			cert.set_version(x509Request.get_version())
			cert.set_not_before(notBefore)
			cert.set_not_after(notAfter)
			cert.set_issuer(self.x509.get_subject())
			cert.set_pubkey(x509Request.get_pubkey())
			cert.sign(self.evpKey, 'sha1')
			
			certPEM = cert.as_pem()
			
			r = requests.put(delegationRoot + '/' + delegationId + '/request', certPEM, cert = (self.ucert, self.ukey))
			
			if r.status_code != 201:
				raise Exception(r.text)
				
			return delegationId			
		
		except FTS3ClientException, e:
			raise e
		except Exception, e:
			raise ClientError, str(e), sys.exc_info()[2]
		

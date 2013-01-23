import json
import pytz
import sys
import requests
from datetime import datetime, timedelta
from M2Crypto import X509, RSA, EVP, ASN1


# Return a list of certificates from the file
def getX509List(file):
	SEEKING_CERT = 0
	LOADING_CERT = 1

	buffer = ""
	x509List = []
	
	fd = open(file, 'r')	
	status = SEEKING_CERT
	for line in fd:
		if line == '-----BEGIN CERTIFICATE-----\n':
			status = LOADING_CERT
			print "Found certificate in chain"
		elif line == '-----END CERTIFICATE-----\n':
			buffer += line
			x509 = X509.load_cert_string(buffer, X509.FORMAT_PEM)
			x509List.append(x509)
			
			print "Loaded", x509.get_subject().as_text()
			
			buffer = ""
			status = SEEKING_CERT
			
		if status == LOADING_CERT:
			buffer += line
				
	del fd
	
	return x509List



class ClientV1(object):
	
	def __init__(self, endpoint, ucert = None, ukey = None):
		self.endpoint = endpoint
		if self.endpoint.endswith('/'):
			self.endpoint = self.endpoint[:-1]
			
		if ucert:	
			self.x509List = getX509List(ucert)
			self.x509     = self.x509List[0]
			if self.x509.get_not_after().get_datetime() < datetime.now(pytz.UTC):
				raise Exception("Proxy expired!")
			
		if ukey:
			self.rsaKey = RSA.load_key(ukey)
			self.evpKey = EVP.PKey()
			self.evpKey.assign_rsa(self.rsaKey)
	
			
	
	def getEndpointInfo(self):
		url = "%s/ping" % (self.endpoint)
		
		try:
			r = requests.get(url)
			j = r.json
			return {'url': self.endpoint,
			    	'version': j['api'],
			    	'schema': j['schema']}
		except Exception, e:
			raise IOError(e)
		
	
		
	def getJobStatus(self, jobId):
		url = "%s/job/%s/" % (self.endpoint, jobId)
		
		try:
			r = requests.get(url)
			return r.json
		except urllib2.HTTPError, e:
			if e.code == 404:
				raise KeyError("requestID <%s> was not found" % jobId)
			else:
				raise IOError(e)
		except Exception, e:
			raise IOError(e)
	
	
	
	def getJobTransfers(self, jobId):
		url = "%s/job/%s/files/" % (self.endpoint, jobId)
		try:
			r = requests.get(url)
			return r.json['objects']
		except urllib2.HTTPError, e:
			if e.code == 404:
				raise KeyError("requestID <%s> was not found" % jobId)
			else:
				raise IOError(e)
		except Exception, e:
			raise IOError(e)
		
		
	def delegate(self):
		urls = {'getRequest': "%s/delegation/request" % (self.endpoint),
				'putSigned':  "%s/delegation/credential" % (self.endpoint),
			   }
		
		try:		
			r = requests.get(urls['getRequest'])
			delegationId = r.headers['X-Delegation-ID']
			requestPEM   = r.content
			
			x509Request = X509.load_request_string(requestPEM)
			print >>sys.stderr, "Signing request for %s" % x509Request.get_subject().as_text()
			
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
			
			r = requests.put(urls['putSigned'] + '/' + delegationId, certPEM)
			
			if r.status_code != 201:
				raise Exception(r.text)
				
			return delegationId			
			
		except Exception, e:
			raise IOError(e)
		

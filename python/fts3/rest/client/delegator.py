from datetime import datetime, timedelta
from exceptions import *
from M2Crypto import X509, RSA, EVP, ASN1, m2
import json
import pytz
import sys
import time



class Delegator(object):
	
	def __init__(self, context):
		self.context = context


	def _getDelegationId(self):
		r = json.loads(self.context.get('/whoami'))
		return r['delegation_id']
	
	
	def _getRemainingLife(self, delegationId):
		r = json.loads(self.context.get('/delegation/' + delegationId))
		
		if r is None:
			return None
		else:
			expirationTime = datetime.strptime(r['termination_time'], '%Y-%m-%dT%H:%M:%S')
			return expirationTime - datetime.now()
		
		
	def _getProxyRequest(self, delegationId):
		requestPEM = self.context.get('/delegation/' + delegationId + '/request')
		x509Request = X509.load_request_string(requestPEM)
		if x509Request.verify(x509Request.get_pubkey()) != 1:
			raise ServerError('Error verifying signature on the request')		
		# Return
		return x509Request
	
	
	def _signRequest(self, x509Request, lifetime):		
		notBefore = ASN1.ASN1_UTCTIME()
		notBefore.set_datetime(datetime.now(pytz.UTC))
		notAfter  = ASN1.ASN1_UTCTIME()
		notAfter.set_datetime(datetime.now(pytz.UTC) + lifetime)
		
		proxySubject = X509.X509_Name()
		for c in self.context.x509.get_subject():
			m2.x509_name_add_entry(proxySubject._ptr(), c._ptr(), -1, 0)
		proxySubject.add_entry_by_txt('commonName', 0x1000, 'proxy', -1, -1, 0)
		
		proxy = X509.X509()
		proxy.set_version(2)
		proxy.set_subject(proxySubject)
		proxy.set_serial_number(long(time.time()))
		proxy.set_version(x509Request.get_version())
		proxy.set_issuer(self.context.x509.get_subject())
		proxy.set_pubkey(x509Request.get_pubkey())
		
		# Make sure the proxy is not longer than any other inside the chain
		any_rfc_proxies = False
		for cert in self.context.x509List:
			if cert.get_not_after() < notAfter:
				notAfter = cert.get_not_after()
			try:
				cert.get_ext('1.3.6.1.5.5.7.1.14')
				any_rfc_proxies = True
			except:
				pass	

		proxy.set_not_after(notAfter)
		proxy.set_not_before(notBefore)
		
		if any_rfc_proxies:
			raise NotImplementedError('RFC proxies not supported yet')		
		
		proxy.sign(self.context.evpKey, 'sha1')
		
		return proxy
	
	
	def _putProxy(self, delegationId, x509Proxy):
		self.context.put('/delegation/' + delegationId + '/credential', x509Proxy)


	def _fullProxyChain(self, x509Proxy):
		chain = x509Proxy.as_pem()
		for cert in self.context.x509List:
			chain += cert.as_pem()
		return chain
		

	def delegate(self, lifetime = timedelta(hours = 7)):	
		try:
			delegationId = self._getDelegationId()		
			self.context.logger.debug("Delegation ID: " + delegationId)
			
			remainingLife = self._getRemainingLife(delegationId)
			
			if remainingLife is None: 
				self.context.logger.debug("No previous delegation found")
			elif remainingLife <= timedelta(0):
				self.context.logger.debug("The delegated credentials expired")
			elif remainingLife >= timedelta(hours = 1):
				self.context.logger.debug("Not bothering doing the delegation")
				return delegationId
							
			# Ask for the request
			self.context.logger.debug("Delegating")
			x509Request = self._getProxyRequest(delegationId)
					
			# Sign request
			self.context.logger.debug("Signing request")
			x509Proxy = self._signRequest(x509Request, lifetime)
			x509ProxyPEM = self._fullProxyChain(x509Proxy)
					
			# Send the signed proxy
			self._putProxy(delegationId, x509ProxyPEM)
				
			return delegationId			
		
		except FTS3ClientException, e:
			raise e
		except Exception, e:
			raise ClientError, str(e), sys.exc_info()[2]


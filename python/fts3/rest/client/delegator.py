from base import Actor
from datetime import datetime, timedelta
from exceptions import *
from M2Crypto import X509, RSA, EVP, ASN1
import json
import pytz
import sys



class Delegator(Actor):
	
	def __init__(self, *args, **kwargs):
		super(Delegator, self).__init__(*args, **kwargs)
		self.whoami         = "%s/whoami" % self.endpoint
		self.delegationRoot = "%s/delegation" % self.endpoint


	def _getDelegationId(self):
		r = json.loads(self.requester.get(self.whoami))
		return r['delegation_id']
	
	
	def _getRemainingLife(self, delegationId):
		r = json.loads(self.requester.get(self.delegationRoot + '/' + delegationId))
		
		if r is None:
			return None
		else:
			expirationTime = datetime.strptime(r['termination_time'], '%Y-%m-%dT%H:%M:%S')
			return expirationTime - datetime.now()
		
		
	def _getProxyRequest(self, delegationId):
		proxy = self.requester.get(self.delegationRoot + '/' + delegationId + '/request')
		return X509.load_request_string(proxy)
	
	
	def _signRequest(self, x509Request, lifetime):		
		notBefore = ASN1.ASN1_UTCTIME()
		notBefore.set_datetime(datetime.now(pytz.UTC))
		notAfter  = ASN1.ASN1_UTCTIME()
		notAfter.set_datetime(datetime.now(pytz.UTC) + lifetime)
		
		proxy = X509.X509()
		proxy.set_subject(x509Request.get_subject())
		proxy.set_serial_number(x509Request.get_subject().as_hash())
		proxy.set_version(x509Request.get_version())
		proxy.set_not_before(notBefore)
		proxy.set_not_after(notAfter)
		proxy.set_issuer(self.x509.get_subject())
		proxy.set_pubkey(x509Request.get_pubkey())
		proxy.sign(self.evpKey, 'sha1')
		
		return proxy
	
	
	def _putProxy(self, delegationId, x509Proxy):
		self.requester.put(self.delegationRoot + '/' + delegationId + '/credential', x509Proxy.as_pem())
		

	def delegate(self, lifetime = timedelta(hours = 7)):	
		try:
			delegationId = self._getDelegationId()		
			self.logger.debug("Delegation ID: " + delegationId)
			
			remainingLife = self._getRemainingLife(delegationId)
			
			if remainingLife is None: 
				self.logger.debug("No previous delegation found")
			elif remainingLife <= timedelta(0):
				self.logger.debug("The delegated credentials expired")
			elif remainingLife >= timedelta(hours = 1):
				self.logger.debug("Not bothering doing the delegation")
				return delegationId
							
			# Ask for the request
			self.logger.debug("Delegating")
			x509Request = self._getProxyRequest(delegationId)
			
			# Sign request
			self.logger.debug("Signing request for %s" % x509Request.get_subject().as_text())
			x509Proxy = self._signRequest(x509Request, lifetime)
			
			# Send the signed proxy
			self._putProxy(delegationId, x509Proxy)
				
			return delegationId			
		
		except FTS3ClientException, e:
			raise e
		except Exception, e:
			raise ClientError, str(e), sys.exc_info()[2]


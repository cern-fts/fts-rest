from base import Actor
from datetime import datetime, timedelta
from exceptions import *
import json
import sys



class Delegator(Actor):
	
	def __init__(self, *args, **kwargs):
		super(Delegator, self).__init__(*args, **kwargs)



	def delegate(self):
		whoami         = "%s/whoami" % self.endpoint
		delegationRoot = "%s/delegation" % self.endpoint
				
		try:
			r = json.loads(self.requester.get(whoami))
			delegationId = r['delegation_id']
			
			self.logger.debug("Delegation ID: " + delegationId)
			
			r = json.loads(self.requester.get(delegationRoot + '/' + delegationId))
			
			if r is not None:
				expirationTime = datetime.strptime(r['termination_time'], '%Y-%m-%dT%H:%M:%S')
				if expirationTime > datetime.now() + timedelta(hours = 1):
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


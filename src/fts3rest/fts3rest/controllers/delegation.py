from fts3.model import CredentialCache, Credential
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from M2Crypto import X509, RSA, EVP, BIO
from pylons.controllers.util import abort
from pylons.decorators import rest
from pylons import request
import pytz
import uuid


def getDNComponents(dn):
	return map(lambda x: tuple(x.split('=')), dn.split('/')[1:])



def populatedName(components):
	x509Name = X509.X509_Name()
	for (field, value) in components:
		x509Name.add_entry_by_txt(field, 0x1000, value, len = -1, loc = -1, set = 0)
	return x509Name



def _muteCallback(*args, **kwargs):
  pass



def generateProxyRequest(dnList):
	# By convention, use the longer representation
	userDN = dnList[-1]
	
	requestKeyPair = RSA.gen_key(512, 65537, callback = _muteCallback)
	requestPKey = EVP.PKey()
	requestPKey.assign_rsa(requestKeyPair)
	request = X509.Request()
	request.set_pubkey(requestPKey)	
	request.set_subject(populatedName([('O', 'Dummy')]))
	request.set_version(0)
	request.sign(requestPKey, 'md5')
	
	return (request, requestPKey)



class DelegationController(BaseController):
	
	@jsonify
	def view(self, id):
		user = request.environ['fts3.User.Credentials']
		cred = Session.query(Credential).get((id, user.user_dn))
		if not cred:
			return None
		else:
			return {'termination_time': cred.termination_time}
	
	
	def request(self, id, start_response):
		user = request.environ['fts3.User.Credentials']
		
		credentialCache = Session.query(CredentialCache).get((id, user.user_dn))
		
		if credentialCache is None:
			(proxyRequest, proxyKey) = generateProxyRequest(user.dn)
			credentialCache = CredentialCache(dlg_id = user.delegation_id,
											  dn = user.user_dn,
										 	  cert_request = proxyRequest.as_pem(),
										  	  priv_key     = proxyKey.as_pem(cipher = None),
										  	  voms_attrs   = ' '.join(user.voms_cred))
			Session.add(credentialCache)
			Session.commit()	
		
		
		start_response('200 OK', [('X-Delegation-ID', credentialCache.dlg_id)])
		return credentialCache.cert_request


	def _readX509List(self, pemString):
		x509List = []
		
		bio = BIO.MemoryBuffer(pemString)
		try:
			while True:
				cert = X509.load_cert_bio(bio)
				x509List.append(cert)
		except X509.X509Error:
			pass
		
		return x509List
	
	def _buildFullProxyPEM(self, proxyPEM, privKey):
		x509List = self._readX509List(proxyPEM)
		return x509List[0].as_pem() + privKey + ''.join(map(lambda x: x.as_pem(), x509List[1:]))
	
	
	@rest.restrict('PUT')
	def credential(self, id, start_response):
		user = request.environ['fts3.User.Credentials']
		credentialCache = Session.query(CredentialCache).get((id, user.user_dn))
		if credentialCache is None:
			start_response('400 BAD REQUEST', [('Content-Type', 'text/plain')])
			return ['No credential cache found']
		
		x509ProxyPEM        = request.body
		x509Proxy           = X509.load_cert_string(x509ProxyPEM)
		proxyExpirationTime = x509Proxy.get_not_after().get_datetime().replace(tzinfo = None)
		x509FullProxyPEM    = self._buildFullProxyPEM(x509ProxyPEM, credentialCache.priv_key)
		
		credential = Credential(dlg_id           = id,
								dn               = user.user_dn,
								proxy            = x509FullProxyPEM,
								voms_attrs       = credentialCache.voms_attrs,
								termination_time = proxyExpirationTime)
		
		Session.merge(credential)
		Session.commit()
		
		start_response('201 CREATED', [])
		
		return ''
	
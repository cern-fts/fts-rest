from fts3.orm import CredentialCache, Credential
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from M2Crypto import X509, RSA, EVP
from pylons.decorators import rest
from pylons import request
import uuid


def getDNComponents(dn):
	return map(lambda x: tuple(x.split('=')), dn.split('/')[1:])



def populatedName(components):
	x509Name = X509.X509_Name()
	for (field, value) in components:
		x509Name.add_entry_by_txt(field, 0x1000, value, len = -1, loc = -1, set = 0)
	return x509Name



def generateProxyRequest(userDN):
	components = getDNComponents(userDN)
	components.append(('CN', 'proxy'))
	
	requestKeyPair = RSA.gen_key(1024, 65537)
	requestPKey = EVP.PKey()
	requestPKey.assign_rsa(requestKeyPair)
	request = X509.Request()
	request.set_pubkey(requestPKey)	
	request.set_subject(populatedName(components))
	request.set_version(2)
	request.sign(requestPKey, 'sha1')
	
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
			(proxyRequest, proxyKey) = generateProxyRequest(user.user_dn)
			credentialCache = CredentialCache(dlg_id = user.delegation_id,
											  dn = user.user_dn,
										 	  cert_request = proxyRequest.as_pem(),
										  	  priv_key     = proxyKey.as_pem(cipher = None),
										  	  voms_attrs   = ' '.join(user.voms_cred))
			Session.add(credentialCache)
			Session.commit()	
		
		
		start_response('200 OK', [('X-Delegation-ID', credentialCache.dlg_id)])
		return credentialCache.cert_request
	
	
	@rest.restrict('PUT')
	def credential(self, id, start_response):
		user = request.environ['fts3.User.Credentials']
		credentialCache = Session.query(CredentialCache).get((id, user.user_dn))
		
		x509ProxyPEM = request.body
		x509Proxy    = X509.load_cert_string(x509ProxyPEM)
		
		credential = Credential(dlg_id           = id,
								dn               = user.user_dn,
								proxy            = x509ProxyPEM,
								voms_attrs       = credentialCache.voms_attrs,
								termination_time = x509Proxy.get_not_after().get_datetime())
		
		Session.merge(credential)
		Session.commit()
		
		start_response('201 CREATED', [])
		
		return ''
	
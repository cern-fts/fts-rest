from django.conf.urls.defaults import *
from django.http import HttpResponse
from fts3.orm import CredentialVersion, CredentialCache, Credential
from M2Crypto import X509, RSA, EVP
from session import session
import json
import uuid



def delegationPing(request, api_name):
	sess = session()
	cv = sess.query(CredentialVersion)[0]
	
	ping = {'delegation': str(cv),
		    'api': api_name}

	response = HttpResponse(json.dumps(ping))
	return response



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



X509_SUBJECT = '/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=aalvarez/CN=678984/CN=Alejandro Alvarez Ayllon/CN=proxy'


def sendProxyRequest(request, api_name):
	# Hardcoded for development
	(proxyRequest, proxyKey) = generateProxyRequest(X509_SUBJECT)
	
	# Register in the database
	credentialCache = CredentialCache(dlg_id = uuid.uuid1(),
									  dn = X509_SUBJECT,
									  cert_request = proxyRequest.as_pem(),
									  priv_key     = proxyKey.as_pem(cipher = None),
									  voms_attrs   = '') 
	
	response = HttpResponse(proxyRequest.as_pem())
	response['X-Delegation-ID'] = credentialCache.dlg_id
	
	sess = session()
	sess.add(credentialCache)
	sess.commit()
	
	return response



def putDelegatedProxy(request, api_name, delegation_id):
	response = HttpResponse(request.body)
	
	x509ProxyPEM = request.body
	x509Proxy    = X509.load_cert_string(x509ProxyPEM)
	
	# Save
	credential = Credential(dlg_id           = delegation_id,
							dn               = X509_SUBJECT,
							proxy            = x509ProxyPEM,
							voms_attrs       = '',
							termination_time = x509Proxy.get_not_after().get_datetime())
	
	sess = session()
	sess.add(credential)
	sess.commit()
	
	response.status_code = 201
	return response



urls = patterns('',
	(r'^$', delegationPing),
	(r'^request$', sendProxyRequest),
	(r'^credential/(?P<delegation_id>\w+)', putDelegatedProxy),
)




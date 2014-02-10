from datetime import datetime
from fts3.model import CredentialCache, Credential
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.helpers import voms
from M2Crypto import X509, RSA, EVP, BIO
from pylons.controllers.util import abort
from pylons.decorators import rest
from pylons import request
import json
import pytz
import types
import uuid

def getDNComponents(dn):
    return map(lambda x: tuple(x.split('=')), dn.split('/')[1:])


def populatedName(components):
    x509Name = X509.X509_Name()
    for (field, value) in components:
        x509Name.add_entry_by_txt(field, 0x1000, value,
                                  len=-1, loc=-1, set=0)
    return x509Name


def _muteCallback(*args, **kwargs):
    pass


def generateProxyRequest(dnList):
    # By convention, use the longer representation
    userDN = dnList[-1]

    requestKeyPair = RSA.gen_key(1024, 65537, callback=_muteCallback)
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
    def view(self, id, start_response):
        """
        Get the termination time of the current delegated credential, if any
        """
        user = request.environ['fts3.User.Credentials']

        if id != user.delegation_id:
            start_response('403 FORBIDDEN', [('Content-Type', 'text/plain')])
            return 'The resquested ID and the credentials ID do not match'

        cred = Session.query(Credential).get((user.delegation_id, user.user_dn))
        if not cred:
            return None
        else:
            return {'termination_time': cred.termination_time}
        
    def delete(self, id, start_response):
        """
        Delete the delegated credentials from the database
        """
        user = request.environ['fts3.User.Credentials']
        
        if id != user.delegation_id:
            start_response('403 FORBIDDEN', [('Content-Type', 'text/plain')])
            return ['The resquested ID and the credentials ID do not match']
        
        cred = Session.query(Credential).get((user.delegation_id, user.user_dn))
        if not cred:
            start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
            return ['Delegated credentials not found']
        else:
            Session.delete(cred)
            Session.commit()
            start_response('204 NO CONTENT', [])
            return ['']

    def request(self, id, start_response):
        """
        Returns a certificate request. First step of the delegation process.
        """
        user = request.environ['fts3.User.Credentials']

        if id != user.delegation_id:
            start_response('403 FORBIDDEN', [('Content-Type', 'text/plain')])
            return ['The resquested ID and the credentials ID do not match']

        credentialCache = Session.query(CredentialCache)\
            .get((user.delegation_id, user.user_dn))

        if credentialCache is None:
            (proxyRequest, proxyKey) = generateProxyRequest(user.dn)
            credentialCache = CredentialCache(dlg_id = user.delegation_id,
                                              dn = user.user_dn,
                                              cert_request = proxyRequest.as_pem(),
                                              priv_key     = proxyKey.as_pem(cipher = None),
                                              voms_attrs   = ' '.join(user.voms_cred))
            Session.add(credentialCache)
            Session.commit()

        start_response('200 OK', [('X-Delegation-ID', credentialCache.dlg_id),
                                  ('Content-Type', 'text/plain')])
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
        x509Chain = ''.join(map(lambda x: x.as_pem(), x509List[1:]))
        return x509List[0].as_pem() + privKey + x509Chain

    @rest.restrict('PUT', 'POST')
    def credential(self, id, start_response):
        """
        Put a proxy generated signing the request sent previously with 'request'
        """
        user = request.environ['fts3.User.Credentials']

        if id != user.delegation_id:
            start_response('403 FORBIDDEN', [('Content-Type', 'text/plain')])
            return ['The resquested ID and the credentials ID do not match']

        credentialCache = Session.query(CredentialCache)\
            .get((user.delegation_id, user.user_dn))
        if credentialCache is None:
            start_response('400 BAD REQUEST', [('Content-Type', 'text/plain')])
            return ['No credential cache found']

        x509ProxyPEM = request.body

        try:
            x509Proxy           = X509.load_cert_string(x509ProxyPEM)
            proxyExpirationTime = x509Proxy.get_not_after().get_datetime().replace(tzinfo = None)
            x509FullProxyPEM    = self._buildFullProxyPEM(x509ProxyPEM, credentialCache.priv_key)

            # Validate the subject
            proxySubject = '/' + '/'.join(x509Proxy.get_subject().as_text().split(', '))
            proxyIssuer = '/' + '/'.join(x509Proxy.get_issuer().as_text().split(', '))
            if proxySubject != proxyIssuer + '/CN=proxy':
                raise Exception("The subject and the issuer of the proxy do not match")
            
            # Make sure the certificate corresponds to the private key
            pkey = EVP.load_key_string(str(credentialCache.priv_key),
                                       callback = lambda v, p1, p2: None)
            if x509Proxy.get_pubkey().get_modulus() != pkey.get_modulus():
                raise Exception("The delegated proxy do not correspond the stored private key")
        except Exception, e:
            start_response('400 BAD REQUEST', [('Content-Type', 'text/plain')])
            return ['Could not process the proxy: ' + str(e)]

        credential = Credential(dlg_id           = user.delegation_id,
                                dn               = user.user_dn,
                                proxy            = x509FullProxyPEM,
                                voms_attrs       = credentialCache.voms_attrs,
                                termination_time = proxyExpirationTime)

        Session.merge(credential)
        Session.commit()

        start_response('201 CREATED', [])
        return ['']

    @rest.restrict('POST')
    def voms(self, id, start_response):
        """
        Generate VOMS extensions for the delegated proxy
        """
        user = request.environ['fts3.User.Credentials']
        
        if id != user.delegation_id:
            start_response('403 FORBIDDEN', [('Content-Type', 'text/plain')])
            return ['The resquested ID and the credentials ID do not match']

        try:
            voms_list = json.loads(request.body)
            if type(voms_list) != types.ListType:
                raise Exception('Expecting a list of strings')
        except Exception, e:
            start_response('400 BAD REQUEST', [('Content-Type', 'text/plain')])
            return [str(e)]

        credential = Session.query(Credential)\
            .get((user.delegation_id, user.user_dn))

        if credential.termination_time <= datetime.utcnow():
            start_response('403 FORBIDDEN', [('Content-Type', 'text/plain')])
            return ['Delegated proxy already expired']

        try:
            voms_client = voms.VomsClient(credential.proxy)
            (new_proxy, new_termination_time) = voms_client.init(voms_list)
        except voms.VomsException, e:
            # Error generating the proxy because of the request itself
            start_response('424 METHOD FAILURE', [('Content-Type', 'text/plain')])
            return [str(e)] 
        except Exception, e:
            # Internal error, re-raise it and let it fail
            raise
        
        credential.proxy = new_proxy
        credential.termination_time = new_termination_time
        credential.voms_attrs = ' '.join(voms_list)
        Session.merge(credential)
        Session.commit()
        
        start_response('203 NON-AUTHORITATIVE INFORMATION', [('Content-Type', 'text/plain')])
        return [str(new_termination_time)]

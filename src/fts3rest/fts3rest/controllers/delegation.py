from datetime import datetime
from fts3.model import CredentialCache, Credential
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.helpers import voms
from M2Crypto import X509, RSA, EVP, BIO
from pylons.decorators import rest
from pylons import request
import json
import types


class ProxyException(Exception):
    pass


def _mute_callback(*args, **kwargs):
    """
    Does nothing. Used as a callback for gen_key
    """
    pass


def _populated_x509_name(components):
    """
    Generates a populated X509_Name with the entries passed in components
    """
    x509_name = X509.X509_Name()
    for (field, value) in components:
        x509_name.add_entry_by_txt(field, 0x1000, value,
                                   len=-1, loc=-1, set=0)
    return x509_name


def _generate_proxy_request():
    """
    Generates a X509 proxy request.
    
    Returns:
        A tuple (X509 request, generated private key)
    """
    key_pair = RSA.gen_key(1024, 65537, callback=_mute_callback)
    pkey = EVP.PKey()
    pkey.assign_rsa(key_pair)
    x509_request = X509.Request()
    x509_request.set_pubkey(pkey)
    x509_request.set_subject(_populated_x509_name([('O', 'Dummy')]))
    x509_request.set_version(0)
    x509_request.sign(pkey, 'md5')

    return (x509_request, pkey)


def _validate_proxy(proxy_pem, private_key_pem):
    """
    Validates a proxy being put by the client
    
    Args:
        proxy_pem: The PEM representation of the proxy
        private_key_pem: The PEM representation of the private key
    
    Returns:
        The proxy expiration time
    
    Raises:
        ProxyException: If the validation fails
    """
    try:
        x509_proxy      = X509.load_cert_string(proxy_pem)
    except X509.X509Error:
        raise ProxyException("Malformed proxy")

    expiration_time = x509_proxy.get_not_after().get_datetime().replace(tzinfo = None)
    private_key     = EVP.load_key_string(str(private_key_pem), callback = _mute_callback)

    if x509_proxy.verify(private_key):
        raise ProxyException("Invalid proxy")

    # Validate the subject
    subject = '/' + '/'.join(x509_proxy.get_subject().as_text().split(', '))
    issuer = '/' + '/'.join(x509_proxy.get_issuer().as_text().split(', '))
    if subject != issuer + '/CN=proxy':
        raise ProxyException("The subject and the issuer of the proxy do not match")

    return expiration_time


def _read_X509_list(x509_pem):
    """
    Loads the list of certificates contained in x509_pem
    """
    x509_list = []
    bio = BIO.MemoryBuffer(x509_pem)
    try:
        while True:
            cert = X509.load_cert_bio(bio)
            x509_list.append(cert)
    except X509.X509Error:
        pass
    return x509_list


def _build_full_proxy(x509_pem, privkey_pem):
    """
    Generates a full proxy from the input parameters.
    A valid full proxy has this format: proxy, private key, certificate chain
    Args:
        proxy_pem: The certificate chain
        privkey_pem: The private key
    Returns:
        A full proxy
    """
    x509_list = _read_X509_list(x509_pem)
    x509_chain = ''.join(map(lambda x: x.as_pem(), x509_list[1:]))
    return x509_list[0].as_pem() + privkey_pem + x509_chain


class DelegationController(BaseController):
    """
    Operations to perform the delegation of credentials
    """

    @doc.return_type('dateTime')
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


    @doc.response(403, 'The requested delegation ID does not belong to the user')
    @doc.response(404, 'The credentials do not exist')
    @doc.response(204, 'The credentials were deleted successfully')
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


    @doc.response(403, 'The requested delegation ID does not belong to the user')
    @doc.response(200, 'The request was generated succesfully')
    @doc.return_type('PEM encoded certificate request')
    def request(self, id, start_response):
        """
        First step of the delegation process: get a certificate request
        
        The returned certificate request must be signed with the user's original
        credentials.
        """
        user = request.environ['fts3.User.Credentials']

        if id != user.delegation_id:
            start_response('403 FORBIDDEN', [('Content-Type', 'text/plain')])
            return ['The resquested ID and the credentials ID do not match']

        credential_cache = Session.query(CredentialCache)\
            .get((user.delegation_id, user.user_dn))

        if credential_cache is None:
            (x509_request, private_key) = _generate_proxy_request()
            credential_cache = CredentialCache(dlg_id = user.delegation_id,
                                               dn = user.user_dn,
                                               cert_request = x509_request.as_pem(),
                                               priv_key     = private_key.as_pem(cipher = None),
                                               voms_attrs   = ' '.join(user.voms_cred))
            Session.add(credential_cache)
            Session.commit()

        start_response('200 OK', [('X-Delegation-ID', credential_cache.dlg_id),
                                  ('Content-Type', 'text/plain')])
        return credential_cache.cert_request

    @doc.input('Signed certificate', 'PEM encoded certificate')
    @doc.response(403, 'The requested delegation ID does not belong to the user')
    @doc.response(400, 'The proxy failed the validation process')
    @doc.response(201, 'The proxy was stored successfully')
    def credential(self, id, start_response):
        """
        Second step of the delegation process: put the generated certificate
        
        The certificate being PUT will have to pass the following validation:
            - There is a previous certificate request done
            - The certificate subject matches the certificate issuer + '/CN=Proxy'
            - The certificate modulus matches the stored private key modulus
        """
        user = request.environ['fts3.User.Credentials']

        if id != user.delegation_id:
            start_response('403 FORBIDDEN', [('Content-Type', 'text/plain')])
            return ['The resquested ID and the credentials ID do not match']

        credential_cache = Session.query(CredentialCache)\
            .get((user.delegation_id, user.user_dn))
        if credential_cache is None:
            start_response('400 BAD REQUEST', [('Content-Type', 'text/plain')])
            return ['No credential cache found']

        x509_proxy_pem = request.body

        try:
            expiration_time = _validate_proxy(x509_proxy_pem, credential_cache.priv_key)
            x509_full_proxy_pem = _build_full_proxy(x509_proxy_pem, credential_cache.priv_key)
        except ProxyException, e:
            start_response('400 BAD REQUEST', [('Content-Type', 'text/plain')])
            return ['Could not process the proxy: ' + str(e)]

        credential = Credential(dlg_id           = user.delegation_id,
                                dn               = user.user_dn,
                                proxy            = x509_full_proxy_pem,
                                voms_attrs       = credential_cache.voms_attrs,
                                termination_time = expiration_time)

        Session.merge(credential)
        Session.commit()

        start_response('201 CREATED', [])
        return ['']

    @doc.input('List of voms commands', 'array')
    @doc.response(403, 'The requested delegation ID does not belong to the user')
    @doc.response(400, 'Could not understand the request')
    @doc.response(424, 'The obtention of the VOMS extensions failed')
    @doc.response(203, 'The obtention of the VOMS extensions succeeded')
    def voms(self, id, start_response):
        """
        Generate VOMS extensions for the delegated proxy
        
        The input must be a json-serialized list of strings, where each strings
        is a voms command (i.e. ["dteam", "dteam:/dteam/Role=lcgadmin"])
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

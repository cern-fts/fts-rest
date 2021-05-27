#   Copyright notice:
#   Copyright  Members of the EMI Collaboration, 2013.
#
#   See www.eu-emi.eu for details on the copyright holders
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

try:
    import simplejson as json
except:
    import json
import logging
import os
import shlex
import types
import M2Crypto.threading

from datetime import datetime
from webob.exc import HTTPBadRequest, HTTPForbidden, HTTPNotFound
from M2Crypto import X509, RSA, EVP, BIO
from pylons import config, request, response
from pylons.templating import render_mako as render

from fts3.model import CredentialCache, Credential
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.helpers import voms
from fts3rest.lib.http_exceptions import HTTPMethodFailure
from fts3rest.lib.middleware.fts3auth import require_certificate
from fts3rest.lib.JobBuilder import get_base_id, get_vo_id

log = logging.getLogger(__name__)


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
    for field, value in components:
        x509_name.add_entry_by_txt(field, 0x1000, value,
                                   len=-1, loc=-1, set=0)
    return x509_name


def _generate_proxy_request(key_len=2048):
    """
    Generates a X509 proxy request.
    
    Args:
        key_len: Length of the RSA key in bits

    Returns:
        A tuple (X509 request, generated private key)
    """
    key_pair = RSA.gen_key(key_len, 65537, callback=_mute_callback)
    pkey = EVP.PKey()
    pkey.assign_rsa(key_pair)
    x509_request = X509.Request()
    x509_request.set_pubkey(pkey)
    x509_request.set_subject(_populated_x509_name([('O', 'Dummy')]))
    x509_request.set_version(0)
    x509_request.sign(pkey, 'sha256')

    return x509_request, pkey


def _read_x509_list(x509_pem):
    """
    Loads the list of certificates contained in x509_pem
    """
    x509_list = []
    bio = BIO.MemoryBuffer(x509_pem)
    try:
        while bio.readable():
            cert = X509.load_cert_bio(bio)
            x509_list.append(cert)
    except X509.X509Error:
        pass
    return x509_list


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
    x509_list = _read_x509_list(proxy_pem)
    if len(x509_list) < 2:
        raise ProxyException("Malformed proxy")
    x509_proxy = x509_list[0]
    x509_proxy_issuer = x509_list[1]

    expiration_time = x509_proxy.get_not_after().get_datetime().replace(tzinfo=None)
    private_key     = EVP.load_key_string(str(private_key_pem), callback=_mute_callback)

    # The modulus of the stored private key and the modulus of the proxy must match
    if x509_proxy.get_pubkey().get_modulus() != private_key.get_modulus():
        raise ProxyException("The proxy does not match the stored associated private key")

    # Verify the issuer
    if x509_proxy.verify(x509_proxy_issuer.get_pubkey()) < 1:
        raise ProxyException("Failed to verify the proxy, maybe signed with the wrong private key?")

    # Validate the subject
    subject = x509_proxy.get_subject().as_text().split(', ')
    issuer  = x509_proxy.get_issuer().as_text().split(', ')
    if subject[:-1] != issuer:
        raise ProxyException(
            "The subject and the issuer of the proxy do not match: %s != %s" %
            (x509_proxy.get_subject().as_text(), x509_proxy.get_issuer().as_text())
        )
    elif not subject[-1].startswith('CN='):
        raise ProxyException("Missing trailing Common Name in the proxy")
    else:
        log.debug("Delegated DN: " + '/'.join(subject))

    return expiration_time


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
    x509_list = _read_x509_list(x509_pem)
    x509_chain = ''.join(map(lambda x: x.as_pem(), x509_list[1:]))
    return x509_list[0].as_pem() + privkey_pem + x509_chain


class DelegationController(BaseController):
    """
    Operations to perform the delegation of credentials
    """

    def __init__(self):
        """
        Constructor
        """
        M2Crypto.threading.init()

        vomses_dir = '/etc/vomses'
        vo_set = set()
        try:
            vomses = os.listdir(vomses_dir)
            for voms in vomses:
                voms_cfg = os.path.join(vomses_dir, voms)
                lines = filter(
                    lambda l: len(l) and l[0] != '#',
                    map(str.strip, open(voms_cfg).readlines())
                )
                for l in lines:
                    vo_set.add(shlex.split(l)[0])
            self.vo_list = list(sorted(vo_set))
        except:
            pass

    @require_certificate
    def certificate(self):
        """
        Returns the user certificate
        """
        response.headers['Content-Type'] = 'application/x-pem-file'
        n = 0
        full_cert = ''
        cert = request.environ.get('SSL_CLIENT_CERT', None)
        while cert:
            full_cert += cert
            cert = request.environ.get('SSL_CLIENT_CERT_CHAIN_%d' % n, None)
            n += 1
        if len(full_cert) > 0:
            return full_cert
        else:
            return None

    @jsonify
    def whoami(self):
        """
        Returns the active credentials of the user
        """
        whoami = request.environ['fts3.User.Credentials']
        whoami.base_id = str(get_base_id())
        for vo in whoami.vos:
            whoami.vos_id.append(str(get_vo_id(vo)))
        return whoami

    @doc.return_type('dateTime')
    @jsonify
    def view(self, dlg_id, start_response):
        """
        Get the termination time of the current delegated credential, if any
        """
        user = request.environ['fts3.User.Credentials']

        if dlg_id != user.delegation_id:
            raise HTTPForbidden('The requested ID and the credentials ID do not match')

        cred = Session.query(Credential).get((user.delegation_id, user.user_dn))
        if not cred:
            return None
        else:
            return {
                'termination_time': cred.termination_time,
                'voms_attrs': cred.voms_attrs.split('\n')
            }

    @doc.response(403, 'The requested delegation ID does not belong to the user')
    @doc.response(404, 'The credentials do not exist')
    @doc.response(204, 'The credentials were deleted successfully')
    @require_certificate
    def delete(self, dlg_id, start_response):
        """
        Delete the delegated credentials from the database
        """
        user = request.environ['fts3.User.Credentials']

        if dlg_id != user.delegation_id:
            raise HTTPForbidden('The requested ID and the credentials ID do not match')

        cred = Session.query(Credential).get((user.delegation_id, user.user_dn))
        if not cred:
            raise HTTPNotFound('Delegated credentials not found')
        else:
            try:
                Session.delete(cred)
                Session.commit()
            except Exception:
                Session.rollback()
                raise
            start_response('204 No Content', [])
            return ['']

    @doc.response(403, 'The requested delegation ID does not belong to the user')
    @doc.response(200, 'The request was generated succesfully')
    @doc.return_type('PEM encoded certificate request')
    @require_certificate
    def request(self, dlg_id, start_response):
        """
        First step of the delegation process: get a certificate request

        The returned certificate request must be signed with the user's original
        credentials.
        """
        user = request.environ['fts3.User.Credentials']

        if dlg_id != user.delegation_id:
            raise HTTPForbidden('The requested ID and the credentials ID do not match')

        credential_cache = Session.query(CredentialCache)\
            .get((user.delegation_id, user.user_dn))

        user_cert = self.certificate()
        if user_cert:
            user_key = X509.load_cert_string(user_cert)
            request_key_len = user_key.get_pubkey().size()*8
        else:
            request_key_len = 2048

        cached = credential_cache is not None and credential_cache.cert_request is not None

        if not cached or request_key_len != EVP.load_key_string(credential_cache.priv_key).size()*8:
            (x509_request, private_key) = _generate_proxy_request(key_len=request_key_len)
            credential_cache = CredentialCache(dlg_id=user.delegation_id, dn=user.user_dn,
                                               cert_request=x509_request.as_pem(),
                                               priv_key=private_key.as_pem(cipher=None),
                                               voms_attrs=' '.join(user.voms_cred))
            try:
                Session.merge(credential_cache)
                Session.commit()
            except Exception:
                Session.rollback()
                raise
            log.debug("Generated new credential request for %s" % dlg_id)
        else:
            log.debug("Using cached request for %s" % dlg_id)        

        start_response('200 Ok', [('X-Delegation-ID', str(credential_cache.dlg_id)),
                                  ('Content-Type', 'text/plain')])
        return [credential_cache.cert_request]

    @doc.input('Signed certificate', 'PEM encoded certificate')
    @doc.response(403, 'The requested delegation ID does not belong to the user')
    @doc.response(400, 'The proxy failed the validation process')
    @doc.response(201, 'The proxy was stored successfully')
    @require_certificate
    def credential(self, dlg_id, start_response):
        """
        Second step of the delegation process: put the generated certificate

        The certificate being PUT will have to pass the following validation:
            - There is a previous certificate request done
            - The certificate subject matches the certificate issuer + '/CN=Proxy'
            - The certificate modulus matches the stored private key modulus
        """
        user = request.environ['fts3.User.Credentials']

        if dlg_id != user.delegation_id:
            raise HTTPForbidden('The requested ID and the credentials ID do not match')

        credential_cache = Session.query(CredentialCache)\
            .get((user.delegation_id, user.user_dn))
        if credential_cache is None:
            raise HTTPBadRequest('No credential cache found')

        x509_proxy_pem = request.body
        log.debug("Received delegated credentials for %s" % dlg_id)
        log.debug(x509_proxy_pem)

        try:
            expiration_time = _validate_proxy(x509_proxy_pem, credential_cache.priv_key)
            x509_full_proxy_pem = _build_full_proxy(x509_proxy_pem, credential_cache.priv_key)
        except ProxyException, e:
            raise HTTPBadRequest('Could not process the proxy: ' + str(e))

        credential = Credential(dlg_id           = user.delegation_id,
                                dn               = user.user_dn,
                                proxy            = x509_full_proxy_pem,
                                voms_attrs       = credential_cache.voms_attrs,
                                termination_time = expiration_time)

        try:
            Session.merge(credential)
            Session.commit()
        except Exception:
            Session.rollback()
            raise

        start_response('201 Created', [])
        return ['']

    @doc.input('List of voms commands', 'array')
    @doc.response(403, 'The requested delegation ID does not belong to the user')
    @doc.response(400, 'Could not understand the request')
    @doc.response(424, 'The obtention of the VOMS extensions failed')
    @doc.response(203, 'The obtention of the VOMS extensions succeeded')
    @require_certificate
    def voms(self, dlg_id, start_response):
        """
        Generate VOMS extensions for the delegated proxy

        The input must be a json-serialized list of strings, where each strings
        is a voms command (i.e. ["dteam", "dteam:/dteam/Role=lcgadmin"])
        """
        user = request.environ['fts3.User.Credentials']

        if dlg_id != user.delegation_id:
            raise HTTPForbidden('The requested ID and the credentials ID do not match')

        try:
            voms_list = json.loads(request.body)
            log.debug("VOMS request received for %s: %s" % (dlg_id, ', '.join(voms_list)))
            if not isinstance(voms_list, types.ListType):
                raise Exception('Expecting a list of strings')
        except Exception, e:
            raise HTTPBadRequest(str(e))

        credential = Session.query(Credential)\
            .get((user.delegation_id, user.user_dn))

        if credential.termination_time <= datetime.utcnow():
            raise HTTPForbidden('Delegated proxy already expired')

        try:
            voms_client = voms.VomsClient(credential.proxy)
            (new_proxy, new_termination_time) = voms_client.init(voms_list)
        except voms.VomsException, e:
            # Error generating the proxy because of the request itself
            raise HTTPMethodFailure(str(e))

        credential.proxy = new_proxy
        credential.termination_time = new_termination_time
        credential.voms_attrs = ' '.join(voms_list)

        try:
            Session.merge(credential)
            Session.commit()
        except Exception:
            Session.rollback()
            raise

        start_response('203 Non-Authoritative Information', [('Content-Type', 'text/plain')])
        return [str(new_termination_time)]

    @require_certificate
    def delegation_page(self):
        """
        Render an HTML form to delegate the credentials
        """
        user = request.environ['fts3.User.Credentials']
        return render(
            '/delegation.html', extra_vars={
                'user': user,
                'vos': self.vo_list,
                'certificate': request.environ.get('SSL_CLIENT_CERT', None),
                'site': config['fts3.SiteName']
            }
        )

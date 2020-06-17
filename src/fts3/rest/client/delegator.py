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

from datetime import datetime, timedelta
from M2Crypto import X509, ASN1, m2, Err
try:
    from M2Crypto.ASN1 import UTC
except:
    from pytz import utc as UTC
import ctypes
try:
    import simplejson as json
except:
    import json
import logging
import platform
import sys
import time

from exceptions import *

log = logging.getLogger(__name__)

# See https://bugzilla.osafoundation.org/show_bug.cgi?id=7530
# for an explanation on all this mess
# TL;DR: M2Crypto fails to properly initialize the internal structure, which
# results eventually in segfaults
class M2Ctx(ctypes.Structure):
    _fields_ = [
        ('flags', ctypes.c_int),
        ('issuer_cert', ctypes.c_void_p),
        ('subject_cert', ctypes.c_void_p),
        ('subject_req', ctypes.c_void_p),
        ('crl', ctypes.c_void_p),
        ('db_meth', ctypes.c_void_p),
        ('db', ctypes.c_void_p),
    ]


def _init_m2_ctx(m2_ctx, issuer=None):
    ctx = M2Ctx.from_address(int(m2_ctx))
    ctx.flags = 0
    ctx.subject_cert = None
    ctx.subject_req = None
    ctx.crl = None
    if issuer is None:
        ctx.issuer_cert = None
    else:
        ctx.issuer_cert = int(issuer.x509)


def _workaround_new_extension(name, value, critical=False, issuer=None, _pyfree=1):
    # m2crypto removes x509v3_lhash with 0.25.1
    try:
        ctx = m2.x509v3_set_nconf()
        if ctx is None:
            raise MemoryError()
        _init_m2_ctx(ctx, issuer)
        x509_ext_ptr = m2.x509v3_ext_conf(None, ctx, name, value)
    except AttributeError:
        lhash = m2.x509v3_lhash()
        ctx = m2.x509v3_set_conf_lhash(lhash)
        _init_m2_ctx(ctx, issuer)
        x509_ext_ptr = m2.x509v3_ext_conf(lhash, ctx, name, value)

    if x509_ext_ptr is None:
        raise Exception('Could not create the X509v3 extension')

    x509_ext = X509.X509_Extension(x509_ext_ptr, _pyfree)
    x509_ext.set_critical(critical)
    return x509_ext


def _m2crypto_extensions_broken():
    (dist, version, id) = platform.linux_distribution(full_distribution_name=False)
    if dist.lower() == 'redhat' and int(version.split('.')[0]) < 6:
        return True
    return False


def _add_rfc3820_extensions(proxy):
    proxy.add_ext(X509.new_extension(
        'proxyCertInfo',
        'critical,language:Inherit all',
        critical=True
    ))


class Delegator(object):

    nid = {'C'                      : m2.NID_countryName,
           'SP'                     : m2.NID_stateOrProvinceName,
           'ST'                     : m2.NID_stateOrProvinceName,
           'stateOrProvinceName'    : m2.NID_stateOrProvinceName,
           'L'                      : m2.NID_localityName,
           'localityName'           : m2.NID_localityName,
           'O'                      : m2.NID_organizationName,
           'organizationName'       : m2.NID_organizationName,
           'OU'                     : m2.NID_organizationalUnitName,
           'organizationUnitName'   : m2.NID_organizationalUnitName,
           'CN'                     : m2.NID_commonName,
           'commonName'             : m2.NID_commonName,
           'Email'                  : m2.NID_pkcs9_emailAddress,
           'emailAddress'           : m2.NID_pkcs9_emailAddress,
           'serialNumber'           : m2.NID_serialNumber,
           'SN'                     : m2.NID_surname,
           'surname'                : m2.NID_surname,
           'GN'                     : m2.NID_givenName,
           'givenName'              : m2.NID_givenName,
           'DC'                     : 391
           }

    def __init__(self, context):
        self.context = context

    def _get_delegation_id(self):
        r = json.loads(self.context.get('/whoami'))
        return r['delegation_id']

    def _get_remaining_life(self, delegation_id):
        r = self.get_info(delegation_id)
        if r is None:
            return None
        else:
            expiration_time = datetime.strptime(r['termination_time'], '%Y-%m-%dT%H:%M:%S')
            return expiration_time - datetime.utcnow()

    def _get_proxy_request(self, delegation_id):
        request_url = '/delegation/' + delegation_id + '/request'
        request_pem = self.context.get(request_url)
        x509_request = X509.load_request_string(request_pem)
        if x509_request.verify(x509_request.get_pubkey()) != 1:
            raise ServerError('Error verifying signature on the request:', Err.get_error())
        # Return
        return x509_request

    def _sign_request(self, x509_request, lifetime):
        not_before = ASN1.ASN1_UTCTIME()
        not_before.set_datetime(datetime.now(UTC))
        not_after = ASN1.ASN1_UTCTIME()
        not_after.set_datetime(datetime.now(UTC) + lifetime)

        proxy_subject = X509.X509_Name()
        for entry in self.context.x509.get_subject():
            ret = m2.x509_name_add_entry(proxy_subject._ptr(), entry._ptr(), -1, 0)
            if ret == 0:
                raise Exception(
                    "%s: '%s'" % (m2.err_reason_error_string(m2.err_get_error()), entry)
                )

        proxy = X509.X509()
        proxy.set_serial_number(self.context.x509.get_serial_number())
        proxy.set_version(x509_request.get_version())
        proxy.set_issuer(self.context.x509.get_subject())
        proxy.set_pubkey(x509_request.get_pubkey())

        # Extensions are broken in SL5!!
        if _m2crypto_extensions_broken():
            log.warning("X509v3 extensions disabled!")
        else:
            # X509v3 Basic Constraints
            proxy.add_ext(X509.new_extension('basicConstraints', 'CA:FALSE', critical=True))
            # X509v3 Key Usage
            proxy.add_ext(X509.new_extension('keyUsage', 'Digital Signature, Key Encipherment', critical=True))
            #X509v3 Authority Key Identifier
            identifier_ext = _workaround_new_extension(
                'authorityKeyIdentifier', 'keyid', critical=False, issuer=self.context.x509
            )
            proxy.add_ext(identifier_ext)

        any_rfc_proxies = False
        # FTS-1217 Ignore the user input and select the min proxy lifetime available on the list
        min_cert_lifetime = self.context.x509_list[0].get_not_after()
        for cert in self.context.x509_list:
            if cert.get_not_after().get_datetime() < min_cert_lifetime.get_datetime():
                not_after = cert.get_not_after()
                min_cert_lifetime = cert.get_not_after()
            try:
                cert.get_ext('proxyCertInfo')
                any_rfc_proxies = True
            except:
                pass

        proxy.set_not_after(not_after)
        proxy.set_not_before(not_before)

        if any_rfc_proxies:
            if _m2crypto_extensions_broken():
                raise NotImplementedError("X509v3 extensions are disabled, so RFC proxies can not be generated!")
            else:
                _add_rfc3820_extensions(proxy)

        if any_rfc_proxies:
            m2.x509_name_set_by_nid(proxy_subject._ptr(), X509.X509_Name.nid['commonName'], str(int(time.time())))
        else:
            m2.x509_name_set_by_nid(proxy_subject._ptr(), X509.X509_Name.nid['commonName'], 'proxy')

        proxy.set_subject(proxy_subject)
        proxy.set_version(2)
        proxy.sign(self.context.evp_key, 'sha1')

        return proxy

    def _put_proxy(self, delegation_id, x509_proxy):
        self.context.put('/delegation/' + delegation_id + '/credential', x509_proxy)

    def _full_proxy_chain(self, x509_proxy):
        chain = x509_proxy.as_pem()
        for cert in self.context.x509_list:
            chain += cert.as_pem()
        return chain

    def get_info(self, delegation_id=None):
        if delegation_id is None:
            delegation_id = self._get_delegation_id()
        return json.loads(self.context.get('/delegation/' + delegation_id))

    def delegate(self, lifetime=timedelta(hours=7), force=False, delegate_when_lifetime_lt=timedelta(hours=2)):
        try:
            delegation_id = self._get_delegation_id()
            log.debug("Delegation ID: " + delegation_id)

            remaining_life = self._get_remaining_life(delegation_id)

            if remaining_life is None:
                log.debug("No previous delegation found")
            elif remaining_life <= timedelta(0):
                log.debug("The delegated credentials expired")
            elif self.context.access_method == 'oauth2' or remaining_life >= delegate_when_lifetime_lt:
                if self.context.access_method == 'oauth2' or not force:
                    log.debug("Not bothering doing the delegation")
                    return delegation_id
                else:
                    log.debug("Delegation not expired, but this is a forced delegation")

            # Ask for the request
            log.debug("Delegating")
            x509_request = self._get_proxy_request(delegation_id)

            # Sign request
            log.debug("Signing request")
            x509_proxy = self._sign_request(x509_request, lifetime)
            x509_proxy_pem = self._full_proxy_chain(x509_proxy)

            # Send the signed proxy
            self._put_proxy(delegation_id, x509_proxy_pem)

            return delegation_id

        except Exception, e:
            raise ClientError(str(e)), None, sys.exc_info()[2]

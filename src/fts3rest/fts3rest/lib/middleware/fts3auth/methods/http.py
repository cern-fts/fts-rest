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

import re, time, dateutil.parser, logging
from base64 import b64decode
from M2Crypto import X509, EVP
from fts3rest.lib.middleware.fts3auth.credentials import InvalidCredentials, vo_from_fqan, build_vo_from_dn, generate_delegation_id

def do_authentication(credentials, env):
    """
    Retrieve credentials from HTTP headers set by WebFTS
    Authorization: Signed-Cert hash="sha256-or-whatever", ts="ISO-timestamp", cert="base64-certificate", sign="base64-signature"
    """
    if not 'HTTP_AUTHORIZATION' in env or not env['HTTP_AUTHORIZATION'].lower().startswith('signed-cert'):
        return False

    log = logging.getLogger(__name__)

    # Parse Authorization header into key="value" pairs
    cred = dict((k.lower(), v) for k, v in re.findall(r"(\w+)\s*=\s*\"([^\"]+)\"", env['HTTP_AUTHORIZATION']))

    if not 'cert' in cred or not 'hash' in cred or not 'sign' in cred or not 'ts' in cred:
        log.info("Wrong format of signed-cert authorization header")
        return False

    try:
        cert = b64decode(cred['cert'])
        sign = b64decode(cred['sign'])
        ts = dateutil.parser.parse(cred['ts']).strftime('%s')
    except (TypeError, ValueError):
        log.info("Cannot decode certificate, signature or timestamp")
        raise InvalidCredentials()

    td = abs(int(time.mktime(time.gmtime())) - int(ts))
    if td > 60:
        log.info("Authorization has expired by " + str(td) + " seconds")
        raise InvalidCredentials()

    x509 = X509.load_cert_string(cert, X509.FORMAT_DER)
    pubkey = x509.get_pubkey().get_rsa()
    verify = EVP.PKey()
    verify.assign_rsa(pubkey)
    verify.reset_context(cred['hash'])
    verify.verify_init()
    verify.verify_update(cert)
    verify.verify_update(cred['ts'])
    if not verify.verify_final(sign):
        log.info("Signature verification failed")
        raise InvalidCredentials()

    credentials.user_dn = '/'+'/'.join(x509.get_subject().as_text().split(', '))

#   for each VOMS attr:
#       fqan = #magic
#       vo = vo_from_fqan(fqan)
#       credentials.voms_cred.append(fqan)
#       if vo not in credentials.vos and vo:
#           credentials.vos.append(vo)

    # Generate the delegation ID
    credentials.delegation_id = generate_delegation_id(credentials.user_dn, credentials.voms_cred)
    # If no vo information is available, build a 'virtual vo' for this user
    if not credentials.vos:
        credentials.vos.append(build_vo_from_dn(credentials.user_dn))
    credentials.method = 'certificate'
    return True

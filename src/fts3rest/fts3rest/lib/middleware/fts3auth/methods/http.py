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

import re
import time
import dateutil.parser
import logging
import urllib
from base64 import b64decode
from M2Crypto import X509, EVP
from m2ext import SSL

from fts3rest.lib.middleware.fts3auth.credentials import InvalidCredentials, build_vo_from_dn, generate_delegation_id, vo_from_fqan
from fts3rest.lib.helpers.voms import VomsClient


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
	proxy = None
	try:
		proxy =  b64decode(cred['prx'])
		log.info("found a proxy on the request")
	except:
		pass
        ts = dateutil.parser.parse(cred['ts']).strftime('%s')
    except (TypeError, ValueError):
        log.info("Cannot decode certificate, signature or timestamp")
        raise InvalidCredentials("Cannot decode certificate, signature or timestamp")

    td = abs(int(time.mktime(time.gmtime())) - int(ts))
    if td > 600:
        log.info("Authorization has expired by " + str(td) + " seconds")
        raise InvalidCredentials("Authorization has expired by " + str(td) + " seconds")
    if proxy:
	x509 = X509.load_cert_string(proxy, X509.FORMAT_DER)
	fileCertString = X509.load_cert_string(cert, X509.FORMAT_DER)
	#print the cert DN
	certDN =  '/' + '/'.join(fileCertString.get_subject().as_text().split(', '))
        proxyDN = '/' + '/'.join(x509.get_subject().as_text().split(', '))
	log.info("cert DN: "+ certDN)
	chain_pem =fileCertString.as_pem()
 	chain_pem += x509.as_pem()
        chain = X509.load_cert_string(chain_pem)
    else:
	x509 = X509.load_cert_string(cert, X509.FORMAT_DER)
        certDN = '/' + '/'.join(x509.get_subject().as_text().split(', '))
    pubkey = x509.get_pubkey().get_rsa()
    verify = EVP.PKey()
    verify.assign_rsa(pubkey)
    verify.reset_context(cred['hash'])
    verify.verify_init()
    if proxy:
    	verify.verify_update(proxy)
    else:
	verify.verify_update(cert)
    verify.verify_update(cred['ts'])
    if not verify.verify_final(sign):
        log.info("Signature verification failed")
        raise InvalidCredentials()

    ctx = SSL.Context()
    ctx.load_verify_locations(capath="/etc/grid-security/certificates")
    if proxy:
	log.info("Trying to verify the proxy")
	if not ctx.validate_certificate(chain):
		log.info("Certificate verification failed")
        	raise InvalidCredentials("Certificate verification failed")
    elif not ctx.validate_certificate(x509):
        log.info("Certificate verification failed")
        raise InvalidCredentials("Certificate verification failed")
    credentials.user_dn = certDN
    if proxy:
	credentials.dn.append(proxyDN)
    credentials.dn.append(credentials.user_dn)
    if 'SSL_CLIENT_S_DN' in env:
        credentials.dn.append(urllib.unquote_plus(env['SSL_CLIENT_S_DN']))
    if proxy:
    	voms_client = VomsClient(chain_pem)
	log.info("proxy path: " + voms_client.proxy_path)
	fqans = voms_client.get_proxy_fqans()
	for fqan in fqans:
		vo = vo_from_fqan(fqan)
		credentials.voms_cred.append(fqan)
		if vo not in credentials.vos and vo:
			credentials.vos.append(vo)

    # Generate the delegation ID
    credentials.delegation_id = generate_delegation_id(credentials.user_dn, credentials.voms_cred)
    # If no vo information is available, build a 'virtual vo' for this user
    if not credentials.vos:
        credentials.vos.append(build_vo_from_dn(credentials.user_dn))
    credentials.method = 'certificate'
    return True

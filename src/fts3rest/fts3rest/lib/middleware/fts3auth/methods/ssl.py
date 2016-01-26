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

import urllib

from fts3rest.lib.middleware.fts3auth.credentials import vo_from_fqan, build_vo_from_dn, generate_delegation_id
import logging


def _mod_gridsite_authn(credentials, env):
    """
    Retrieve credentials from GRST_ variables set by mod_gridsite
    """
    grst_index = 0
    grst_env = 'GRST_CRED_AURI_%d' % grst_index
    while grst_env in env:
        cred = env[grst_env]

        if cred.startswith('dn:'):
            credentials.dn.append(urllib.unquote_plus(cred[3:]))
        elif cred.startswith('fqan:'):
            fqan = urllib.unquote_plus(cred[5:])
            vo = vo_from_fqan(fqan)
            credentials.voms_cred.append(fqan)
            if vo not in credentials.vos and vo:
                credentials.vos.append(vo)

        grst_index += 1
        grst_env = 'GRST_CRED_AURI_%d' % grst_index
    return len(credentials.dn) > 0


def _mod_ssl_authn(credentials, env):
    """
    Retrieve credentials from SSL_ variables set by mod_ssl
    """
    if 'SSL_CLIENT_S_DN' in env:
        credentials.dn.append(urllib.unquote_plus(env['SSL_CLIENT_S_DN']))
        return True
    return False

def do_authentication(credentials, env):
    """
    Try with a proxy or certificate, via mod_gridsite or mod_ssl
    """
    got_creds = _mod_gridsite_authn(credentials, env) or _mod_ssl_authn(credentials, env)
    if not got_creds:
        return False
    # If more than one dn, pick first one
    if len(credentials.dn) > 0:
        credentials.user_dn = credentials.dn[0]
    # Generate the delegation ID
    if credentials.user_dn is not None:
        credentials.delegation_id = generate_delegation_id(credentials.user_dn, credentials.voms_cred)
    # If no vo information is available, build a 'virtual vo' for this user
    if not credentials.vos and credentials.user_dn:
        credentials.vos.append(build_vo_from_dn(credentials.user_dn))
    credentials.method = 'certificate'
    # If the user's DN matches the host DN, then grant all
    host_dn = env.get('SSL_SERVER_S_DN', None)
    if host_dn and host_dn == credentials.user_dn:
        credentials.is_root = True
    else:
        if '/' not in str(host_dn):
            host_dn = str(host_dn).replace(',','/')
            host_dn ='/'+'/'.join(reversed(str(host_dn).split('/')))
            if host_dn == credentials.user_dn :
                credentials.is_root = True
    return True

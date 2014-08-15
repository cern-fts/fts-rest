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

from fts3rest.lib.oauth2provider import FTS3OAuth2ResourceProvider
from fts3rest.lib.middleware.fts3auth.credentials import vo_from_fqan, build_vo_from_dn


def do_authentication(credentials, env):
    """
    The user will be the one who gave the bearer token
    """
    res_provider = FTS3OAuth2ResourceProvider(env)
    db_creds = res_provider.get_credentials()
    if db_creds is None:
        return False
    credentials.dn.append(db_creds.dn)
    credentials.user_dn = db_creds.dn
    credentials.delegation_id = db_creds.dlg_id
    if db_creds.voms_attrs:
        for fqan in db_creds.voms_attrs.split('\n'):
            credentials.voms_cred.append(fqan)
            credentials.vos.append(vo_from_fqan(fqan))
    else:
        credentials.vos.append(build_vo_from_dn(credentials.user_dn))
    credentials.method = 'oauth2'
    return True

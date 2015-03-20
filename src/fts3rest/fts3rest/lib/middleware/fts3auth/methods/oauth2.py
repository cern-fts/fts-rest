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

import types
from fts3rest.lib.oauth2provider import FTS3OAuth2ResourceProvider
from fts3rest.lib.middleware.fts3auth.credentials import vo_from_fqan, build_vo_from_dn, InvalidCredentials


def _oauth2_get_granted_level_for(self, operation):
    if operation not in self.oauth2_scope:
        return None
    return self.get_granted_level_for_overriden(operation)


def do_authentication(credentials, env):
    """
    The user will be the one who gave the bearer token
    """
    res_provider = FTS3OAuth2ResourceProvider(env)
    authn = res_provider.get_authorization()
    if authn is None:
        return False
    if not authn.is_valid:
        if authn.error == 'access_denied':
            raise InvalidCredentials('Invalid OAuth2 credentials')
        return False

    credentials.dn.append(authn.credentials.dn)
    credentials.user_dn = authn.credentials.dn
    credentials.delegation_id = authn.credentials.dlg_id
    if authn.credentials.voms_attrs:
        for fqan in authn.credentials.voms_attrs.split('\n'):
            credentials.voms_cred.append(fqan)
            credentials.vos.append(vo_from_fqan(fqan))
    else:
        credentials.vos.append(build_vo_from_dn(credentials.user_dn))
    credentials.method = 'oauth2'

    # Override get_granted_level_for so we can filter by the scope
    setattr(credentials, 'oauth2_scope', authn.scope)
    setattr(credentials, 'get_granted_level_for_overriden', credentials.get_granted_level_for)
    setattr(credentials, 'get_granted_level_for', types.MethodType(_oauth2_get_granted_level_for, credentials))

    return True

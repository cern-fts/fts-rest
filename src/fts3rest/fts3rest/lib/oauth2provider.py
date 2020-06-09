#   Copyright notice:
#   Copyright CERN, 2014.
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

import logging
from datetime import datetime, timedelta
import json
import jwt
import pylons
from fts3rest.lib.base import Session
from fts3rest.lib.middleware.fts3auth.constants import VALID_OPERATIONS
from fts3rest.lib.middleware.fts3auth.credentials import generate_delegation_id
from fts3rest.lib.oauth2lib.provider import AuthorizationProvider, ResourceAuthorization, ResourceProvider
from fts3rest.lib.openidconnect import oidc_manager
from jwcrypto.jwk import JWK


from fts3.model.credentials import Credential, CredentialCache
from fts3.model.oauth2 import OAuth2Application, OAuth2Code, OAuth2Token

log = logging.getLogger(__name__)


class FTS3OAuth2AuthorizationProvider(AuthorizationProvider):
    """
    OAuth2 Authorization provider, specific methods
    """

    def validate_client_id(self, client_id):
        app = Session.query(OAuth2Application).get(client_id)
        return app is not None

    def validate_client_secret(self, client_id, client_secret):
        app = Session.query(OAuth2Application).get(client_id)
        if not app:
            return False
        return app.client_secret == client_secret

    def validate_scope(self, client_id, scope):
        app = Session.query(OAuth2Application).get(client_id)
        for s in scope:
            if s not in VALID_OPERATIONS or s not in app.scope:
                return False
        return True

    def validate_redirect_uri(self, client_id, redirect_uri):
        app = Session.query(OAuth2Application).get(client_id)
        if not app:
            return False
        return redirect_uri in app.redirect_to.split()

    def validate_access(self):
        user = pylons.request.environ['fts3.User.Credentials']
        return user is not None

    def from_authorization_code(self, client_id, code, scope):
        code = Session.query(OAuth2Code).get(code)
        if not code:
            return None
        return {'dlg_id': code.dlg_id}

    def from_refresh_token(self, client_id, refresh_token, scope):
        code = Session.query(OAuth2Token).get((client_id, refresh_token))
        if not code:
            return None
        return {'dlg_id': code.dlg_id}

    def _insert_user(self, user):
        # We will need the user in t_credential_cache at least!
        cred = Session.query(CredentialCache).filter(CredentialCache.dlg_id == user.delegation_id).first()
        if not cred:
            cred = CredentialCache(
                dlg_id=user.delegation_id,
                dn=user.user_dn,
                cert_request=None,
                priv_key=None,
                voms_attrs='\n'.join(user.voms_cred)
            )
            Session.merge(cred)

    def persist_authorization_code(self, client_id, code, scope):
        user = pylons.request.environ['fts3.User.Credentials']
        self._insert_user(user)
        # Remove previous codes
        Session.query(OAuth2Code).filter(
            (OAuth2Code.client_id == client_id) & (OAuth2Code.dlg_id == user.delegation_id)
        ).delete()
        # Token
        code = OAuth2Code(
            client_id=client_id,
            code=code,
            scope=scope,
            dlg_id=user.delegation_id
        )
        Session.merge(code)
        Session.commit()

    def is_already_authorized(self, dlg_id, client_id, scope):
        code = Session.query(OAuth2Token).filter(
            (OAuth2Token.client_id == client_id) & (OAuth2Token.dlg_id == dlg_id)
        )
        if scope:
            code = code.filter(OAuth2Token.scope == scope)
        code = code.all()
        if len(code) > 0:
            return True
        else:
            return None

    def persist_token_information(self, client_id, scope, access_token,
                                  token_type, expires_in, refresh_token,
                                  data):
        # Remove previous tokens
        Session.query(OAuth2Token).filter(
            (OAuth2Token.dlg_id == data['dlg_id']) & (OAuth2Token.client_id == client_id)
        ).delete()
        # Add new
        token = OAuth2Token(
            client_id=client_id,
            scope=scope,
            access_token=access_token,
            token_type=token_type,
            expires=datetime.utcnow() + timedelta(seconds=expires_in),
            refresh_token=refresh_token,
            dlg_id=data['dlg_id']
        )
        Session.merge(token)
        Session.commit()

    def discard_authorization_code(self, client_id, code):
        auth_code = Session.query(OAuth2Code).get(code)
        if auth_code is not None:
            Session.delete(auth_code)
            Session.commit()

    def discard_refresh_token(self, client_id, refresh_token):
        token = Session.query(OAuth2Token).get((client_id, refresh_token))
        if token is not None:
            Session.delete(token)
            Session.commit()


class FTS3ResourceAuthorization(ResourceAuthorization):
    dlg_id = None
    credentials = None
    scope = None


class FTS3OAuth2ResourceProvider(ResourceProvider):
    """
    OAuth2 resource provider
    """

    def __init__(self, environ, config):
        self.environ = environ
        self.config = config

    @property
    def authorization_class(self):
        return FTS3ResourceAuthorization

    def get_authorization_header(self):
        return self.environ.get('HTTP_AUTHORIZATION', None)

    def validate_access_token(self, access_token, authorization):
        """
        Validate access token offline or online

        Description of the algorithm:
        - Validate access token offline (using cached keys) or online (using introspection RFC 7662).
        - If a credential already exists in the DB and has not expired, the new token is discarded and the old
        credential is used.
        - If a credential already exists in the DB but has expired, delete it.
        - If there's no credential, Instrospect the token to get additional information (if not done before). Then,
        exchange the access token with a refresh token. Store both tokens in the DB.

        :param access_token:
        :param authorization: attribute .is_valid is set to True if validation successful
        """
        authorization.is_valid = False

        if self._should_validate_offline():
            valid, credential = self._validate_token_offline(access_token)
        else:
            valid, credential = self._validate_token_online(access_token)
        if not valid:
            log.warning("Access token provided is not valid")
            return

        # Check if a credential already exists in the DB
        credential_db = Session.query(Credential).filter(Credential.dn == credential['sub']).first()
        if credential_db and credential_db.expired():
            log.debug("credential_db_has_expired")
            Session.delete(credential_db)
            Session.commit()
            credential_db = None

        if not credential_db:
            if self._should_validate_offline():
                log.debug("offline and not in db")
                # Introspect to obtain additional information
                valid, credential = self._validate_token_online(access_token)
                if not valid:
                    log.debug("Access token provided is not valid")
                    return
            # Store credential in DB
            log.debug("Store credential in DB")
            dlg_id = generate_delegation_id(credential['sub'], "")
            try:
                if 'wlcg' in credential['iss']:
                    # Hardcoded scope and audience for wlcg tokens. To change once the wlcg standard evolves
                    scope = 'offline_access openid storage.read:/ storage.modify:/'
                    audience = 'https://wlcg.cern.ch/jwt/v1/any'
                    access_token, refresh_token = oidc_manager.generate_token_with_scope(credential['iss'],
                                                                                         access_token, scope, audience)
                else:
                    refresh_token = oidc_manager.generate_refresh_token(credential['iss'], access_token)
            except Exception:
                return
            credential_db = self._save_credential(dlg_id, credential['sub'],
                                                  str(access_token) + ':' + str(refresh_token),
                                                  self._generate_voms_attrs(credential),
                                                  datetime.utcfromtimestamp(credential['exp']))

        authorization.is_oauth = True
        authorization.token = credential_db.proxy.split(':')[0]
        authorization.dlg_id = credential_db.dlg_id
        authorization.expires_in = credential_db.termination_time - datetime.utcnow()
        if authorization.expires_in > timedelta(seconds=0):
            authorization.credentials = self._get_credentials(credential_db.dlg_id)
            if authorization.credentials:
                authorization.is_valid = True

    def _get_credentials(self, dlg_id):
        """
        Get the user credentials bound to the authorization token
        """
        return Session.query(Credential).filter(Credential.dlg_id == dlg_id).first()

    def _generate_voms_attrs(self, credential):
        if 'email' in credential:
            if 'username' in credential:
                # 'username' is never there whether offline or online
                return credential['email'] + " " + credential['username']
            else:
                # 'user_id' is there only online
                return credential['email'] + " " + credential['user_id']
        else:
            if 'username' in credential:
                return credential['username'] + " "
            else:
                return credential['user_id'] + " "

    def _validate_token_offline(self, access_token):
        """
        Validate access token using cached information from the provider
        :param access_token:
        :return: tuple(valid, credential) or tuple(False, None)
        """
        log.debug('entered validate_token_offline')
        try:
            unverified_payload = jwt.decode(access_token, verify=False)
            unverified_header = jwt.get_unverified_header(access_token)
            issuer = unverified_payload['iss']
            key_id = unverified_header['kid']
            log.debug('issuer={}, key_id={}'.format(issuer, key_id))

            algorithm = unverified_header.get('alg', 'RS256')
            log.debug('alg={}'.format(algorithm))

            pub_key = oidc_manager.get_provider_key(issuer, key_id)
            log.debug('key={}'.format(pub_key))
            pub_key = JWK.from_json(json.dumps(pub_key.to_dict()))
            log.debug('pubkey={}'.format(pub_key))
            # Verify & Validate
            if 'wlcg' in issuer:
                audience = 'https://wlcg.cern.ch/jwt/v1/any'
                credential = jwt.decode(access_token, pub_key.export_to_pem(), algorithms=[algorithm], audience=audience)
            else:
                credential = jwt.decode(access_token,
                                        pub_key.export_to_pem(),
                                        algorithms=[algorithm],
                                        options={'verify_aud': False} # We don't check audience for non-WLCG token)
                                        )
            log.debug('offline_response::: {}'.format(credential))
        except Exception as ex:
            log.debug(ex)
            log.debug('return False (exception)')
            return False, None
        log.debug('return True, credential')
        return True, credential

    def _validate_token_online(self, access_token):
        """
        Validate access token using Introspection (RFC 7662)
        :param access_token:
        :return: tuple(valid, credential) or tuple(False, None)
        """
        try:
            unverified_payload = jwt.decode(access_token, verify=False)
            issuer = unverified_payload['iss']
            log.debug('issuer={}'.format(issuer))
            response = oidc_manager.introspect(issuer, access_token)
            log.debug('online_response::: {}'.format(response))
            return response["active"], response
        except Exception as ex:
            log.debug('exception {}'.format(ex))
            return False, None

    def _save_credential(self, dlg_id, dn, proxy, voms_attrs, termination_time):
        credential = Credential(
            dlg_id=dlg_id,
            dn=dn,
            proxy=proxy,
            voms_attrs=voms_attrs,
            termination_time=termination_time
        )
        Session.add(credential)
        Session.commit()
        return credential

    def _should_validate_offline(self):
        if 'fts3.ValidateAccessTokenOffline' in self.config:
            option = self.config.get('fts3.ValidateAccessTokenOffline')
            if option == 'False':
                return False
        return True

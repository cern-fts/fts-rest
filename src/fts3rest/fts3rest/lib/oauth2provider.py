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

import pylons
import logging

from datetime import datetime, timedelta
from fts3rest.lib.base import Session
from fts3rest.lib.middleware.fts3auth.constants import VALID_OPERATIONS
from fts3rest.lib.middleware.fts3auth.credentials import generate_delegation_id
from fts3rest.lib.oidc_configuration import oidc_manager
from fts3rest.lib.oauth2lib.provider import AuthorizationProvider, ResourceProvider, ResourceAuthorization
from fts3.model.credentials import CredentialCache, Credential
from fts3.model.oauth2 import OAuth2Application, OAuth2Code, OAuth2Token, OAuth2Providers
from fts3.rest.client.request import Request
from ast import literal_eval
import json

import oic

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
        authorization.is_valid = False

        # Try to first validate the supplied access_token offline in order to avoid the expensive REST query to IAM
        validated_offline = False
        if self._should_validate_offline():
            valid, offline_credential = self._validate_token_offline(access_token)
            if valid:
                # If token is valid, check if this user has been seen before and if yes authorize.
                # If not, validate online in order to get the extra info i.e. email etc
                credential_stored_offline = Session.query(Credential).filter(Credential.dn.like(offline_credential['sub'] + "%")).first()
                if credential_stored_offline:
                    validated_offline = True
            else:
                log.debug("Access token provided is not valid - offline validation")
                return

        if validated_offline:
            credential = credential_stored_offline
        else:
            credential = Session.query(Credential).filter(Credential.proxy.like(access_token + "%")).first()
        if (not credential or credential.expired()):
            # Delete the db entry in case of credential expired before validating the new one
            if credential:
                Session.delete(credential)
                Session.commit()

            requestor = Request(None, None)  # VERIFY:TRUE
            body = {'token': access_token}
            log.debug("About to contact IAM server in order to verify the token")
            credential = json.loads(requestor.method('POST', self.config['fts3.AuthorizationProvider'], body=body,
                                                     user=self.config['fts3.ClientId'],
                                                     passw=self.config['fts3.ClientSecret']))
            if not credential or not credential['active']:
                return

            dlg_id = generate_delegation_id(credential['sub'], "")
            c = Session.query(Credential).filter(Credential.dlg_id == dlg_id).first()
            if c:
                Session.delete(c)
                Session.commit()

            log.debug("Credential is as follows: " + str(credential))

            refresh_credential = self._generate_refresh_token(access_token)
            if refresh_credential:
                log.debug("Refresh credential is as follows: " + str(refresh_credential))
                refresh_token= refresh_credential['refresh_token']
            else:
                refresh_token = ""

            credential = self._save_credential(dlg_id, credential['sub'],
                                               access_token + ':' + refresh_token,
                                               self._generate_voms_attrs(credential),
                                               datetime.utcfromtimestamp(credential['exp']))
            log.debug("credentials stored")

        authorization.is_oauth = True
        authorization.expires_in = credential.termination_time - datetime.utcnow()
        authorization.token = credential.proxy.split(':')[0]
        authorization.dlg_id = credential.dlg_id
        #authorization.scope = token.scope
        if authorization.expires_in > timedelta(seconds=0):
            authorization.credentials = self._get_credentials(credential.dlg_id)
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
                return credential['email'] + " " + credential['username']
            else:
                return credential['email'] + " " + credential['user_id']
        else:
            if 'username' in credential:
                return credential['username'] + " "
            else:
                return credential['user_id'] + " "

    def _validate_token_offline(self, access_token):
        try:
            from jwcrypto import jwk
            import jwt
########### not needed
            jwkProvider = Session.query(OAuth2Providers).filter(OAuth2Providers.provider_url.like(self.config['fts3.AuthorizationProviderJwkEndpoint'] + "%")).first()
            if not jwkProvider:
                requestor = Request(None, None)
                jwksIAM = json.loads(requestor.method('GET', self.config['fts3.AuthorizationProviderJwkEndpoint']))
                if jwksIAM is None:
                    raise  Exception("Failed to contact the provider JWK endpoint")
                oauth2provider = OAuth2Providers(
                    provider_url=self.config['fts3.AuthorizationProviderJwkEndpoint'],
                    provider_jwk=str(jwksIAM).replace("\'","\"").replace("u\"","\""))
                Session.add(oauth2provider)
                Session.commit()
                jwksIAM = oauth2provider.provider_jwk
            else:
                jwksIAM = jwkProvider.provider_jwk
########### not needed end

            unverified_header = jwt.get_unverified_header(access_token)
            issuer = unverified_header['iss']
            key_id = unverified_header['kid']

            client = oidc_manager.clients[issuer]
            issuer_keys = client.keyjar.get_issuer_keys(issuer)

            # jwksIAM contains keys as json/dict
            # Import json key
            kid_id = json.loads(jwksIAM)
            kid_id = kid_id.get("keys")[0].get("kid", "rsa1")
            log.debug("kid id " + kid_id)
            jwks = jwk.JWKSet.from_json(jwksIAM)
            # Extract public key
            pub_key = jwks.get_key(kid_id)
            if pub_key is None:
                err = "Offline token validation failed: not able to acquire the provider public key with kid: " + kid_id
                log.debug(err)
                raise Exception(err)
            # Validate
            credential = jwt.decode(access_token, pub_key.export_to_pem(), algorithm='RS256')
        except Exception as e:
            log.error("Offline token validation failed: " + str(e))
            return False, None
        return True, credential

    def _generate_refresh_token(self, access_token):
        requestor = Request(None, None)  # VERIFY:TRUE
        # Request a refresh token based on this access token through the token-exchange grant-type
        body = {'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
                'subject_token_type': 'urn:ietf:params:oauth:token-type:access_token',
                'subject_token': access_token,
                'scope': 'offline_access openid profile',
                'audience': self.config['fts3.ClientId']}
        refresh_credential = None 
        try:
            refresh_credential = json.loads(requestor.method('POST', self.config['fts3.AuthorizationProviderTokenEndpoint'],
                                                             body=body,
                                                             user=self.config['fts3.ClientId'],
                                                             passw=self.config['fts3.ClientSecret']))
        except Exception as e:
            log.error("Error when requesting a refresh token: " + str(e))
        return refresh_credential

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
        return 'fts3.ValidateAccessTokenOffline' in self.config.keys()

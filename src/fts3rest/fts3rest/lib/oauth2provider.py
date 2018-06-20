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
from fts3rest.lib.oauth2lib.provider import AuthorizationProvider, ResourceProvider, ResourceAuthorization
from fts3.model.credentials import CredentialCache, Credential
from fts3.model.oauth2 import OAuth2Application, OAuth2Code, OAuth2Token
from fts3.rest.client.request import Request
import json

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

        credential = Session.query(Credential).filter(Credential.proxy == access_token).first()
        if not credential or credential.expired():
            # Delete the db entry in case of credential expired before validating the new one
            if credential:
                Session.delete(credential)

            requestor = Request(None, None)  # VERIFY:TRUE
            body = {'token': access_token}
            log.debug("About to contact IAM server")
            credential = json.loads(requestor.method('POST', self.config['fts3.AuthorizationProvider'], body=body,
                                                   user=self.config['fts3.ClientId'],
                                                   passw=self.config['fts3.ClientSecret']))
            if not credential or not credential['active']:
                return

            dlg_id = generate_delegation_id(credential['sub'], "")
            c = Session.query(Credential).filter(Credential.dlg_id == dlg_id).first()
            if c:
                Session.delete(c)

            log.debug("Credential is as follows: " + str(credential))

            credential = Credential(
                dlg_id=dlg_id,
                dn=credential['sub'],
                proxy=access_token,
                voms_attrs=self._generate_voms_attrs(credential),
                termination_time=datetime.utcfromtimestamp(credential['exp'])
            )
            Session.add(credential)
            Session.commit()

        authorization.is_oauth = True
        authorization.expires_in = credential.termination_time - datetime.utcnow()
        authorization.token = credential.proxy
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
            return credential['email'] + " " + credential['user_id']
        else:
            return credential['user_id'] + " "


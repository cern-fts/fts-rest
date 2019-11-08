from oic.oic import Client
from oic.oic.message import RegistrationResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from oic.extension.message import TokenIntrospectionRequest
from oic.extension.message import TokenIntrospectionResponse
from oic.oic.message import Message, AccessTokenResponse
from oic import rndstr
from oic.oic import Grant, Token
from oic.utils import time_util
import jwt
from datetime import datetime, timedelta

import logging
log = logging.getLogger(__name__)


class OIDCmanager:

    def __init__(self):
        self.clients = {}
        self.config = None

    def setup(self, config):
        self.config = config
        self._configure_clients(config['fts3.Providers'])
        self._set_keys_cache_time(int(config['fts3.JWKCacheSeconds']))
        self._retrieve_clients_keys()

    def _configure_clients(self, providers_config):
        # log.debug('provider_info::: {}'.format(client.provider_info))
        for provider in providers_config:
            client = Client(client_authn_method=CLIENT_AUTHN_METHOD)
            # Retrieve well-known configuration
            client.provider_config(provider)
            # Register
            client_reg = RegistrationResponse(client_id=providers_config[provider]['client_id'],
                                              client_secret=providers_config[provider]['client_secret'])
            client.store_registration_info(client_reg)
            self.clients[provider] = client

    def _retrieve_clients_keys(self):
        for provider in self.clients:
            client = self.clients[provider]
            client.keyjar.get_issuer_keys(provider)

    def _set_keys_cache_time(self, cache_time):
        for provider in self.clients:
            client = self.clients[provider]
            keybundles = client.keyjar.issuer_keys[provider]
            log.debug('len(keybundles)={}'.format(len(keybundles)))
            for keybundle in keybundles:
                keybundle.cache_time = cache_time

    def get_provider_key(self, issuer, kid):
        client = self.clients[issuer]
        keys = client.keyjar.get_issuer_keys(issuer)  # List of Keys (from pyjwkest)
        for key in keys:
            if key.kid == kid:
                return key
        raise ValueError("Key with kid {} not found".format(kid))

    def introspect(self, issuer, access_token):
        client = self.clients[issuer]
        response = client.do_any(request_args={'token': access_token},
                                 request=TokenIntrospectionRequest,
                                 response=TokenIntrospectionResponse,
                                 body_type='json',
                                 method='POST',
                                 authn_method="client_secret_basic"
                                 )
        log.debug('introspect_response::: {}'.format(response))
        return response

    def generate_refresh_token(self, issuer, access_token):
        log.debug("enter generate_refresh_token")
        client = self.clients[issuer]
        body = {'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
                'subject_token_type': 'urn:ietf:params:oauth:token-type:access_token',
                'subject_token': access_token,
                'scope': 'offline_access openid profile',
                'audience': client.client_id}
        log.debug("before do any")
        try:
            response = client.do_any(Message,
                                     request_args=body,
                                     endpoint=client.provider_info["token_endpoint"],
                                     body_type='json',
                                     method='POST',
                                     authn_method="client_secret_basic"
                                     )
            response = response.json()
            refresh_token = response['refresh_token']
        except Exception as ex:
            log.debug('exception in refresh token')
            log.debug(ex)
            refresh_token = ""
        log.debug('refresh_token_response::: {}'.format(refresh_token))
        return refresh_token

    def refresh_access_token(self, credential):
        # Request a new access token based on the refresh token
        access_token, refresh_token = credential.proxy.split(':')
        unverified_payload = jwt.decode(access_token, verify=False)
        issuer = unverified_payload['iss']
        client = self.clients[issuer]
        log.debug('refresh_access_token for {}'.format(issuer))

        refresh_session_state = rndstr(50)
        client.grant[refresh_session_state] = Grant()
        client.grant[refresh_session_state].grant_expiration_time = time_util.utc_time_sans_frac() + 60
        #client.grant[refresh_session_state].code = "access_code"
        resp = AccessTokenResponse()
        resp["refresh_token"] = refresh_token
        client.grant[refresh_session_state].tokens.append(Token(resp))
        new_credential = client.do_access_token_refresh(authn_method="client_secret_basic",
                                                        state=refresh_session_state)

        # A new refresh token is optional
        oldrefresh = refresh_token
        refresh_token = new_credential.get('refresh_token', oldrefresh)
        log.debug('new refresh token? {}'.format('refresh_token' in new_credential))
        log.debug('are they the same? {}'.format(refresh_token == oldrefresh))
        # todo? check if refresh_token will expire soon
        # if so, do a self.generate_refresh_token
        access_token = new_credential.get('access_token')
        unverified_payload = jwt.decode(access_token, verify=False)
        expiration_time = unverified_payload['exp']
        credential.proxy = new_credential['access_token'] + ':' + refresh_token
        credential.termination_time = datetime.utcfromtimestamp(expiration_time)

        return credential


# Should be the only instance, called during the middleware initialization
oidc_manager = OIDCmanager()

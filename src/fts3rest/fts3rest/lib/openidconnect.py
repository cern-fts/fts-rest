import logging
from datetime import datetime

import jwt
from oic import rndstr
from oic.extension.message import TokenIntrospectionRequest, TokenIntrospectionResponse
from oic.oic import Client, Grant, Token
from oic.oic.message import AccessTokenResponse, Message, RegistrationResponse
from oic.utils import time_util
from oic.utils.authn.client import CLIENT_AUTHN_METHOD

log = logging.getLogger(__name__)


class OIDCmanager:
    """
    Class that interfaces with PyOIDC

    It is supposed to have a unique instance which provides all operations that require
    information from the OIDC issuers.
    """

    def __init__(self):
        self.clients = {}
        self.config = None

    def setup(self, config):
        self.config = config
        self._configure_clients(config['fts3.Providers'])
        self._set_keys_cache_time(int(config.get('fts3.JWKCacheSeconds', 86400)))
        self._retrieve_clients_keys()

    def _configure_clients(self, providers_config):
        # log.debug('provider_info::: {}'.format(client.provider_info))
        for provider in providers_config:
            try:
                client = Client(client_authn_method=CLIENT_AUTHN_METHOD)
                # Retrieve well-known configuration
                client.provider_config(provider)
                # Register
                client_reg = RegistrationResponse(client_id=providers_config[provider]['client_id'],
                                                  client_secret=providers_config[provider]['client_secret'])
                client.store_registration_info(client_reg)
                issuer = client.provider_info['issuer']
                self.clients[issuer] = client
            except Exception, ex:
                log.warning("Exception registering provider: {}".format(provider))
                log.warning(ex)

    def _retrieve_clients_keys(self):
        for provider in self.clients:
            client = self.clients[provider]
            client.keyjar.get_issuer_keys(provider)

    def _set_keys_cache_time(self, cache_time):
        for provider in self.clients:
            client = self.clients[provider]
            keybundles = client.keyjar.issuer_keys[provider]
            for keybundle in keybundles:
                keybundle.cache_time = cache_time

    def filter_provider_keys(self, issuer, kid=None, alg=None):
        """
        Return Provider Keys after applying Key ID and Algorithm filter.
        If no filters match, return the full set.
        :param issuer: provider
        :param kid: Key ID
        :param alg: Algorithm
        :return: keys
        :raise ValueError: client could not be retrieved
        """
        client = self.clients.get(issuer)
        if client is None:
            raise ValueError('Could not retrieve client for issuer={}'.format(issuer))
        # List of Keys (from pyjwkest)
        keys = client.keyjar.get_issuer_keys(issuer)
        filtered_keys = [key for key in keys if key.kid == kid or key.alg == alg]
        if len(filtered_keys) is 0:
            return keys
        return filtered_keys

    def introspect(self, issuer, access_token):
        """
        Make a Token Introspection request
        :param issuer: issuer of the token
        :param access_token: token to introspect
        :return: JSON response
        """
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
        """
        Exchange an access token for a refresh token
        :param issuer: issuer of the access token
        :param access_token:
        :return: refresh token
        :raise Exception: If refresh token cannot be obtained
        """
        log.debug("enter generate_refresh_token")
        client = self.clients[issuer]
        body = {'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
                'subject_token_type': 'urn:ietf:params:oauth:token-type:access_token',
                'subject_token': access_token,
                'scope': 'offline_access openid profile',
                'audience': client.client_id}
        try:
            response = client.do_any(Message,
                                     request_args=body,
                                     endpoint=client.provider_info["token_endpoint"],
                                     body_type='json',
                                     method='POST',
                                     authn_method="client_secret_basic"
                                     )
            response = response.json()
            log.debug("response: {}".format(response))
            refresh_token = response['refresh_token']
            log.debug('refresh_token_response::: {}'.format(refresh_token))
        except Exception as ex:
            log.warning("Exception raised when requesting refresh token")
            log.warning(ex)
            raise ex
        return refresh_token

    def request_token_exchange(self, issuer, access_token, scope=None, audience=None):
        """
        Do a token exchange request
        :param issuer: issuer of the access token
        :param access_token: token to exchange
        :param scope: string containing scopes separated by space
        :return: provider response in json
        :raise Exception: if request fails
        """
        client = self.clients[issuer]
        body = {'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
                'subject_token_type': 'urn:ietf:params:oauth:token-type:access_token',
                'subject_token': access_token
                }
        if scope:
            body['scope'] = scope
        if audience:
            body['audience'] = audience

        try:
            response = client.do_any(Message,
                                     request_args=body,
                                     endpoint=client.provider_info["token_endpoint"],
                                     body_type='json',
                                     method='POST',
                                     authn_method="client_secret_basic"
                                     )
            response = response.json()
            log.debug("response: {}".format(response))
        except Exception as ex:
            log.warning("Exception raised when exchanging token")
            log.warning(ex)
            raise ex
        return response

    def generate_token_with_scope(self, issuer, access_token, scope, audience=None):
        """
        Exchange an access token for another access token with the specified scope
        :param issuer: issuer of the access token
        :param access_token:
        :param scope: string containing scopes separated by space
        :return: new access token and optional refresh_token
        :raise Exception: If token cannot be obtained
        """
        response = self.request_token_exchange(issuer, access_token, scope=scope, audience=audience)
        access_token = response['access_token']
        refresh_token = response.get('access_token', None)
        return access_token, refresh_token

    def refresh_access_token(self, credential):
        """
        Request new access token
        :param credential: Credential from DB containing an access token and a refresh token
        :return: Updated credential containing new access token
        """
        access_token, refresh_token = credential.proxy.split(':')
        unverified_payload = jwt.decode(access_token, verify=False)
        issuer = unverified_payload['iss']
        client = self.clients[issuer]
        log.debug('refresh_access_token for {}'.format(issuer))

        # Prepare and make request
        refresh_session_state = rndstr(50)
        client.grant[refresh_session_state] = Grant()
        client.grant[refresh_session_state].grant_expiration_time = time_util.utc_time_sans_frac() + 60
        resp = AccessTokenResponse()
        resp["refresh_token"] = refresh_token
        client.grant[refresh_session_state].tokens.append(Token(resp))
        new_credential = client.do_access_token_refresh(authn_method="client_secret_basic",
                                                        state=refresh_session_state)
        # A new refresh token is optional
        refresh_token = new_credential.get('refresh_token', refresh_token)
        access_token = new_credential.get('access_token')
        unverified_payload = jwt.decode(access_token, verify=False)
        expiration_time = unverified_payload['exp']
        credential.proxy = new_credential['access_token'] + ':' + refresh_token
        credential.termination_time = datetime.utcfromtimestamp(expiration_time)

        return credential


# Should be the only instance, called during the middleware initialization
oidc_manager = OIDCmanager()

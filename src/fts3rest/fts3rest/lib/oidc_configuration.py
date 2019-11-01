from oic.oic import Client
from oic.oic.message import RegistrationResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from oic.extension.message import TokenIntrospectionRequest
from oic.extension.message import TokenIntrospectionResponse
from oic.oic.message import Message

import logging
log = logging.getLogger(__name__)


class OIDCmanager:

    def __init__(self):
        self.clients = {}
        self.config = None

    def __call__(self, config):
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
        keys = client.keyjar.get_issuer_keys(issuer)
        return self.find_key_with_kid(keys, kid)

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

    @staticmethod
    def find_key_with_kid(keys, kid):
        """
        :param keys: List of Keys (from pyjwkest)
        :param kid:
        :return: the key
        """
        for key in keys:
            if key.kid == kid:
                return key
        raise ValueError("Key with kid {} not found".format(kid))


# Should be the only instance, called during the middleware initialization
oidc_manager = OIDCmanager()

from oic.oic import Client
from oic.oic.message import RegistrationResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD

import logging
log = logging.getLogger(__name__)


class OIDCmanager:

    def __init__(self):
        self.clients = {}

    def __call__(self, config):
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

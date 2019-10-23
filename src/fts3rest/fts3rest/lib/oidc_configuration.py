from oic.oic import Client
from oic.oic.message import RegistrationResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD


class OIDCmanager:

    def __init__(self):
        self.clients = {}

    def __call__(self, config):
        self._configure_clients(config)

    def _configure_clients(self, config):
        providers_config = config['fts3.Providers']
        for provider in providers_config:
            client = Client(client_authn_method=CLIENT_AUTHN_METHOD)
            # Retrieve well-known configuration
            client.provider_config(provider)
            # Register
            client_reg = RegistrationResponse(client_id=providers_config[provider]['client_id'],
                                              client_secret=providers_config[provider]['client_secret'])
            client.store_registration_info(client_reg)
            self.clients[provider] = client


oidc_manager = OIDCmanager()

from fts3rest.tests import TestController
from fts3rest.lib.openidconnect import OIDCmanager
from fts3rest.lib.oauth2provider import FTS3OAuth2ResourceProvider
from fts3.model import Credential

import subprocess
from subprocess import PIPE, STDOUT


class TestFTS3OAuth2ResourceProvider(TestController):
    """
    Test token validation

    To run these tests, the host should have oidc-agent installed,
    with an account 'wlcgtest' in the provider https://wlcg.cloud.cnaf.infn.it/
    """

    def setUp(self):
        self.oidc_manager = OIDCmanager()
        self.config = self.app.app.config
        self.issuer = 'https://wlcg.cloud.cnaf.infn.it/'
        self.oidc_manager.setup(self.config)
        self.oauth2_resource_provider = FTS3OAuth2ResourceProvider(dict(), self.config)
        self.expired_token = "eyJraWQiOiJyc2ExIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiI4NmE1MDc1Ny01YzJjLTQwYjEtYTgwNy1lMjE0NTY1OGEwMmYiLCJpc3MiOiJodHRwczpcL1wvd2xjZy5jbG91ZC5jbmFmLmluZm4uaXRcLyIsImV4cCI6MTU3ODU2NjA5NywiaWF0IjoxNTc4NTYyNDk3LCJqdGkiOiI4OTA0MGMwZC0zNmU0LTRkMWQtYTJkMy02MWNkY2I1N2RjYzQifQ.DvGkRyoU6l0YC8gDhFOQ01JuvbmsZ-XHG6zd3jbY-rm4MzxtaKXWab2hechd5Al3w-eygziCEB8QO65G8phqOew_e5YQZpqw8P-x2NRXVlSGuEWp9PYtUMt4BV5pHvBVdwp1OyP2Sr53p3xMA-0oaGw0h_CmyOMGK-k2Wk_jkhU"

    def _get_xdc_access_token(self):
        command = "eval `oidc-agent` && oidc-add wlcgtest --pw-cmd=echo && oidc-token wlcgtest"
        output = subprocess.check_output(command, shell=True)
        output = str(output).strip()
        token = output.split('\n')[2]  # The 3rd line is the token
        return token

    def test_validate_access_token(self):
        token = self._get_xdc_access_token()
        auth = self.oauth2_resource_provider.authorization_class()
        self.oauth2_resource_provider.validate_access_token(token, auth)
        self.assertTrue(auth.is_valid)

    def test_validate_token_offline(self):
        token = self._get_xdc_access_token()
        valid, credential = self.oauth2_resource_provider._validate_token_offline(token)
        self.assertTrue(valid)
        self.assertEqual(credential['iss'], self.issuer)

    def test_validate_token_online(self):
        token = self._get_xdc_access_token()
        valid, credential = self.oauth2_resource_provider._validate_token_online(token)
        self.assertTrue(valid)
        self.assertEqual(credential['iss'], self.issuer)

    def test_validate_access_token_invalid(self):
        token = self._get_xdc_access_token()
        token += 'invalid'
        auth = self.oauth2_resource_provider.authorization_class()
        self.oauth2_resource_provider.validate_access_token(token, auth)
        self.assertFalse(auth.is_valid)

    def test_validate_token_offline_invalid(self):
        token = self._get_xdc_access_token()
        token += 'invalid'
        valid, credential = self.oauth2_resource_provider._validate_token_offline(token)
        self.assertFalse(valid)

    def test_validate_token_online_invalid(self):
        token = self._get_xdc_access_token()
        token += 'invalid'
        valid, credential = self.oauth2_resource_provider._validate_token_online(token)
        self.assertFalse(valid)

    def test_validate_access_token_expired(self):
        token = self.expired_token
        auth = self.oauth2_resource_provider.authorization_class()
        self.oauth2_resource_provider.validate_access_token(token, auth)
        self.assertFalse(auth.is_valid)

    def test_validate_token_offline_expired(self):
        token = self.expired_token
        valid, credential = self.oauth2_resource_provider._validate_token_offline(token)
        self.assertFalse(valid)

    def test_validate_token_online_expired(self):
        token = self.expired_token
        valid, credential = self.oauth2_resource_provider._validate_token_online(token)
        self.assertFalse(valid)
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

    def _get_xdc_access_token(self):
        command = "eval `oidc-agent` && oidc-add wlcgtest --pw-cmd=echo && oidc-token wlcgtest"
        output = subprocess.check_output(command, shell=True)
        output = str(output).strip()
        token = output[output.find("ey"):]
        return token

    def test_validate_access_token(self):
        auth = self.oauth2_resource_provider.authorization_class()
        self.oauth2_resource_provider.validate_access_token(token, auth)
        self.assertTrue(auth.is_valid)

    def test_validate_token_offline(self):
        token = self._get_xdc_access_token()
        valid, credential = self.oauth2_resource_provider._validate_token_offline(token)
        self.assertTrue(valid)

    def test_validate_token_online(self):
        token = self._get_xdc_access_token()
        valid, credential = self.oauth2_resource_provider._validate_token_online(token)
        self.assertTrue(valid)
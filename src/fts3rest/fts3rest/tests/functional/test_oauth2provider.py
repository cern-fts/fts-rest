from fts3rest.tests import TestController
from fts3rest.lib.openidconnect import OIDCmanager
from fts3.model import Credential

import subprocess
from subprocess import PIPE, STDOUT


class TestFTS3OAuth2ResourceProvider(TestController):
    """
    Tests OIDCmanager operations

    To run these tests, the host should have an oidc-agent daemon active,
    with an account 'wlcgtest' in the provider https://wlcg.cloud.cnaf.infn.it/,
    added with oidc-add
    """

    def setUp(self):
        self.oidc_manager = OIDCmanager()
        self.config = self.app.app.config
        self.issuer = 'https://wlcg.cloud.cnaf.infn.it/'

    def _get_xdc_access_token(self):
        command = "eval `oidc-agent` && oidc-add wlcgtest < '\n' && oidc-token wlcgtest"
        output = subprocess.check_output(command, shell=True)
        token = str(output).strip()
        return token

    def test_validate_access_token(self):
        pass

    def test_validate_token_offline(self):
        pass

    def test_validate_token_online(self):
        pass
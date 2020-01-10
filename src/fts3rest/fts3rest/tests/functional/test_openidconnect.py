from fts3rest.tests import TestController
from fts3rest.lib.openidconnect import OIDCmanager
from fts3.model import Credential

import subprocess
from subprocess import PIPE, STDOUT


class TestOpenidconnect(TestController):
    """
    Tests OIDCmanager operations

    To run these tests, the host should have oidc-agent installed,
    with an account 'wlcgtest' in the provider https://wlcg.cloud.cnaf.infn.it/
    """

    def setUp(self):
        self.oidc_manager = OIDCmanager()
        self.config = self.app.app.config
        self.issuer = 'https://wlcg.cloud.cnaf.infn.it/'

    def _get_xdc_access_token(self):
        command = "eval `oidc-agent` && oidc-add wlcgtest --pw-cmd=echo && oidc-token wlcgtest"
        output = subprocess.check_output(command, shell=True)
        output = str(output).strip()
        token = output.split('\n')[2]  # The 3rd line is the token
        return token

    def test_configure_clients(self):
        self.oidc_manager._configure_clients(self.config['fts3.Providers'])
        self.assertEqual(len(self.oidc_manager.clients), len(self.config['fts3.Providers']))

    def test_introspect(self):
        self.oidc_manager.setup(self.config)
        access_token = self._get_xdc_access_token()
        response = self.oidc_manager.introspect(self.issuer, access_token)
        self.assertTrue(response['active'])

    def test_generate_refresh_token(self):
        self.oidc_manager.setup(self.config)
        access_token = self._get_xdc_access_token()
        self.oidc_manager.generate_refresh_token(self.issuer, access_token)

    def test_generate_refresh_token_invalid(self):
        self.oidc_manager.setup(self.config)
        access_token = self._get_xdc_access_token()
        access_token += 'invalid'
        with self.assertRaises(Exception):
            self.oidc_manager.generate_refresh_token(self.issuer, access_token)

    def test_refresh_access_token(self):
        self.oidc_manager.setup(self.config)
        access_token = self._get_xdc_access_token()
        refresh_token = self.oidc_manager.generate_refresh_token(self.issuer, access_token)
        credential = Credential()
        credential.proxy = ':'.join([access_token, refresh_token])
        new_credential = self.oidc_manager.refresh_access_token(credential)
        self.assertIsNotNone(new_credential.termination_time)

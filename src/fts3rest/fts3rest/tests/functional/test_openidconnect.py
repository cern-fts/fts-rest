from fts3rest.tests import TestController
from fts3rest.lib.openidconnect import OIDCmanager
from fts3.model import Credential

import subprocess


class TestOpenidconnect(TestController):
    """
    Tests OIDCmanager operations

    To run these tests, the host should have an oidc-agent daemon active,
    with an account 'wlcgtest' in the provider https://wlcg.cloud.cnaf.infn.it/,
    added with oidc-add
    """

    def setUp(self):
        self.oidc_manager = OIDCmanager()
        self.config = self.app.app.config
        self.issuer = 'https://iam.extreme-datacloud.eu/'
        self.issuer = 'https://wlcg.cloud.cnaf.infn.it/'

    def test_configure_clients(self):
        self.oidc_manager._configure_clients(self.config['fts3.Providers'])
        self.assertEqual(len(self.oidc_manager.clients), len(self.config['fts3.Providers']))

    def _get_xdc_access_token(self):
        output = subprocess.check_output('oidc-token wlcgtest', shell=True)
        token = str(output).strip()
        return token

    def test_introspect(self):
        print(self.config['fts3.Providers'])
        self.oidc_manager.setup(self.config)
        access_token = self._get_xdc_access_token()
        response = self.oidc_manager.introspect(self.issuer, access_token)
        self.assertTrue(response['active'])

    def test_generate_refresh_token(self):
        self.oidc_manager.setup(self.config)
        access_token = self._get_xdc_access_token()
        self.oidc_manager.generate_refresh_token(self.issuer, access_token)

    def test_refresh_access_token(self):
        self.oidc_manager.setup(self.config)
        access_token = self._get_xdc_access_token()
        refresh_token = self.oidc_manager.generate_refresh_token(self.issuer, access_token)
        credential = Credential()
        credential.proxy = ':'.join([access_token, refresh_token])
        new_credential = self.oidc_manager.refresh_access_token(credential)
        self.assertIsNotNone(new_credential.termination_time)

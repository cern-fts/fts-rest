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
    with an account 'xdctest'
    """

    def setUp(self):
        self.oidc_manager = OIDCmanager()
        self.config = self.app.app.config
        self.issuer = 'https://iam.extreme-datacloud.eu/'
        self.oidc_manager.setup(self.config)
        self.oauth2_resource_provider = FTS3OAuth2ResourceProvider(dict(), self.config)
        self.expired_token = "eyJraWQiOiJyc2ExIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiI5NGQyNTQyOS1mYTZhLTRiYTctOGM0NS1mMTk1YjI3ZWVkNjMiLCJpc3MiOiJodHRwczpcL1wvaWFtLmV4dHJlbWUtZGF0YWNsb3VkLmV1XC8iLCJleHAiOjE1ODAyMjIyMDksImlhdCI6MTU4MDIxODYwOSwianRpIjoiYTI0NDRhYTQtNTE3YS00Y2E0LTgwMTUtY2IyMjc0Nzg4YzlkIn0.hvTjA-Ix_YVxU3HmLB6FQa98eYtUwbw1WcZMO5p_qOjnPwD0OtQViVtV-a5__hLY1_qRFouAzgVvqKnueokh1pmKoI6TJN2KpmybueAZR30lIG_t_aAn4hGQvuVezs_0LLISojQUgprbi2PDsU1q8WTJq1J5mwGwlBijGmHQs60"

    def _get_xdc_access_token(self):
        command = "eval `oidc-agent` && oidc-add xdctest --pw-cmd=echo && oidc-token xdctest"
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
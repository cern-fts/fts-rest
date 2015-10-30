#   Copyright notice:
#   Copyright CERN, 2014.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import json
import pylons
import time
import urlparse

from datetime import datetime, timedelta
from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import OAuth2Application, OAuth2Code, OAuth2Token, AuthorizationByDn
from Cookie import SimpleCookie as Cookie


class TestOAuth2(TestController):
    """
    Tests oauth2 api
    """

    def get_cookie(self, response, cookie):
        existing = response.headers.getall('Set-Cookie')
        if not existing:
            return None
        cookies = Cookie()
        for header in existing:
            cookies.load(header)
        if isinstance(cookie, str):
            cookie = cookie.encode('utf8')
        if cookie in cookies:
            return cookies[cookie].value
        else:
            return None

    def setUp(self):
        super(TestOAuth2, self).setUp()
        pylons.config['fts3.oauth2'] = True

    def tearDown(self):
        super(TestOAuth2, self).tearDown()
        Session.query(OAuth2Application).delete()
        Session.query(OAuth2Token).delete()
        Session.query(OAuth2Code).delete()
        Session.query(AuthorizationByDn).delete()
        Session.commit()

    def test_register(self, scope='transfer', no_vo=False):
        """
        Test the registration of an app
        """
        self.setup_gridsite_environment(no_vo=no_vo)
        req = {
            'name': 'MyApp',
            'description': 'Blah blah blah',
            'website': 'https://example.com',
            'redirect_to': 'https://mysite.com/callback',
            'scope': scope
        }
        client_id = self.app.post_json(
            url="/oauth2/register",
            params=req,
            status=201
        ).json
        self.assertNotEqual(None, client_id)

        app = Session.query(OAuth2Application).get(client_id)

        self.assertEqual('MyApp', app.name)
        self.assertEqual('Blah blah blah', app.description)
        self.assertEqual('https://example.com', app.website)
        self.assertEqual('https://mysite.com/callback', app.redirect_to)
        self.assertEqual('/DC=ch/DC=cern/CN=Test User', app.owner)
        self.assertEqual(set(scope.split(',')), app.scope)

        self.app.post_json(
            url="/oauth2/register",
            params=req,
            status=403
        )

        return client_id

    def test_get_my_apps(self):
        """
        Get my list of apps
        """
        client_id = self.test_register()
        apps = self.app.get(
            url="/oauth2/apps",
            status=200
        ).json

        self.assertEqual(1, len(apps['apps']))
        self.assertEqual(client_id, apps['apps'][0]['client_id'])

    def test_get_app(self):
        """
        Ask for a given app
        """
        client_id = self.test_register()
        app = self.app.get(
            url="/oauth2/apps/%s" % str(client_id),
            status=200
        ).json
        self.assertEqual(client_id, app['client_id'])

    def test_delete(self):
        """
        Test the removal of an app
        """
        client_id = self.test_register()
        self.app.delete(
            url="/oauth2/apps/%s" % str(client_id),
            status=200
        )
        app = Session.query(OAuth2Application).get(client_id)
        self.assertEqual(None, app)

    def test_get_app_forbidden(self):
        """
        Ask for an app that does not belong to us
        """
        client_id = self.test_register()
        self.app.extra_environ.update({'GRST_CRED_AURI_0': 'dn:/DC=ch/DC=cern/CN=Test User 2'})
        self.app.get(
            url="/oauth2/apps/%s" % str(client_id),
            status=403
        )

    def test_delete_app_forbidden(self):
        """
        Test the removal of an app that does not belong to us
        """
        client_id = self.test_register()
        self.app.extra_environ.update({'GRST_CRED_AURI_0': 'dn:/DC=ch/DC=cern/CN=Test User 2'})
        self.app.delete(
            url="/oauth2/apps/%s" % str(client_id),
            status=403
        )

    def test_no_direct_grant_post(self):
        """
        An authorization POST must come from the FTS3 server itself!
        """
        client_id = self.test_register()
        self.app.post(
            url="/oauth2/authorize?client_id=%s&redirect_to=https://mysite.com/callback&something=else" % str(client_id),
            params={'accept': True},
            status=403
        )

    def test_get_code(self, scope='transfer', no_vo=False, client_id=None):
        """
        Get a OAuth2 code (second step, after redirection)
        """
        if not client_id:
            client_id = self.test_register(scope=scope, no_vo=no_vo)

        response = self.app.get(
            url="/oauth2/authorize?client_id=%s&redirect_to=https://mysite.com/callback&something=else&scope=%s" % (str(client_id), scope),
            status=200
        )
        csrf = self.get_cookie(response, 'fts3oauth2_csrf')
        self.assertTrue(csrf is not None)

        response = self.app.post(
            url="/oauth2/authorize?client_id=%s&redirect_to=https://mysite.com/callback&something=else&scope=%s" % (str(client_id), scope),
            params={'accept': True, 'CSRFToken': csrf},
            status=302
        )
        redirect_path, redirect_args = response.headers['Location'].split('?', 2)
        self.assertEqual('https://mysite.com/callback', redirect_path)
        args = urlparse.parse_qs(redirect_args)
        self.assertIn('something', args.keys())
        self.assertEqual('else', args['something'][0])
        self.assertIn('code', args.keys())
        return client_id, args['code'][0]

    def test_get_code_invalid_scope(self):
        """
        Try to get a OAuth2 code (second step) with a scope that wasn't registered
        """
        client_id = self.test_register(scope='transfer')

        self.app.get(
            url="/oauth2/authorize?client_id=%s&redirect_to=https://mysite.com/callback&something=else&scope=transfer,copy" % str(client_id),
            status=400
        )

    def _get_client_secret(self, client_id):
        app = self.app.get(
            url="/oauth2/apps/%s" % client_id,
            status=200
        ).json
        return app['client_secret']

    def test_get_token(self, scope='transfer', no_vo=False, client_id=None):
        """
        Get a OAuth2 token (third step)
        """
        client_id, code = self.test_get_code(scope=scope, no_vo=no_vo, client_id=client_id)
        auth = self.app.post(
            url="/oauth2/token",
            params={
                'grant_type': 'authorization_code',
                'client_id': client_id,
                'client_secret': self._get_client_secret(client_id),
                'code': code,
                'redirect_uri': 'https://mysite.com/callback',
                'scope': scope
            },
            status=200
        ).json
        self.assertIn('access_token', auth.keys())
        self.assertIn('refresh_token', auth.keys())
        self.assertEqual('Bearer', auth.get('token_type'))

        return client_id, auth['access_token'], auth['refresh_token'], datetime.utcnow() + timedelta(seconds=auth['expires_in'])

    def test_get_token_invalid_scope(self):
        """
        Get a OAuth2 token (third step) but requesting a token that is not registered
        """
        client_id, code = self.test_get_code(scope='transfer')
        self.app.post(
            url="/oauth2/token",
            params={
                'grant_type': 'authorization_code',
                'client_id': client_id,
                'client_secret': self._get_client_secret(client_id),
                'code': code,
                'redirect_uri': 'https://mysite.com/callback',
                'scope': 'transfer,config'
            },
            status=400
        )

    def test_refresh_token(self):
        """
        Refresh a token
        """
        client_id, access_token, refresh_token, expires = self.test_get_token('transfer')
        auth = self.app.post(
            url="/oauth2/token",
            params={
                'grant_type': 'refresh_token',
                'client_id': client_id,
                'client_secret': self._get_client_secret(client_id),
                'refresh_token': refresh_token,
                'scope': 'transfer'
            },
            status=200
        ).json
        self.assertIn('access_token', auth.keys())
        time.sleep(1)
        self.assertGreater(datetime.utcnow() + timedelta(seconds=auth['expires_in']), expires)

    def test_whoami_bearer(self):
        """
        Ask for /whoami using only the bearer token
        """
        client_id, access_token, refresh_token, expires = self.test_get_token()

        del self.app.extra_environ['GRST_CRED_AURI_0']

        # Without bearer first
        whoami = self.app.get(
            url="/whoami",
            status=200
        ).json
        self.assertEqual('anon', whoami['user_dn'])
        self.assertEqual('unauthenticated', whoami['method'])

        # With bearer
        whoami = self.app.get(
            url="/whoami",
            headers={'Authorization': str('Bearer %s' % access_token)},
            status=200
        ).json
        self.assertEqual('/DC=ch/DC=cern/CN=Test User', whoami['user_dn'])

    def test_revoke(self):
        """
        Authorize, then revoke and check if it can be used
        """
        client_id, access_token, refresh_token, expires = self.test_get_token()
        self.app.get(
            url="/oauth2/revoke/%s" % client_id,
            status=303
        )
        del self.app.extra_environ['GRST_CRED_AURI_0']
        self.app.get(
            url="/jobs",
            headers={'Authorization': str('Bearer %s' % access_token)},
            status=403
        )

    def test_oauth2_with_bearer(self):
        """
        Using bearer tokens in the OAuth2 controller must be denied
        """
        client_id, access_token, refresh_token, expires = self.test_get_token()

        del self.app.extra_environ['GRST_CRED_AURI_0']

        self.app.get(
            url="/oauth2/apps",
            headers={'Authorization': str('Bearer %s' % access_token)},
            status=403
        )
        self.app.get(
            url="/oauth2/register",
            headers={'Authorization': str('Bearer %s' % access_token)},
            status=403
        )
        self.app.post(
            url="/oauth2/register",
            headers={'Authorization': str('Bearer %s' % access_token)},
            params={'name': 'Something', 'website': 'https://1234/'},
            status=403
        )

    def test_expired(self):
        """
        Get a token, the token expires, so it should be denied
        """
        client_id, access_token, refresh_token, expires = self.test_get_token()
        del self.app.extra_environ['GRST_CRED_AURI_0']

        whoami = self.app.get(
            url="/whoami",
            headers={'Authorization': str('Bearer %s' % access_token)},
            status=200
        ).json
        self.assertEqual('oauth2', whoami['method'])

        token = Session.query(OAuth2Token).get((client_id, refresh_token))
        token.expires = datetime.utcnow() - timedelta(hours=1)
        Session.merge(token)
        Session.commit()

        self.app.get(
            url="/whoami",
            headers={'Authorization': str('Bearer %s' % access_token)},
            status=403
        )

    def test_with_no_config_scope(self):
        """
        Get a token but only for transfer, trying to configure even if the user
        is allowed must fail
        """
        AuthorizationByDn(dn=self.TEST_USER_DN, operation='config')

        client_id, access_token, refresh_token, expires = self.test_get_token()
        del self.app.extra_environ['GRST_CRED_AURI_0']

        self.app.get(
            url="/config/fixed",
            headers={'Authorization': str('Bearer %s' % access_token)},
            status=403
        )

    def test_with_config_scope(self):
        """
        Get a token including config, try to configure
        """
        AuthorizationByDn(dn=self.TEST_USER_DN, operation='config')

        client_id, access_token, refresh_token, expires = self.test_get_token(scope='transfer,config')
        del self.app.extra_environ['GRST_CRED_AURI_0']

        self.app.get(
            url="/config/fixed",
            headers={'Authorization': str('Bearer %s' % access_token)},
            status=200
        )

    def test_with_config_scope_no_authorized(self):
        """
        Even if the scope is present, if the user has no permission it should be forbidden
        """
        client_id, access_token, refresh_token, expires = self.test_get_token(scope='transfer,config', no_vo=True)
        del self.app.extra_environ['GRST_CRED_AURI_0']

        self.app.get(
            url="/config/fixed",
            headers={'Authorization': str('Bearer %s' % access_token)},
            status=403
        )

    def test_with_config_scope_auth(self):
        """
        Even being authorized and having the config scope, adding new authorizations must be denied
        """
        AuthorizationByDn(dn=self.TEST_USER_DN, operation='config')

        client_id, access_token, refresh_token, expires = self.test_get_token(scope='transfer,config')

        self.app.post_json(
            url="/config/authorize",
            headers={'Authorization': str('Bearer %s' % access_token)},
            params={'dn': '/DC=ky/DC=pirates/CN=badguy', 'operation': 'config'},
            status=403
        )

    def test_rogue_app(self):
        """
        Register an application with transfer and config, grant only transfer, config must be forbidden
        """
        client_id = self.test_register(scope='transfer,config')
        client_id, access_token, refresh_token, expires = self.test_get_token(scope='transfer', client_id=client_id)
        del self.app.extra_environ['GRST_CRED_AURI_0']

        self.app.get(
            url="/config/fixed",
            headers={'Authorization': str('Bearer %s' % access_token)},
            status=403
        )

    def test_app_not_found(self):
        """
        Application not found
        """
        client_id = self.test_get_app()
        self.app.get(
            url="/oauth2/apps/%s" % client_id,
            status=404
        )

    def test_update_app(self):
        """
        Try to update app
        """
        client_id = str(self.test_register())

        config = {'redirect_to': 'https://xxx/path', 'description': 'abcd'}

        self.app.post_json(
            url="/oauth2/apps/%s" % client_id,
            params=config,
            status=303
        )

        app = Session.query(OAuth2Application).get(client_id)

        self.assertEqual('MyApp', app.name)
        self.assertEqual('abcd', app.description)
        self.assertEqual('https://xxx/path', app.redirect_to)
        self.assertEqual('/DC=ch/DC=cern/CN=Test User', app.owner)

    def test_invalid_scope(self):
        """
        Set invalid scope
        """
        self.setup_gridsite_environment()
        req = {
            'name': 'MyApp',
            'description': 'Blah blah blah',
            'website': 'https://example.com',
            'redirect_to': 'https://mysite.com/callback',
            'scope': 'transfer,1'
        }
        self.app.post_json(
            url="/oauth2/register",
            params=req,
            status=400
        )

    def test_missing_web_or_name(self):
        """
        Missing website
        """

        config = {'name': 'MyApp', 'website': 'https://example.com'}

        for i in config:
            self.setup_gridsite_environment()
            k = config
            del config[i]
            self.app.post(url="/oauth2/register", params=k, status=400)
            return config

    def test_missing_redirect(self):
        """
        Missing redirect_to
        """
        self.setup_gridsite_environment()
        req = {
            'name': 'MyApp',
            'description': 'Blah blah blah',
            'website': 'https://example.com',
            'redirect_to': '',
            'scope': 'transfer'
        }
        self.app.post_json(
            url="/oauth2/register",
            params=req,
            status=400
        )

    def test_get_my_apps_3(self):
        """
        Lines 100,101
        """
        self.setup_gridsite_environment()
        req = {
            'name': 'MyApp',
            'description': 'Blah blah blah',
            'website': 'https://example.com',
            'redirect_to': 'https://mysite.com/callback',
            'scope': 'transfer'
        }
        self.app.post(
            url="/oauth2/register",
            content_type='text/html; charset=UTF-8',
            params=json.dumps(req),
            status=400
        )

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
from fts3.model import OAuth2Application, OAuth2Token
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

    def tearDown(self):
        Session.query(OAuth2Application).delete()
        pylons.config['fts3.oauth2'] = True

    def test_register(self):
        """
        Test the registration of an app
        """
        self.setup_gridsite_environment()
        req = {
            'name': 'MyApp',
            'description': 'Blah blah blah',
            'website': 'https://example.com',
            'redirect_to': 'https://mysite.com/callback'
        }
        response = self.app.post(
            url="/oauth2/register",
            content_type='application/json',
            params=json.dumps(req),
            status=201
        )
        client_id = json.loads(response.body)
        self.assertNotEqual(None, client_id)

        app = Session.query(OAuth2Application).get(client_id)

        self.assertEqual('MyApp', app.name)
        self.assertEqual('Blah blah blah', app.description)
        self.assertEqual('https://example.com', app.website)
        self.assertEqual('https://mysite.com/callback', app.redirect_to)
        self.assertEqual('/DC=ch/DC=cern/CN=Test User', app.owner)

        return client_id

    def test_get_my_apps(self):
        """
        Get my list of apps
        """
        client_id = self.test_register()
        response = self.app.get(
            url="/oauth2/apps",
            status=200
        )
        apps = json.loads(response.body)

        self.assertEqual(1, len(apps['apps']))
        self.assertEqual(client_id, apps['apps'][0]['client_id'])

    def test_get_app(self):
        """
        Ask for a given app
        """
        client_id = self.test_register()
        response = self.app.get(
            url="/oauth2/apps/%s" % str(client_id),
            status=200
        )
        app = json.loads(response.body)
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

    def test_get_code(self):
        """
        Get a OAuth2 code (second step, after redirection)
        """
        client_id = self.test_register()

        response = self.app.get(
            url="/oauth2/authorize?client_id=%s&redirect_to=https://mysite.com/callback&something=else" % str(client_id),
            status=200
        )
        csrf = self.get_cookie(response, 'fts3oauth2_csrf')
        self.assertTrue(csrf is not None)

        response = self.app.post(
            url="/oauth2/authorize?client_id=%s&redirect_to=https://mysite.com/callback&something=else" % str(client_id),
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

    def _get_client_secret(self, client_id):
        response = self.app.get(
            url="/oauth2/apps/%s" % client_id,
            status=200
        )
        app = json.loads(response.body)
        return app['client_secret']

    def test_get_token(self):
        """
        Get a OAuth2 token (third step)
        """
        client_id, code = self.test_get_code()
        response = self.app.post(
            url="/oauth2/token",
            params={
                'grant_type': 'authorization_code',
                'client_id': client_id,
                'client_secret': self._get_client_secret(client_id),
                'code': code,
                'redirect_uri': 'https://mysite.com/callback'
            },
            status=200
        )
        auth = json.loads(response.body)
        self.assertIn('access_token', auth.keys())
        self.assertIn('refresh_token', auth.keys())
        self.assertEqual('Bearer', auth.get('token_type'))

        return client_id, auth['access_token'], auth['refresh_token'], datetime.utcnow() + timedelta(seconds=auth['expires_in'])

    def test_refresh_token(self):
        """
        Refresh a token
        """
        client_id, access_token, refresh_token, expires = self.test_get_token()
        response = self.app.post(
            url="/oauth2/token",
            params={
                'grant_type': 'refresh_token',
                'client_id': client_id,
                'client_secret': self._get_client_secret(client_id),
                'refresh_token': refresh_token,
            },
            status=200
        )
        auth = json.loads(response.body)
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
        response = self.app.get(
            url="/whoami",
            status=200
        )
        whoami = json.loads(response.body)
        self.assertEqual('anon', whoami['user_dn'])
        self.assertEqual('unauthenticated', whoami['method'])

        # With bearer
        response = self.app.get(
            url="/whoami",
            headers={'Authorization': str('Bearer %s' % access_token)},
            status=200
        )
        whoami = json.loads(response.body)
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

    def test_oauth2_disable(self):
        """
        Disable OAuth2 in the configuration
        """
        self.setup_gridsite_environment()
        pylons.config['fts3.oauth2'] = False

        self.app.get(
            url="/oauth2/apps",
            status=403
        )
        self.app.get(
            url="/oauth2/register",
            status=403
        )
        self.app.get(
            url="/oauth2/authorize",
            status=403
        )

    def test_expired(self):
        """
        Get a token, the token expires, so it should be denied
        """
        client_id, access_token, refresh_token, expires = self.test_get_token()
        del self.app.extra_environ['GRST_CRED_AURI_0']

        response = self.app.get(
            url="/whoami",
            headers={'Authorization': str('Bearer %s' % access_token)},
            status=200
        )
        whoami = json.loads(response.body)
        self.assertEqual('oauth2', whoami['method'])

        token = Session.query(OAuth2Token).get((client_id, refresh_token))
        token.expires = datetime.utcnow() - timedelta(hours=1)
        Session.merge(token)
        Session.commit()

        response = self.app.get(
            url="/whoami",
            headers={'Authorization': str('Bearer %s' % access_token)},
            status=403
        )

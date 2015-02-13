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

import base64
import json
import logging
import os
import pylons
import urlparse
from sqlalchemy.exc import IntegrityError
from pylons.templating import render_mako as render
from pylons.controllers.util import redirect
from routes import url_for

from fts3.model.oauth2 import OAuth2Application, OAuth2Token, OAuth2Code
from fts3rest.lib.oauth2provider import FTS3OAuth2AuthorizationProvider
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import to_json
from fts3rest.lib.http_exceptions import *
from fts3rest.lib.middleware.fts3auth import require_certificate
from fts3rest.lib.oauth2lib.utils import random_ascii_string


URN_NO_REDIRECT = 'urn:ietf:wg:oauth:2.0:oob'

log = logging.getLogger(__name__)


class OAuth2Error(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def _generate_app_id():
    return base64.urlsafe_b64encode(os.urandom(16)).strip('=')


def _generate_app_secret():
    return base64.urlsafe_b64encode(os.urandom(32)).strip('=')


def _accept_html(accept):
    """
    Returns True if the request asked for HTML
    """
    return hasattr(accept, 'accept_html') and accept.accept_html()


class Oauth2Controller(BaseController):
    """
    OAuth2.0 controller
    """

    def __init__(self, *args, **kwargs):
        super(Oauth2Controller, self).__init__(*args, **kwargs)
        self.oauth2_provider = FTS3OAuth2AuthorizationProvider()

    @require_certificate
    def register_form(self):
        """
        Registration form
        """
        user = pylons.request.environ['fts3.User.Credentials']
        return render('/register.html', extra_vars={'user': user, 'site': pylons.config['fts3.SiteName']})

    @doc.response(201, 'Application registered')
    @doc.response(303, 'Application registered, follow redirection (when html requested)')
    @doc.response(400, 'Bad request')
    @doc.response(403, 'Tried to update an application that does not belong to the user')
    @doc.return_type('client_id')
    @require_certificate
    def register(self):
        """
        Register a new third party application
        """
        if pylons.request.content_type.split(';')[0].strip() == 'application/json':
            req = json.loads(pylons.request.body)
        else:
            req = pylons.request.POST

        if not req.get('name', None):
            raise HTTPBadRequest('Missing application name')
        if not req.get('website', None):
            raise HTTPBadRequest('Missing application website')
        if not req.get('redirect_to', None):
            raise HTTPBadRequest('Missing redirect urls')

        user = pylons.request.environ['fts3.User.Credentials']

        app_id = _generate_app_id()
        app = OAuth2Application(
            client_id=app_id,
            client_secret=_generate_app_secret(),
            name=req['name'],
            description=req.get('description', ''),
            website=req['website'],
            redirect_to=req['redirect_to'],
            owner=user.user_dn
        )

        try:
            Session.merge(app)
            Session.commit()
        except IntegrityError:
            Session.rollback()
            raise HTTPForbidden('The name already exists')
        except:
            Session.rollback()
            raise

        log.info("New application registered: %s (%s)" % (req['name'], app_id))

        if _accept_html(pylons.request.accept):
            redirect(url_for(controller='oauth2', action='get_my_apps'), code=HTTPSeeOther.code)
        else:
            pylons.response.status_int = HTTPCreated.code
            pylons.response.headers['Content-Type'] = 'application/json'
            return [to_json(app.client_id)]

    @doc.return_type(array_of=OAuth2Application)
    @require_certificate
    def get_my_apps(self):
        """
        Returns the list of registered apps
        """
        user = pylons.request.environ['fts3.User.Credentials']
        my_apps = Session.query(OAuth2Application).filter(OAuth2Application.owner == user.user_dn).all()

        authorized_apps = Session.query(
            OAuth2Application.client_id, OAuth2Application.name, OAuth2Application.website,
            OAuth2Application.description, OAuth2Token.refresh_token, OAuth2Token.scope, OAuth2Token.expires
        ).filter((OAuth2Token.dlg_id == user.delegation_id) & (OAuth2Token.client_id == OAuth2Application.client_id))

        response = {'apps': my_apps, 'authorized': authorized_apps}
        if _accept_html(pylons.request.accept):
            pylons.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
            response['user'] = user
            response['site'] = pylons.config['fts3.SiteName']
            return render('/apps.html', extra_vars=response)
        else:
            pylons.response.headers['Content-Type'] = 'application/json'
            # Better serialization for authorized apps
            authorized = list()
            for auth in authorized_apps:
                authorized.append({
                    'name': auth.name,
                    'website': auth.website,
                    'description': auth.description,
                    'scope': auth.scope,
                    'expires': auth.expires
                })
            response['authorized'] = authorized
            return [to_json(response)]

    @doc.return_type(OAuth2Application)
    @doc.response(403, 'The application does not belong to the user')
    @doc.response(404, 'Application not found')
    @require_certificate
    def get_app(self, client_id):
        """
        Return information about a given app
        """
        user = pylons.request.environ['fts3.User.Credentials']
        app = Session.query(OAuth2Application).get(client_id)
        if not app:
            raise HTTPNotFound('Application not found')
        if app.owner != user.user_dn:
            raise HTTPForbidden()
        if _accept_html(pylons.request.accept):
            pylons.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
            return render('/app.html', extra_vars={'app': app, 'user': user, 'site': pylons.config['fts3.SiteName']})
        else:
            pylons.response.headers['Content-Type'] = 'application/json'
            return [to_json(app)]

    @doc.response(403, 'The application does not belong to the user')
    @doc.response(404, 'Application not found')
    @require_certificate
    def update_app(self, client_id):
        """
        Update an application
        """
        user = pylons.request.environ['fts3.User.Credentials']
        app = Session.query(OAuth2Application).get(client_id)
        if not app:
            raise HTTPNotFound('Application not found')
        if app.owner != user.user_dn:
            raise HTTPForbidden()
        if pylons.request.headers['Content-Type'].startswith('application/json'):
            fields = json.loads(pylons.request.body)
        else:
            fields = pylons.request.POST

        try:
            if 'delete' not in fields:
                app.description = fields.get('description', '')
                app.website = fields.get('website', '')
                app.redirect_to = fields.get('redirect_to', '')
                Session.merge(app)
                Session.commit()
                redirect(url_for(controller='oauth2', action='get_app'), code=HTTPSeeOther.code)
            else:
                Session.delete(app)
                Session.query(OAuth2Token).filter(OAuth2Token.client_id == client_id).delete()
                Session.query(OAuth2Code).filter(OAuth2Code.client_id == client_id).delete()
                Session.commit()
                redirect(url_for(controller='oauth2', action='get_my_apps'), code=HTTPSeeOther.code)
        except:
            Session.rollback()
            raise

    @doc.response(403, 'The application does not belong to the user')
    @doc.response(404, 'Application not found')
    @require_certificate
    def delete_app(self, client_id):
        """
        Delete an application from the database
        """
        user = pylons.request.environ['fts3.User.Credentials']
        app = Session.query(OAuth2Application).get(client_id)
        if app is None:
            raise HTTPNotFound('Application not found')
        if app.owner != user.user_dn:
            raise HTTPForbidden()

        try:
            Session.delete(app)
            Session.query(OAuth2Token).filter(OAuth2Token.client_id == client_id).delete()
            Session.query(OAuth2Code).filter(OAuth2Code.client_id == client_id).delete()
            Session.commit()
        except:
            Session.rollback()
            raise

        log.info("Application removed: %s" % client_id)

        return None

    def _auth_fields(self):
        req = pylons.request.GET
        auth = dict(
            response_type=req.get('response_type', 'code'),
            client_id=req.get('client_id', None),
            state=None,
            redirect_uri=req.get('redirect_uri', None)
        )

        if not auth['client_id']:
            raise OAuth2Error('Missing client id')

        app = Session.query(OAuth2Application).get(auth['client_id'])
        if not app:
            raise OAuth2Error('Invalid client id')

        redirections = [r.strip() for r in app.redirect_to.split('\n')]
        if auth['redirect_uri']:
            if auth['redirect_uri'] not in redirections:
                raise OAuth2Error('Redirection endpoint unknown!')
        else:
            auth['redirect_uri'] = redirections[0]

        if auth['redirect_uri'] != URN_NO_REDIRECT:
            redirect_parsed = urlparse.urlparse(auth['redirect_uri'])
            if redirect_parsed.hostname != 'localhost' and redirect_parsed.scheme != 'https':
                raise OAuth2Error('Redirection endpoint is not https!')

        # Populate state from unused query args
        auth['state'] = dict(
            filter(
                lambda p: p[0] not in ['response_type', 'client_id', 'redirect_uri'],
                req.iteritems()
            )
        )
        return auth, app

    @require_certificate
    def authorize(self):
        """
        Perform OAuth2 authorization step
        """
        user = pylons.request.environ['fts3.User.Credentials']
        try:
            auth, app = self._auth_fields()
        except OAuth2Error, e:
            return render(
                '/authz_failure.html',
                extra_vars={'reason': str(e), 'site': pylons.config['fts3.SiteName']}
            )

        authorized = self.oauth2_provider.is_already_authorized(user.delegation_id, app.client_id)
        if authorized:
            response = self.oauth2_provider.get_authorization_code(
                    auth['response_type'], auth['client_id'],
                    auth['redirect_uri'], **auth['state']
            )
            for (k, v) in response.headers.iteritems():
                pylons.response.headers[str(k)] = str(v)

            if auth['redirect_uri'] == URN_NO_REDIRECT:
                location = pylons.response.headers['Location']
                del pylons.response.headers['Location']
                return render(
                    '/authz_noredirect.html',
                    extra_vars={
                        'params': urlparse.parse_qs(urlparse.urlparse(location).query),
                        'site': pylons.config['fts3.SiteName']
                    }
                )
            else:
                pylons.response.status_int = response.status_code
                return response.raw
        else:
            csrftoken = random_ascii_string(32)
            pylons.response.set_cookie('fts3oauth2_csrf', csrftoken, max_age=300)
            return render(
                '/authz_confirm.html',
                extra_vars={
                    'app': app,
                    'user': user,
                    'site': pylons.config['fts3.SiteName'],
                    'CSRFToken': csrftoken
                }
            )

    @require_certificate
    def confirm(self):
        """
        Triggered by user action. Confirm, or reject, access.
        """
        user = pylons.request.environ['fts3.User.Credentials']
        try:
            auth, app = self._auth_fields()

            if 'accept' in pylons.request.POST:
                cookie_csrftoken = pylons.request.cookies.get('fts3oauth2_csrf')
                form_csrftoken = pylons.request.POST.get('CSRFToken', None)

                if cookie_csrftoken != form_csrftoken or cookie_csrftoken is None:
                    log.critical("Got something that looks like a CSRF attempt!")
                    log.critical("User: %s (%s)" % (user.user_dn, user.method))
                    log.critical("App id: %s" % auth['client_id'])
                    log.critical("Origin: %s" % pylons.request.headers.get('Origin'))
                    log.critical("Referer: %s" % pylons.request.headers.get('Referer'))
                    raise OAuth2Error('Cross-site request forgery token mismatch! Authorization denied')

                log.info("User %s authorized application %s" % (user.user_dn, auth['client_id']))

                response = self.oauth2_provider.get_authorization_code(
                    auth['response_type'], auth['client_id'],
                    auth['redirect_uri'], **auth['state']
                )
                for (k, v) in response.headers.iteritems():
                    pylons.response.headers[str(k)] = str(v)

                if auth['redirect_uri'] == URN_NO_REDIRECT:
                    location = pylons.response.headers['Location']
                    del pylons.response.headers['Location']
                    return render(
                        '/authz_noredirect.html',
                        extra_vars={
                            'params': urlparse.parse_qs(urlparse.urlparse(location).query),
                            'site': pylons.config['fts3.SiteName']
                        }
                    )
                else:
                    pylons.response.status_int = response.status_code
                    return response.raw
            else:
                redirect(url_for(controller='oauth2', action='get_my_apps'), code=HTTPSeeOther.code)
        except OAuth2Error, e:
            pylons.response.status_int = 403
            return render(
                '/authz_failure.html',
                extra_vars={'reason': str(e), 'site': pylons.config['fts3.SiteName']}
            )

    def get_token(self):
        """
        Get an access token
        """
        if pylons.request.method == 'GET':
            req = pylons.request.GET
        else:
            req = pylons.request.POST

        if req.get('grant_type', None) == 'authorization_code':
            for field in ['grant_type', 'client_id', 'client_secret', 'redirect_uri', 'code']:
                if field not in req:
                    raise HTTPBadRequest("%s missing" % field)
            response = self.oauth2_provider.get_token(**req)
            log.info(
                "Application %s got a a new access token from code %s" % (req['client_id'], req['code'])
            )
        else:
            for field in ['grant_type', 'client_id', 'client_secret', 'refresh_token']:
                if field not in req:
                    raise HTTPBadRequest("%s missing" % field)
            response = self.oauth2_provider.refresh_token(**req)
            log.info("Application %s refreshed the token %s" % (req['client_id'], req['refresh_token']))

        for (k, v) in response.headers.iteritems():
            pylons.response.headers[str(k)] = str(v)
        pylons.response.status_int = response.status_code
        return response.raw

    @require_certificate
    def revoke_token(self, client_id):
        """
        Current user revokes all tokens for a given application
        """
        user = pylons.request.environ['fts3.User.Credentials']
        try:
            Session.query(OAuth2Token).filter(
                (OAuth2Token.client_id == client_id) & (OAuth2Token.dlg_id == user.delegation_id)
            ).delete()
            Session.query(OAuth2Code).filter(
                (OAuth2Code.client_id == client_id) & (OAuth2Code.dlg_id == user.delegation_id)
            )
            Session.commit()
        except:
            Session.rollback()
            raise
        log.warning("User %s revoked application %s" % (user.user_dn, client_id))
        redirect(url_for(controller='oauth2', action='get_my_apps'), code=HTTPSeeOther.code)

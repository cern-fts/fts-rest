#   Copyright notice:
#   Copyright  Members of the EMI Collaboration, 2013.
#
#   See www.eu-emi.eu for details on the copyright holders
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

import logging

from fts3rest.lib.base import Session
from fts3.model import BannedDN
from credentials import UserCredentials, InvalidCredentials
from sqlalchemy.exc import DatabaseError
from webob.exc import HTTPUnauthorized, HTTPForbidden, HTTPError


log = logging.getLogger(__name__)


class FTS3AuthMiddleware(object):
    """
    Pylons middleware to wrap the authentication as part of the request
    process.
    """

    def __init__(self, wrap_app, config):
        self.app    = wrap_app
        self.config = config

    def _get_credentials(self, environ):
        try:
            credentials = UserCredentials(environ, self.config['fts3.Roles'])
        except InvalidCredentials, e:
            raise HTTPForbidden('Invalid credentials (%s)' % str(e))

        if not credentials.user_dn:
            raise HTTPUnauthorized('A valid X509 certificate or proxy is needed')

        if not self._has_authorized_vo(credentials):
            raise HTTPForbidden('The user does not belong to any authorized vo')

        if self._is_banned(credentials):
            raise HTTPForbidden('The user has been banned')

        return credentials

    def __call__(self, environ, start_response):
        try:
            credentials = self._get_credentials(environ)
            environ['fts3.User.Credentials'] = credentials
            log.info("%s logged in via %s" % (credentials.user_dn, credentials.method))
        except HTTPError, e:
            log.error(e.detail)
            return e(environ, start_response)
        except DatabaseError, e:
            log.error("Database error when trying to get user's credentials: %s" % str(e))
            Session.remove()
            raise
        except Exception, e:
            log.error("Unexpected error when trying to get user's credentials: %s" % str(e))
            raise
        else:
            return self.app(environ, start_response)

    def _has_authorized_vo(self, credentials):
        if '*' in self.config['fts3.AuthorizedVO']:
            return True
        for v in credentials.vos:
            if v in self.config['fts3.AuthorizedVO']:
                return True
        return False

    def _is_banned(self, credentials):
        banned = Session.query(BannedDN).get(credentials.user_dn)
        return banned is not None

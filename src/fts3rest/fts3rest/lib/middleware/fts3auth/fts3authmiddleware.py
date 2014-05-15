#   Copyright notice:
#   Copyright © Members of the EMI Collaboration, 2010.
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

from fts3rest.lib.base import Session
from fts3.model import BannedDN
from credentials import UserCredentials
from webob.exc import HTTPForbidden


class FTS3AuthMiddleware(object):
    """
    Pylons middleware to wrap the authentication as part of the request
    process.
    """

    def __init__(self, wrap_app, config):
        self.app    = wrap_app
        self.config = config

    def __call__(self, environ, start_response):
        credentials = UserCredentials(environ, self.config['fts3.Roles'])

        if not credentials.user_dn:
            return HTTPForbidden('A valid X509 certificate or proxy is needed')(environ, start_response)

        if not self._has_authorized_vo(credentials):
            return HTTPForbidden('The user does not belong to any authorized vo')(environ, start_response)

        if self._is_banned(credentials):
            return HTTPForbidden('The user has been banned')(environ, start_response)

        environ['fts3.User.Credentials'] = credentials

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

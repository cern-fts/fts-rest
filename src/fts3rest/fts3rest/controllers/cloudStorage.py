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

from pylons import request

from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController
from CSInterface import CSInterface
from webob.exc import HTTPUnauthorized


class CloudstorageController(BaseController):
    """
    Cloud storage support
    """

    def __before__(self):
        user = request.environ['fts3.User.Credentials']
        if user.method == 'unauthenticated':
            raise HTTPUnauthorized

    def _get_user_dn(self):
        user = request.environ['fts3.User.Credentials']
        return user.user_dn

    @doc.return_type(bool)
    def is_registered(self, service):
        """
        Return a boolean indicating if the user has a token registered
        for the given certificate
        """
        controller = CSInterface(self._get_user_dn(), service)
        return controller.is_registered()

    @doc.response(204, 'Token deleted')
    @doc.response(404, 'No token for the user')
    def remove_token(self, service, start_response):
        """
        Remove the token associated with the given service
        """
        controller = CSInterface(self._get_user_dn(), service)
        controller.remove_token()
        start_response('204 No Content', [])
        return ['']

    @doc.response(200, 'Got the request token')
    def get_access_requested(self, service):
        """
        First authorization step: obtain a request token
        """
        controller = CSInterface(self._get_user_dn(), service)
        return controller.get_access_requested()

    @doc.response(404, 'The user has not registered for the given service')
    def is_access_requested(self, service):
        """
        Returns the status of the authorization
        """
        controller = CSInterface(self._get_user_dn(), service)
        return controller.is_access_requested()

    @doc.response(400, 'Previous steps failed or didn\' happen')
    @doc.response(404, 'The storage has not been properly configured')
    def get_access_granted(self, service):
        """
        Third authorization step: get a valid access token
        """
        controller = CSInterface(self._get_user_dn(), service)
        return controller.get_access_granted()

    @doc.query_arg('surl', 'The folder')
    @doc.response(403, 'No token for the given storage')
    def get_folder_content(self, service):
        """
        Get the content of the given directory
        """
        controller = CSInterface(self._get_user_dn(), service)
        return controller.get_folder_content()

    @doc.response(403, 'No token for the given storage')
    def get_file_link(self, service, file_path):
        """
        Get the final HTTP url from the logical file_path inside the cloud storage
        """
        controller = CSInterface(self._get_user_dn(), service)
        return controller.get_file_link(file_path)

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

from fts3rest.lib.base import BaseController
from CSInterface import CSInterface


class CloudstorageController(BaseController):

    def _get_user_dn(self):
        user = request.environ['fts3.User.Credentials']
        return user.user_dn

    def is_registered(self, service):
        controller = CSInterface(self._get_user_dn(), service)
        return controller.is_registered()

    def get_access_requested(self, service):
        controller = CSInterface(self._get_user_dn(), service)
        return controller.get_access_requested()

    def is_access_requested(self, service):
        controller = CSInterface(self._get_user_dn(), service)
        return controller.is_access_requested()

    def get_access_granted(self, service):
        controller = CSInterface(self._get_user_dn(), service)
        return controller.get_access_granted()

    def get_folder_content(self, service):
        controller = CSInterface(self._get_user_dn(), service)
        return controller.get_folder_content()

    def get_file_link(self, service, file_path):
        controller = CSInterface(self._get_user_dn(), service)
        return controller.get_file_link(file_path)

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

    def _getUserDN(self):
        user = request.environ['fts3.User.Credentials']
        return user.user_dn

    def isCSRegistered(self, service):
        controller = CSInterface(self._getUserDN(), service)
        return controller.isCSRegistered()

    def getCSAccessRequested(self, service):
        controller = CSInterface(self._getUserDN(), service)
        return controller.getCSAccessRequested()

    def isCSAccessRequested(self, service):
        controller = CSInterface(self._getUserDN(), service)
        return controller.isCSAccessRequested()

    def getCSAccessGranted(self, service):
        controller = CSInterface(self._getUserDN(), service)
        return controller.getCSAccessGranted()

    def getCSFolderContent(self, service):
        controller = CSInterface(self._getUserDN(), service)
        return controller.getCSFolderContent()

    def getCSFileLink(self, service, file_path):
        controller = CSInterface(self._getUserDN(), service)
        return controller.getCSFileLink(file_path)

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

# Interface class for all cloud storages (Dropbox, ownCloud, etc)
#
# Usage: (example of class creation and method call)
#    var conClass = CSInterface(userDN, serviceName).getInstance()
#    conClass.is_registered()
#
# Andres Abad Rodriguez <andres.abad.rodriguez@cern.ch>
#

from CSdropbox import DropboxConnector
#import importlib


class CSInterface(object):

    def __init__(self, user_dn, service):

       # try:
            # Dynamic load of the class required for this External Storage
            #module = __import__("CS" + service.strip().lower())

            #mName = service.strip().lower().title() + "Connector"
            #module = importlib.import_module("CS" + service.strip().lower() + "." + mName)

        #    mName = service.strip().lower().title() + "Connector"
        #    mod = __import__("CS" + service.strip().lower(), fromlist=[mName])
        #    module = mod.mName
        #except Exception, e:
        #    raise e

        #try:
        #    class_ = getattr(module, service)
            # new instance of the class
         #   self.CSClass = class_(self.userDN, self.service)

        #except Exception, e:
        #    raise e
        self.user_dn = user_dn
        self.service = service.strip().lower()
        if self.service == "dropbox":
            self.__class__ = DropboxConnector

    def is_registered(self):
        raise NotImplemented()

    def get_access_requested(self):
        raise NotImplemented()

    def is_access_requested(self):
        raise NotImplemented()

    def get_access_granted(self):
        raise NotImplemented()

    def get_folder_content(self):
        raise NotImplemented()

    def get_file_link(self, file_path):
        raise NotImplemented()

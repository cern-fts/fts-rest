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

import pkgutil
import sys


class Authenticator(object):
    """
    Wraps different authentication methods installed in this directory.
    The 'do_authentication' call must:
        * Return True and set the credentials parameter if
          the recognised method is used and valid.
        * Return False if the recognised method is _NOT_ in use
        * Raise InvalidCredentials is the recognised method _IS_ in use, but invalid
    """

    def __init__(self):
        _current_module = sys.modules[__name__]
        _prefix = _current_module.__name__ + '.'
        self._auth_modules = list()
        for importer, modname, ispkg in pkgutil.iter_modules(_current_module.__path__, _prefix):
            _authnmod = importer.find_module(modname).load_module(modname)
            if hasattr(_authnmod, 'do_authentication'):
                self._auth_modules.append(_authnmod)

    def __call__(self, credentials, env):
        """
        Iterate through pluggable authentication modules
        """
        for authnmod in self._auth_modules:
            if authnmod.do_authentication(credentials, env):
                return True
        return False

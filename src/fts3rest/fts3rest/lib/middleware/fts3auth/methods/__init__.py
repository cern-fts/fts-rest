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


def do_authentication(credentials, env):
    """
    Iterate through pluggable authentication modules
    """
    current_module = sys.modules[__name__]
    prefix = current_module.__name__ + '.'
    for importer, modname, ispkg in pkgutil.iter_modules(current_module.__path__, prefix):
        authnmod = importer.find_module(modname).load_module(modname)
        if hasattr(authnmod, 'do_authentication'):
            if authnmod.do_authentication(credentials, env):
                return True
    return False

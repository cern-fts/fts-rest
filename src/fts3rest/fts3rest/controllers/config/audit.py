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

try:
    import simplejson as json
except:
    import json
import logging

from fts3.model import *
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import accept
from fts3rest.lib.middleware.fts3auth import authorize
from fts3rest.lib.middleware.fts3auth.constants import *

__controller__ = 'ConfigAuditController'
log = logging.getLogger(__name__)


class ConfigController(BaseController):
    """
    Config audit
    """

    @doc.return_type(array_of=ConfigAudit)
    @authorize(CONFIG)
    @accept(html_template='/config/audit.html')
    def audit(self):
        """
        Returns the last 100 entries of the config audit tables
        """
        return Session.query(ConfigAudit).order_by(ConfigAudit.datetime.desc()).limit(100).all()

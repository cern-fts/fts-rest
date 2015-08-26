#   Copyright notice:
#
#   Copyright CERN 2013-2015
#
#   Copyright Members of the EMI Collaboration, 2013.
#       See www.eu-emi.eu for details on the copyright holders
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
from pylons import request

from fts3.model import *
from fts3rest.controllers.config import audit_configuration
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify, get_input_as_dict
from fts3rest.lib.http_exceptions import *
from fts3rest.lib.middleware.fts3auth import authorize
from fts3rest.lib.middleware.fts3auth.constants import *


__controller__ = 'DrainController'
log = logging.getLogger(__name__)


class DrainController(BaseController):
    """
    Drain operations
    """

    @doc.response(400, 'Bad request. Invalid host or invalid drain value')
    @doc.response(403, 'The user is not allowed to change the configuration')
    @authorize(CONFIG)
    @jsonify
    def set_drain(self):
        """
        Set the drain status of a server
        """
        input_dict = get_input_as_dict(request)

        hostname = input_dict.get('hostname')
        try:
            drain = input_dict.get('drain', 'true').lower() == 'true'
        except:
            raise HTTPBadRequest('Invalid drain value')

        entries = Session.query(Host).filter(Host.hostname == hostname).all()
        if not entries:
            raise HTTPBadRequest('Host not found')

        try:
            for entry in entries:
                entry.drain = drain
                Session.merge(entry)
                audit_configuration(
                    'drain', 'Turning drain %s the drain mode for %s' % (drain, hostname)
                )
            Session.commit()
        except:
            Session.rollback()
            raise

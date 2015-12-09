#   Copyright notice:
#   Copyright CERN, 2015.
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

from fts3.model import File
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.middleware.fts3auth import authorize, require_certificate
from fts3rest.lib.middleware.fts3auth.constants import *
from fts3rest.lib.helpers import jsonify


__controller__ = 'ServerStatusController'


class ServerStatusController(BaseController):
    """
    Server general status
    """

    @require_certificate
    @authorize(CONFIG)
    @jsonify
    def hosts_activity(self):
        """
        What are the hosts doing
        """
        staging = Session.execute(
            "SELECT COUNT(*), agent_dn "
            " FROM t_file "
            " WHERE file_state = 'STARTED' "
            " GROUP BY agent_dn")
        response = dict()

        for (count, host) in staging:
            response[host] = dict(staging=count)

        active = Session.execute(
            "SELECT COUNT(*), transferHost "
            " FROM t_file "
            " WHERE file_state = 'ACTIVE' "
            " GROUP BY transferHost"
        )
        for (count, host) in active:
            if host not in response:
                response[host] = dict()
            response[host]['active'] = count

        return response

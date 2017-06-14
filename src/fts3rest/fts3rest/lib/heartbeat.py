#   Copyright notice:
#   Copyright CERN, 2017
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


import logging
import socket
import time
from datetime import datetime
from threading import Thread

from fts3.model import Host
from fts3rest.lib.base import Session

log = logging.getLogger(__name__)


class Heartbeat(Thread):
    """
    Keeps running on the background updating the db marking the process as alive
    """

    def __init__(self, tag, interval):
        """
        Constructor
        """
        Thread.__init__(self)
        self.tag = tag
        self.interval = interval
        self.daemon = True

    def run(self):
        """
        Thread logic
        """
        host = Host(
            hostname=socket.getfqdn(),
            service_name=self.tag,
        )

        while self.interval:
            host.beat = datetime.utcnow()
            try:
                Session.merge(host)
                Session.commit()
                log.debug('Hearbeat')
            except Exception, e:
                log.warning("Failed to update the heartbeat: %s" % str(e))
            time.sleep(self.interval)

#   Copyright notice:
#   Copyright CERN, 2018
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
import time
import socket
from threading import Thread
from datetime import datetime, timedelta
from fts3.model import Host
from fts3.model import Credential
from fts3rest.lib.base import Session
from fts3rest.lib.openidconnect import oidc_manager

log = logging.getLogger(__name__)


class IAMTokenRefresher(Thread):
    """
    Keeps running on the background updating the db marking the process as alive
    """

    def __init__(self, tag, config):
        """
        Constructor
        """
        Thread.__init__(self)
        self.daemon = True
        self.tag = tag
        self.interval = int(config.get('fts3.TokenRefreshDaemonIntervalInSeconds', 600))
        self.config = config

    def run(self):
        """
        Thread logic
        """
        # verify that no other fts-token-refresh-daemon is running on this machine so as
        # to make sure that no two fts-token-refresh-daemons run simultaneously
        service_name = Session.query(Host).filter(Host.service_name == self.tag).first()

        condition = (datetime.utcnow() - service_name.beat) > timedelta(seconds=self.interval)
        if not service_name or condition:
            host = Host(hostname=socket.getfqdn(), service_name=self.tag)
            while self.interval:
                host.beat = datetime.utcnow()
                try:
                    Session.merge(host)
                    Session.commit()
                    log.debug('fts-token-refresh-daemon heartbeat')
                except Exception, e:
                    log.warning("Failed to update the fts-token-refresh-daemon heartbeat: %s" % str(e))

                credentials = Session.query(Credential).filter(Credential.proxy.notilike("%CERTIFICATE%")).all()
                log.debug('{} credentials to refresh'.format(len(credentials)))
                for credential in credentials:
                    try:
                        credential = oidc_manager.refresh_access_token(credential)
                        log.debug('OK refresh_access_token')
                        Session.merge(credential)
                        Session.commit()
                    except Exception, e:
                        log.warning("Failed to refresh token for dn: %s because: %s" % (str(credential.dn), str(e)))
                time.sleep(self.interval)

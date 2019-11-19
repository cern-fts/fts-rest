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
import socket
import time
from datetime import datetime, timedelta
from threading import Thread

from fts3rest.lib.base import Session
from fts3rest.lib.openidconnect import oidc_manager

from fts3.model import Credential, Host

log = logging.getLogger(__name__)


class IAMTokenRefresher(Thread):
    """
    Daemon thread that refreshes all access tokens in the DB at every interval.

    Keeps running on the background updating the DB, marking the process as alive.
    There should be ONLY ONE across all instances.
    Keep in mind that with the Apache configuration line
        WSGIDaemonProcess fts3rest python-path=... processes=2 threads=15
    there will be 2 instances of the application per server, meaning we need to check that there is only one
    IAMTokenRefresher per host, and only one between all hosts.
    """

    def __init__(self, tag, config):
        Thread.__init__(self)
        self.daemon = True  # The thread will immediately exit when the main thread exit
        self.tag = tag
        self.interval = int(config.get('fts3.TokenRefreshDaemonIntervalInSeconds', 600))
        self.config = config

    def run(self):
        # verify that no other fts-token-refresh-daemon is running on this machine so as
        # to make sure that no two fts-token-refresh-daemons run simultaneously
        service_name = Session.query(Host).filter(Host.service_name == self.tag).first()

        # todo: fix this condition, if time between restarting server is less than interval, thread won't run
        # also, should remove from DB when exiting (catch exit exception?)
        #condition = (datetime.utcnow() - service_name.beat) > timedelta(seconds=self.interval)
        condition = True

        if not service_name or condition:
            log.debug('thread running')
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
        else:
            log.debug('thread skipping')

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
import random
from datetime import datetime, timedelta
from threading import Thread

from fts3rest.lib.base import Session
from fts3rest.lib.openidconnect import oidc_manager
from fts3.model import Credential, Host

from sqlalchemy.exc import SQLAlchemyError

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

    Todo: should use a different Session (it is non concurrent)
    """

    def __init__(self, tag, config):
        Thread.__init__(self)
        self.daemon = True  # The thread will immediately exit when the main thread exits
        self.tag = tag
        self.refresh_interval = int(config.get('fts3.TokenRefreshDaemonIntervalInSeconds', 600))
        self.config = config

    def _thread_not_active(self, thread):
        # The thread is considered not active if it hasn't updated the DB for 2*refresh_interval
        return (datetime.utcnow() - thread.beat) > timedelta(seconds=2 * self.refresh_interval)

    def run(self):
        """
        Regularly check if there is another active IAMTokenRefresher in the DB. If not, become the active thread.
        """
        # The interval at which the thread will check if there is another active thread.
        # It is arbitrary: I chose 2 times the refresh interval, plus a random offset to avoid multiple threads
        # checking at the same time (although DB access is transactional)
        db_check_interval = 2 * self.refresh_interval + random.randint(0, 120)
        while True:
            # Check that no other fts-token-refresh-daemon is running on this server
            refresher_threads = Session.query(Host).filter(Host.service_name == self.tag).all()
            if all(self._thread_not_active(thread) for thread in refresher_threads):
                log.debug('Activating thread')
                for thread in refresher_threads:
                    Session.delete(thread)
                host = Host(hostname=socket.getfqdn(), service_name=self.tag)
                while True:
                    host.beat = datetime.utcnow()
                    try:
                        Session.merge(host)
                        Session.commit()
                        log.debug('fts-token-refresh-daemon heartbeat')
                    except SQLAlchemyError as ex:
                        log.warning("Failed to update the fts-token-refresh-daemon heartbeat: %s" % str(ex))
                        Session.rollback()
                        raise

                    credentials = Session.query(Credential).filter(Credential.proxy.notilike("%CERTIFICATE%")).all()
                    log.debug('{} credentials to refresh'.format(len(credentials)))
                    for credential in credentials:
                        try:
                            credential = oidc_manager.refresh_access_token(credential)
                            log.debug('OK refresh_access_token')
                            Session.merge(credential)
                            Session.commit()
                        except Exception as ex:
                            log.warning("Failed to refresh token for dn: %s because: %s" % (str(credential.dn),
                                                                                            str(ex)))
                            Session.rollback()
                            raise
                    time.sleep(self.refresh_interval)
            else:
                log.debug('Another thread is active -- Going to sleep')
                time.sleep(db_check_interval)

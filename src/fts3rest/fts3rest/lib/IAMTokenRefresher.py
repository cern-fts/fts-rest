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
import json
import time
import socket
from fts3.model import Host
from threading import Thread
from fts3.rest.client.request import Request
from datetime import datetime, timedelta

from fts3.model import Credential
from fts3rest.lib.base import Session

log = logging.getLogger(__name__)


class IAMTokenRefresher(Thread):
    """
    Keeps running on the background updating the db marking the process as alive
    """

    def __init__(self, tag, interval, config):
        """
        Constructor
        """
        Thread.__init__(self)
        self.tag = tag
        self.interval = interval
        self.daemon = True
        self.config = config

    def _refresh_token(self, credential):
        # Request a new access token based on the refresh token
        requestor = Request(None, None)  # VERIFY:TRUE

        refresh_token = credential.proxy.split(':')[1]
        body = {'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': self.config['fts3.ClientId'],
                'client_secret': self.config['fts3.ClientSecret']}

        new_credential = json.loads(
            requestor.method('POST', self.config['fts3.AuthorizationProviderTokenEndpoint'], body=body,
                             user=self.config['fts3.ClientId'],
                             passw=self.config['fts3.ClientSecret']))

        credential.proxy = new_credential['access_token'] + ':' + new_credential['refresh_token']
        credential.termination_time = datetime.utcfromtimestamp(new_credential['exp'])

        return credential

    def _check_if_token_should_be_refreshed(self, credential):
        last_submitted_querry = "SELECT j.submit_time " \
                                "FROM t_job j " \
                                "LEFT JOIN t_credential c on j.user_dn = c.dn " \
                                "WHERE c.dn =\'{}\' " \
                                "ORDER BY submit_time DESC " \
                                "LIMIT 1"
        latest = Session.execute(last_submitted_querry.format(credential.dn)).fetchone()

        if (len(latest) > 0) and ((datetime.utcnow() - latest[0]) < timedelta(seconds=int(
                self.config.get('fts3.TokenRefreshTimeSinceLastTransferInSeconds', 2629743)))):
            return True
        return False

    def run(self):
        """
        Thread logic
        """

        # verify that no other fts-token-refresh-daemon is running on this machine so as
        # to make sure that no two fts-token-refresh-daemons run simultaneously
        service_name = Session.query(Host).filter(Host.service_name == self.tag).first()

        if not service_name or (service_name and (datetime.utcnow() - service_name.beat) > timedelta(
                seconds=int(self.interval))):

            host = Host(
                hostname=socket.getfqdn(),
                service_name=self.tag,
            )

            while self.interval:

                host.beat = datetime.utcnow()
                try:
                    Session.merge(host)
                    Session.commit()
                    log.debug('fts-token-refresh-daemon heartbeat')
                except Exception, e:
                    log.warning("Failed to update the fts-token-refresh-daemon heartbeat: %s" % str(e))

                credentials = Session.query(Credential).filter(Credential.proxy.notilike("%CERTIFICATE%")).all()

                for c in credentials:
                    try:
                        if self._check_if_token_should_be_refreshed(c):
                            c = self._refresh_token(c)
                            Session.merge(c)
                            Session.commit()
                    except Exception, e:
                        log.warning("Failed to refresh token for dn: %s because: %s" % (str(c.dn), str(e)))
                time.sleep(self.interval)

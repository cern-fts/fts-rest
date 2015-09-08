#   Copyright notice:
#   Copyright CERN, 2015.
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

import json
from base import Base


class ServerStatus(Base):

    def __init__(self):
        super(ServerStatus, self).__init__(
            description="Use this command to check on the service status.",
        )

        self.opt_parser.add_option('-H', '--host', dest='host', default=None,
                                   help='limit the output to a given host')
        self.opt_parser.add_option('--is-active', dest='is_active',
                                   default=False, action='store_true',
                                   help='the tool will return < 0 on error, 0 if nothing is active, '
                                        '1 if there are active transfers, 2 if there are active staging, 3 if there are both ')

    def run(self):
        context = self._create_context()
        host_activity = json.loads(context.get('/status/hosts'))
        hosts = [self.options.host] if self.options.host else host_activity.keys()
        total_count = dict(active=0, staging=0)
        for host in hosts:
            self.logger.info(host)
            for state, count in host_activity.get(host, {}).iteritems():
                self.logger.info("\t%s: %d" % (state, count))
                total_count[state] += count

        if self.options.is_active:
            return ((total_count['active'] > 0) * 1) + ((total_count['staging'] > 0) * 2)
        else:
            return 0

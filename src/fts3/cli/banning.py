#   Copyright notice:
#   Copyright  CERN, 2014.
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

import sys

from base import Base
from fts3.rest.client import Ban


class Banning(Base):

    def __init__(self):
        super(Banning, self).__init__(
            description="Ban and unban storage elements and users",
            example="""
                $ %(prog)s -s https://fts3-devel.cern.ch:8446 --storage gsiftp://sample
                No jobs affected
                $ %(prog)s -s https://fts3-devel.cern.ch:8446 --storage gsiftp://sample --unban
                $
            """
        )

        self.opt_parser.add_option('--storage', dest='storage',
                                   help='storage element')
        self.opt_parser.add_option('--user', dest='user_dn',
                                   help='user dn')
        self.opt_parser.add_option('--unban', dest='unban',
                                   default=False, action='store_true',
                                   help='unban instead of ban')

        self.opt_parser.add_option('--status', dest='status',
                                   default='cancel',
                                   help='status of the jobs that are already in the queue: cancel or wait')
        self.opt_parser.add_option('--timeout', dest='timeout',
                                   default=0,
                                   help='the timeout for the jobs that are already in the queue if status is wait')
        self.opt_parser.add_option('--allow-submit', dest='allow_submit',
                                   default=False, action='store_true',
                                   help='allow submissions if status is wait')

    def validate(self):
        # Some sanity checks
        # This are checked server side anyway (or so they should) but we can shorcurt here
        self.options.status = self.options.status.lower()
        if self.options.status not in ['cancel', 'wait']:
            self.logger.critical('Status can only be cancel or wait')
            sys.exit(1)

        if self.options.status == 'cancel':
            if self.options.allow_submit:
                self.logger.critical('--allow-submit can only be used with --status=wait')
                sys.exit(1)
        else:
            if self.options.user_dn:
                self.logger.critical('--user only accept cancel')
                sys.exit(1)

        if (not self.options.storage and not self.options.user_dn) or (self.options.storage and self.options.user_dn):
            self.logger.critical('Need to specify only one of --storage or --user')
            sys.exit(1)

    def run(self):
        context = self._create_context()
        ban = Ban(context)

        affected_jobs = None
        if self.options.storage:
            if self.options.unban:
                ban.unban_se(self.options.storage)
            else:
                affected_jobs = ban.ban_se(
                    self.options.storage, self.options.status, self.options.timeout, self.options.allow_submit
                )
        else:
            if self.options.unban:
                ban.unban_dn(self.options.user_dn)
            else:
                affected_jobs = ban.ban_dn(self.options.user_dn)

        if affected_jobs:
            self.logger.info('Affected jobs:')
            for j in affected_jobs:
                self.logger.info(j)
        elif not self.options.unban:
            self.logger.info('No jobs affected')

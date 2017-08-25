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

from base import Base
from fts3.rest.client import Delegator as Deleg
from datetime import timedelta

class Delegator(Base):

    def __init__(self):
        super(Delegator, self).__init__(
            description="This command can be used to (re)delegate your credentials to the FTS3 server",
            example="""
            $ %(prog)s -s https://fts3-devel.cern.ch:8446
            Delegation id: 9a4257f435fa2010"
            """
        )

        self.opt_parser.add_option('-f', '--force', dest='force',
                                   default=False, action='store_true',
                                   help='force the delegation')

        self.opt_parser.add_option('-H', '--hours', dest='duration',
                                   default=12, type='int',
                                   help='Duration of the delegation in hours (Default: 12)')

    def run(self):
        context = self._create_context()
        delegator = Deleg(context)
        delegation_id = delegator.delegate(lifetime=timedelta(hours=self.options.duration),force=self.options.force)
        self.logger.info("Delegation id: %s" % delegation_id)
        self.logger.debug("Termination time: %s" % delegator.get_info()['termination_time'])
        return delegation_id

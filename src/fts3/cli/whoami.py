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

import json

from base import Base
from fts3.rest.client import Inquirer


class WhoAmI(Base):

    def run(self):
        context = self._create_context()
        inquirer = Inquirer(context)
        whoami = inquirer.whoami()

        if self.options.json:
            print json.dumps(whoami, indent=2)
        else:
            self.logger.info("User DN: %s" % whoami['dn'][0])
            for vo in whoami['vos']:
                self.logger.info("VO: %s" % vo)
            self.logger.info("Delegation id: %s" % whoami['delegation_id'])

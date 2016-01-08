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

try:
    import simplejson as json
except:
    import json 

from base import Base
from fts3.rest.client import Inquirer


class WhoAmI(Base):

    def __init__(self):
        super(WhoAmI, self).__init__(
            description="""
            This command exists for convenience. It can be used to check, as the name suggests,
            who are we for the server.
            """,
            example="""
            $ %(prog)s -s https://fts3-pilot.cern.ch:8446
            User DN: /DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=saketag/CN=678984/CN=Alejandro Alvarez Ayllon
            VO: dteam
            VO: dteam/cern
            Delegation id: 9a4257f435fa2010
            """
        )

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
            for vo_id in whoami['vos_id']:
                self.logger.info("VO id: %s" % vo_id)
            self.logger.info("Delegation id: %s" % whoami['delegation_id'])
            self.logger.info("Base id: %s" % whoami['base_id'])

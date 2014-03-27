import json
import logging
import sys

from base import Base
from fts3.rest.client import Context, Inquirer


class WhoAmI(Base):

    def __init__(self, argv=sys.argv[1:]):
        super(WhoAmI, self).__init__()

        (self.options, self.args) = self.opt_parser.parse_args(argv)

        if self.options.verbose:
            self.logger.setLevel(logging.DEBUG)

        if self.options.endpoint is None:
            self.logger.critical('Need an endpoint')
            sys.exit(1)

    def __call__(self):
        context = Context(self.options.endpoint, ukey=self.options.ukey, ucert=self.options.ucert)
        inquirer = Inquirer(context)
        whoami = inquirer.whoami()

        if self.options.json:
            print json.dumps(whoami, indent=2)
        else:
            self.logger.info("User DN: %s" % whoami['dn'][0])
            for vo in whoami['vos']:
                self.logger.info("VO: %s" % vo)
            self.logger.info("Delegation id: %s" % whoami['delegation_id'])

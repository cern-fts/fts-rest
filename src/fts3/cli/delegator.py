import logging
import sys

from base import Base
from fts3.rest.client import Delegator as Deleg, Context


class Delegator(Base):

    def __init__(self, argv=sys.argv[1:]):
        super(Delegator, self).__init__()

        self.opt_parser.add_option('-f', '--force', dest='force',
                                   default=False, action='store_true',
                                   help='force the delegation')

        (self.options, self.args) = self.opt_parser.parse_args(argv)

        if self.options.verbose:
            self.logger.setLevel(logging.DEBUG)

        if self.options.endpoint is None:
            self.logger.critical('Need an endpoint')
            sys.exit(1)

    def __call__(self):
        context = Context(self.options.endpoint, ukey=self.options.ukey, ucert=self.options.ucert)
        delegator = Deleg(context)
        delegation_id = delegator.delegate(force=self.options.force)
        self.logger.info("Delegation id: %s" % delegation_id)
        self.logger.debug("Termination time: %s" % delegator.get_info()['termination_time'])
        return delegation_id

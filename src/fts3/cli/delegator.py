from base import Base
from datetime import timedelta
from fts3.rest.client import Delegator as Deleg, Context
import logging
import sys
import time



class Delegator(Base):
	
	def __init__(self, argv = sys.argv[1:]):
		super(Delegator, self).__init__()

		(self.options, self.args) = self.optParser.parse_args(argv)

		if self.options.verbose:
			self.logger.setLevel(logging.DEBUG)

		if self.options.endpoint is None:
			self.logger.critical('Need an endpoint')
			sys.exit(1)


	def __call__(self):
		self.context = Context(self.options.endpoint,
													 ukey=self.options.ukey,
													 ucert=self.options.ucert)

		delegator = Deleg(self.context)
		delegationId = delegator.delegate()
		self.logger.info("Delegation id: %s" % delegationId)
		return delegationId


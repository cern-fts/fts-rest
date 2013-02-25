from fts3.rest.client import Inquirer, Context
from base import Base
from utils import *
import logging
import sys



class JobShower(Base):
	
	def __init__(self, argv = sys.argv[1:]):
		super(JobShower, self).__init__(extra_args = 'JOB_ID')
		
		(self.options, self.args) = self.optParser.parse_args(argv)
		
		if self.options.endpoint is None:
			self.logger.critical('Need an endpoint')
			sys.exit(1)
			
		if len(self.args) == 0:
			self.logger.critical('Need a job id')
			sys.exit(1)
			
		self.jobId = self.args[0]
			
		if self.options.verbose:
			self.logger.setLevel(logging.DEBUG)


	def __call__(self):
		context  = Context(self.options.endpoint)
		inquirer = Inquirer(context)
		job      = inquirer.getJobStatus(self.jobId)
		
		if not self.options.json:
			self.logger.info(job2HumanReadable(job))
		else:
			self.logger.info(job2Json(job))

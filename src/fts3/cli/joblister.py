from fts3.rest.client import Inquirer, Context
from base import Base
from utils import *
import logging
import sys



class JobLister(Base):
	
	def __init__(self, argv = sys.argv[1:]):
		super(JobLister, self).__init__()
		# Specific options
		self.optParser.add_option('-u', '--userdn', dest = 'user_dn',
								  help = 'query only for the given user.')
		self.optParser.add_option('-o', '--voname', dest = 'vo_name',
								  help = 'query only for the given VO.')
		
		# And parse
		(self.options, self.args) = self.optParser.parse_args(argv)
		
		if self.options.endpoint is None:
			self.logger.critical('Need an endpoint')
			sys.exit(1)
			
		if self.options.verbose:
			self.logger.setLevel(logging.DEBUG)
			
	
	def __call__(self):
		self.context = Context(self.options.endpoint,
													 ukey=self.options.ukey,
													 ucert=self.options.ucert)
		
		inquirer = Inquirer(context)
		
		jobList  = inquirer.getJobList(self.options.user_dn, self.options.vo_name)
	
		if not self.options.json:
			self.logger.info(jobList2HumanReadable(jobList))
		else:
			self.logger.info(jobList2Json(jobList))

from optparse import OptionParser
import logging


class Base(object):
	
	def __init__(self):
		self.logger = logging.getLogger()
		
		# Common CLI options
		self.optParser = OptionParser()
		
		self.optParser.add_option('-v', '--verbose', dest = 'verbose', default = False, action = 'store_true',
								  help = 'verbose output.')
		self.optParser.add_option('-s', '--endpoint', dest = 'endpoint',
								  help = 'FTS3 REST endpoint.')
		self.optParser.add_option('-j', dest = 'json', default = False, action = 'store_true',
								  help = 'print the output in JSON format.')

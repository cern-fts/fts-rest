from optparse import OptionParser
import logging


class Base(object):
	
	def __init__(self, extra_args = None):	
		self.logger = logging.getLogger()
		
		# Common CLI options
		usage = None
		if extra_args:
			usage = "usage: %prog [options] " + extra_args
			
		self.optParser = OptionParser(usage = usage)
		
		self.optParser.add_option('-v', '--verbose', dest = 'verbose', default = False, action = 'store_true',
								  help = 'verbose output.')
		self.optParser.add_option('-s', '--endpoint', dest = 'endpoint',
								  help = 'FTS3 REST endpoint.')
		self.optParser.add_option('-j', dest = 'json', default = False, action = 'store_true',
								  help = 'print the output in JSON format.')

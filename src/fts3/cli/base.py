from ConfigParser import ConfigParser
from optparse import OptionParser
import logging
import os

CONFIG_FILENAMES = ['/etc/fts3/fts3client.cfg',
										os.path.expanduser('~/.fts3client.cfg')]

class Base(object):
	
	def __init__(self, extra_args = None):
		self.logger = logging.getLogger()
		
		# Common CLI options
		usage = None
		if extra_args:
			usage = "usage: %prog [options] " + extra_args

		config = ConfigParser(allow_no_value=True, defaults=
				{
					'verbose': 'false',
					'endpoint': None,
					'json': 'false',
					'ukey': None,
					'ucert': None
				}
			)
		config.read(CONFIG_FILENAMES)
		
		self.optParser = OptionParser(usage = usage)
		
		self.optParser.add_option('-v', '--verbose', dest = 'verbose', action = 'store_true',
								  help = 'verbose output.', default=config.getboolean('Main', 'verbose'))
		self.optParser.add_option('-s', '--endpoint', dest = 'endpoint',
								  help = 'FTS3 REST endpoint.', default=config.get('Main', 'endpoint'))
		self.optParser.add_option('-j', dest = 'json', action = 'store_true',
								  help = 'print the output in JSON format.',
									default=config.get('Main', 'json'))
		self.optParser.add_option('--key', dest = 'ukey',
								  help = 'the user certificate private key.',
									default=config.get('Main', 'ukey'))
		self.optParser.add_option('--cert', dest = 'ucert',
								  help = 'the user certificate.',
									default=config.get('Main', 'ucert'))

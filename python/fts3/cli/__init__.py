from joblister import JobLister
from jobshower import JobShower
import logging
import sys


class FTS3CliFormatter(logging.Formatter):
	def format(self, record):
		
		if record.levelno == logging.CRITICAL:
			self._fmt = 'Error: %(msg)s'
		elif record.levelno == logging.DEBUG:
			self._fmt = '# %(msg)s'
		else:
			self._fmt = '%(msg)s'
		
		return super(FTS3CliFormatter, self).format(record)

fmt = FTS3CliFormatter()
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(fmt)
logging.root.addHandler(handler)
logging.root.setLevel(logging.INFO)

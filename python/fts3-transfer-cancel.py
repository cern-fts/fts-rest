#!/usr/bin/env python
from fts3.cli import JobCanceller
import logging
import sys
import traceback


try:
	canceller = JobCanceller(sys.argv[1:])
	canceller()
except Exception, e:
	logging.critical(str(e))
	if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
		traceback.print_exc()
	sys.exit(1)

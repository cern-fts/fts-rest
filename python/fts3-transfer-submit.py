#!/usr/bin/env python
from fts3.cli import JobSubmitter
import logging
import sys
import traceback


try:
	submitter = JobSubmitter(sys.argv[1:])
	submitter()
except Exception, e:
	logging.critical(str(e))
	if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
		traceback.print_exc()
	sys.exit(1)

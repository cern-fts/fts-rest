#!/usr/bin/env python
from fts3.cli import JobLister
import logging
import sys
import traceback

try:
	lister = JobLister(sys.argv[1:])
	lister()
except Exception, e:
	logging.critical(str(e))
	if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
		traceback.print_exc()
	sys.exit(1)

#!/usr/bin/env python
from fts3.cli import JobShower
import logging
import sys
import traceback


try:
	shower = JobShower(sys.argv[1:])
	shower()
except Exception, e:
	logging.critical(str(e))
	if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
		traceback.print_exc()
	sys.exit(1)

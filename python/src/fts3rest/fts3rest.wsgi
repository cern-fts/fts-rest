#!/usr/bin/env python
import os, sys

wd = os.path.dirname(__file__)
if wd not in sys.path:
	sys.path.append(wd)

from paste.deploy import loadapp

application = loadapp('config:%s/development.ini' % wd)

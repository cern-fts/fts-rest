#!/usr/bin/env python

# Need to override the PYTHONPATH for EL6, so slqlachemy 0.8
# is found
import sys
sys.path.insert(0, '/usr/lib64/python2.6/site-packages/SQLAlchemy-0.8.2-py2.6-linux-x86_64.egg/')

from paste.deploy import loadapp
from paste.script.util.logging_config import fileConfig

fileConfig('/etc/fts3/fts3rest.ini')
application = loadapp('config:/etc/fts3/fts3rest.ini')

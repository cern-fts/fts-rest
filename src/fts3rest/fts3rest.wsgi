#!/usr/bin/env python
from paste.deploy import loadapp
from paste.script.util.logging_config import fileConfig

fileConfig('/etc/fts3/fts3rest.ini')
application = loadapp('config:/etc/fts3/fts3rest.ini')

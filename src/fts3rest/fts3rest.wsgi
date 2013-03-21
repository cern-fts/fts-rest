#!/usr/bin/env python
from paste.deploy import loadapp

application = loadapp('config:/etc/fts3/fts3rest.ini')

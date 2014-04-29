#!/usr/bin/env python
#
# How to query whoami
#
import json
import logging
import fts3.rest.client.easy as fts3
from optparse import OptionParser


opts = OptionParser()
opts.add_option('-s', '--endpoint', dest='endpoint', default='https://fts3-pilot.cern.ch:8446')

(options, args) = opts.parse_args()

logging.getLogger('fts3.rest.client').setLevel(logging.DEBUG)

context = fts3.Context(options.endpoint)
whoami = fts3.whoami(context)
print json.dumps(whoami, indent=2)

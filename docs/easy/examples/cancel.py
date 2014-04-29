#!/usr/bin/env python
#
# How to cancel a job
#
import json
import logging
import fts3.rest.client.easy as fts3
from optparse import OptionParser


opts = OptionParser()
opts.add_option('-s', '--endpoint', dest='endpoint', default='https://fts3-pilot.cern.ch:8446')

(options, args) = opts.parse_args()
if len(args) < 1:
    raise Exception('Need a job id')
job_id = args[0]

logging.getLogger('fts3.rest.client').setLevel(logging.DEBUG)

context = fts3.Context(options.endpoint)
final_status = fts3.cancel(context, job_id)
print json.dumps(final_status, indent=2)

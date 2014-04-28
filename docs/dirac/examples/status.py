#!/usr/bin/env python
#
# How to get the state of a given job
#
import json
import logging
import fts3.rest.client.dirac_bindings as fts3
from optparse import OptionParser


opts = OptionParser()
opts.add_option('-s', '--endpoint', dest='endpoint', default='https://fts3-pilot.cern.ch:8446')
opts.add_option('-l', '--list', dest='list_files', default=False, action='store_true')

(options, args) = opts.parse_args()
if len(args) < 1:
    raise Exception('Need a job id')
job_id = args[0]

logging.getLogger('fts3.rest.client').setLevel(logging.DEBUG)

context = fts3.Context(options.endpoint)
job_status = fts3.get_job_status(context, job_id, list_files=options.list_files)
print json.dumps(job_status, indent=2)

#!/usr/bin/env python
#
# How to submit a transfer
#
import json
import logging
import fts3.rest.client.dirac_bindings as fts3
from optparse import OptionParser


opts = OptionParser()
opts.add_option('-s', '--endpoint', dest='endpoint', default='https://fts3-pilot.cern.ch:8446')
opts.add_option('--dry-run', dest='dry_run', default=False, action='store_true')

(options, args) = opts.parse_args()
if len(args) < 2:
    raise Exception('Need a source and a destination')

source = args[0]
destination = args[1]
checksum = None

if len(args) > 2:
    checksum = args[2]

logging.getLogger('fts3.rest.client').setLevel(logging.DEBUG)

# Build the job
transfer = fts3.new_transfer(source, destination,
                             checksum=checksum, filesize=None,
                             metadata='Test submission')
job = fts3.new_job([transfer], verify_checksum=True, metadata='Test job', retry=1)

# Submit or just print
if options.dry_run:
    print json.dumps(job, indent=2)
else:
    context = fts3.Context(options.endpoint)
    print fts3.submit(context, job)

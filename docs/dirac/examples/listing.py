#!/usr/bin/env python
#
# How to get the list of transfers
#
import json
import logging
import fts3.rest.client.dirac_bindings as fts3
from optparse import OptionParser


opts = OptionParser()
opts.add_option('-s', '--endpoint', dest='endpoint', default='https://fts3-pilot.cern.ch:8446')
opts.add_option('--vo', dest='vo', default=None)
opts.add_option('--dn', dest='dn', default=None)
(options, args) = opts.parse_args()

logging.getLogger('fts3.rest.client').setLevel(logging.DEBUG)

context = fts3.Context(options.endpoint)

# Query and print
# user_dn and vo can be set in order to filter the return values
# (i.e. fts3.list_jobs(context, vo = 'lhcb'), but can be omitted
jobs = fts3.list_jobs(context, user_dn=options.dn, vo=options.vo)
print json.dumps(jobs, indent=2)

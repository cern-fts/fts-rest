#!/usr/bin/env python
#
# How to get the list of transfers
#

#   Copyright notice:
#   Copyright © Members of the EMI Collaboration, 2010.
# 
#   See www.eu-emi.eu for details on the copyright holders
# 
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
# 
#       http://www.apache.org/licenses/LICENSE-2.0
# 
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import json
import logging
import fts3.rest.client.easy as fts3
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

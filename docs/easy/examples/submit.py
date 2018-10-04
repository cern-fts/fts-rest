#!/usr/bin/env python
#
# How to submit a transfer
#

#   Copyright notice:
#   Copyright  Members of the EMI Collaboration, 2013.
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
job = fts3.new_job([transfer], verify_checksum=True, metadata='Test job', retry=1, priority =3)

# Submit or just print
if options.dry_run:
    print json.dumps(job, indent=2)
else:
    context = fts3.Context(options.endpoint)
    print fts3.submit(context, job)

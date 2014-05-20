#   Copyright notice:
#   Copyright  CERN, 2014.
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
import sys

from base import Base
from fts3.rest.client import Context, Inquirer


def _human_readable_snapshot(logger, snapshot):
    for entry in snapshot:
        logger.info("Source:              %s" % entry.get('source_se'))
        logger.info("Destination:         %s" % entry.get('dest_se'))
        logger.info("VO:                  %s" % entry.get('vo_name'))
        logger.info("Max. Active:         %d" % entry.get('max_active', 0))
        logger.info("Active:              %d" % entry.get('active', 0))
        logger.info("Submitted:           %d" % entry.get('submitted', 0))
        logger.info("Finished:            %d" % entry.get('finished', 0))
        logger.info("Failed:              %d" % entry.get('failed', 0))
        ratio = entry.get('success_ratio', None)
        if ratio:
            logger.info("Success ratio:       %.2f%%" % ratio)
        else:
            logger.info("Success ratio:       -")
        avg_thr = entry.get('avg_throughput', None)
        if avg_thr is not None:
            logger.info("Avg. Throughput:     %.2f MB/s" % avg_thr)
        else:
            logger.info("Avg. Throughput:     -")
        avg_duration = entry.get('avg_duration', None)
        if avg_duration is not None:
            logger.info("Avg. Duration:       %d seconds" % avg_duration)
        else:
            logger.info("Avg. Duration:       -")
        avg_queued = entry.get('avg_queued')
        if avg_queued is not None:
            logger.info("Avg. Queued:         %d seconds" % avg_queued)
        else:
            logger.info("Avg. Queued:         -")
        frequent_error = entry.get('frequent_error', None)
        if frequent_error and 'count' in frequent_error and 'reason' in frequent_error:
            logger.info("Most frequent error: [%d] %s" % (frequent_error['count'], frequent_error['reason']))
        else:
            logger.info("Most frequent error: -")
        limits = entry.get('limits', None)
        if isinstance(limits, dict):
            if limits.get('source', None):
                logger.info("Max. Source Thr:     %.2f" % limits['source'])
            if limits.get('destination', None):
                logger.info("Max. Dest. Thr:      %.2f" % limits['destination'])
        logger.info("\n")


class Snapshot(Base):
    def __init__(self, argv=sys.argv[1:]):
        super(Snapshot, self).__init__()
        # Specific options
        self.opt_parser.add_option('--vo', dest='vo',
                                   help='filter by VO')
        self.opt_parser.add_option('--source', dest='source',
                                   help='filter by source SE')
        self.opt_parser.add_option('--destination', dest='destination',
                                   help='filter by destination SE')
        (self.options, self.args) = self.opt_parser.parse_args(argv)

        if self.options.endpoint is None:
            self.logger.critical('Need an endpoint')
            sys.exit(1)

        if self.options.verbose:
            self.logger.setLevel(logging.DEBUG)

    def __call__(self):
        context = Context(self.options.endpoint, ukey=self.options.ukey, ucert=self.options.ucert)
        inquirer = Inquirer(context)
        snapshot = inquirer.get_snapshot(self.options.vo, self.options.source, self.options.destination)
        if self.options.json:
            self.logger.info(json.dumps(snapshot, indent=2))
        else:
            _human_readable_snapshot(self.logger, snapshot)

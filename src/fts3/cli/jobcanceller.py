import logging
import sys

from base import Base
from fts3.rest.client import Submitter, Context


class JobCanceller(Base):

    def __init__(self, argv=sys.argv[1:]):
        super(JobCanceller, self).__init__()

        (self.options, self.args) = self.opt_parser.parse_args(argv)

        if self.options.endpoint is None:
            self.logger.critical('Need an endpoint')
            sys.exit(1)

        if len(self.args) == 0:
            self.logger.critical('Need a job id')
            sys.exit(1)

        self.job_id = self.args[0]

        if self.options.verbose:
            self.logger.setLevel(logging.DEBUG)

    def __call__(self):
        context = Context(self.options.endpoint, ukey=self.options.ukey, ucert=self.options.ucert)
        submitter = Submitter(context)
        job = submitter.cancel(self.job_id)
        self.logger.info(job['job_state'])

import logging
import sys

from fts3.rest.client import Inquirer, Context
from base import Base
from utils import *


class JobShower(Base):

    def __init__(self, argv=sys.argv[1:]):
        super(JobShower, self).__init__(extra_args='JOB_ID')

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

        inquirer = Inquirer(context)
        job      = inquirer.get_job_status(self.job_id, list_files=self.options.json)

        if not self.options.json:
            self.logger.info(job_human_readable(job))
        else:
            self.logger.info(job_as_json(job))

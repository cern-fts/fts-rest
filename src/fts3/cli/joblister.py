import logging
import sys

from fts3.rest.client import Inquirer, Context
from base import Base
from utils import *


class JobLister(Base):

    def __init__(self, argv=sys.argv[1:]):
        super(JobLister, self).__init__()
        # Specific options
        self.opt_parser.add_option('-u', '--userdn', dest='user_dn',
                                   help='query only for the given user.')
        self.opt_parser.add_option('-o', '--voname', dest='vo_name',
                                   help='query only for the given VO.')

        # And parse
        (self.options, self.args) = self.opt_parser.parse_args(argv)

        if self.options.endpoint is None:
            self.logger.critical('Need an endpoint')
            sys.exit(1)

        if self.options.verbose:
            self.logger.setLevel(logging.DEBUG)

    def __call__(self):
        context = Context(self.options.endpoint, ukey=self.options.ukey, ucert=self.options.ucert)
        inquirer = Inquirer(context)
        job_list  = inquirer.get_job_list(self.options.user_dn, self.options.vo_name)
        if not self.options.json:
            self.logger.info(job_list_human_readable(job_list))
        else:
            self.logger.info(job_list_as_json(job_list))

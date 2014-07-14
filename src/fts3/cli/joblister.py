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

import logging
import sys

from fts3.rest.client import Inquirer
from base import Base
from utils import *


class JobLister(Base):

    def __init__(self, argv=sys.argv[1:]):
        super(JobLister, self).__init__()
        # Specific options
        self.opt_parser.add_option('-u', '--userdn', dest='user_dn',
                                   help='query only for the given user')
        self.opt_parser.add_option('-o', '--voname', dest='vo_name',
                                   help='query only for the given VO')
        self.opt_parser.add_option('--source', dest='source_se',
                                   help='query only for the given source storage element')
        self.opt_parser.add_option('--destination', dest='dest_se',
                                   help='query only for the given destination storage element')

        # And parse
        (self.options, self.args) = self.opt_parser.parse_args(argv)

        if self.options.endpoint is None:
            self.logger.critical('Need an endpoint')
            sys.exit(1)

        if self.options.verbose:
            self.logger.setLevel(logging.DEBUG)

    def __call__(self):
        context = self._create_context() 
        inquirer = Inquirer(context)
        job_list  = inquirer.get_job_list(
            self.options.user_dn, self.options.vo_name, self.options.source_se, self.options.dest_se
        )
        if not self.options.json:
            self.logger.info(job_list_human_readable(job_list))
        else:
            self.logger.info(job_list_as_json(job_list))

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

from fts3.rest.client import Inquirer
from base import Base
from utils import *


class JobLister(Base):

    def __init__(self):
        super(JobLister, self).__init__(
            description="This command can be used to list the running jobs, allowing to filter by user dn or vo name",
            example="""
            $ %(prog)s -s https://fts3-devel.cern.ch:8446 -o atlas
            Request ID: ff294db7-655a-4c0a-9efb-44a994677bb3
            Status: ACTIVE
            Client DN: /DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=ddmadmin/CN=531497/CN=Robot: ATLAS Data Management
            Reason: None
            Submission time: 2014-04-15T07:05:38
            Priority: 3
            VO Name: atlas

            Request ID: a2e4586c-760a-469e-8303-d0f3d5aadc73
            Status: READY
            Client DN: /DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=ddmadmin/CN=531497/CN=Robot: ATLAS Data Management
            Reason: None
            Submission time: 2014-04-15T07:07:33
            Priority: 3
            VO Name: atlas
            """
        )
        # Specific options
        self.opt_parser.add_option('-u', '--userdn', dest='user_dn',
                                   help='query only for the given user')
        self.opt_parser.add_option('-o', '--voname', dest='vo_name',
                                   help='query only for the given VO')
        self.opt_parser.add_option('--source', dest='source_se',
                                   help='query only for the given source storage element')
        self.opt_parser.add_option('--destination', dest='dest_se',
                                   help='query only for the given destination storage element')

    def run(self):
        context = self._create_context()
        inquirer = Inquirer(context)
        job_list = inquirer.get_job_list(
            self.options.user_dn, self.options.vo_name, self.options.source_se, self.options.dest_se
        )
        if not self.options.json:
            self.logger.info(job_list_human_readable(job_list))
        else:
            self.logger.info(job_list_as_json(job_list))

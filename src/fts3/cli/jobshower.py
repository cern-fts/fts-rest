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

import sys

from fts3.rest.client import Inquirer
from base import Base
from utils import *


class JobShower(Base):

    def __init__(self):
        super(JobShower, self).__init__(
            extra_args='JOB_ID',
            description="This command can be used to check the current status of a given job",
            example="""
            $ %(prog)s -s https://fts3-devel.cern.ch:8446 c079a636-c363-11e3-b7e5-02163e009f5a
            Request ID: c079a636-c363-11e3-b7e5-02163e009f5a
            Status: FINISHED
            Client DN: /DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=saketag/CN=678984/CN=Alejandro Alvarez Ayllon
            Reason:
            Submission time: 2014-04-13T23:31:34
            Priority: 3
            VO Name: dteam
            """
        )

    def validate(self):
        if len(self.args) == 0:
            self.logger.critical('Need a job id')
            sys.exit(1)

    def run(self):
        job_id = self.args[0]
        context = self._create_context()

        inquirer = Inquirer(context)
        job      = inquirer.get_job_status(job_id, list_files=self.options.json)

        if not self.options.json:
            self.logger.info(job_human_readable(job))
        else:
            self.logger.info(job_as_json(job))

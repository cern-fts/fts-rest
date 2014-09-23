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

from base import Base
from fts3.rest.client import Submitter


class JobCanceller(Base):

    def __init__(self):
        super(JobCanceller, self).__init__(
            description="""
            This command can be used to cancel a running job.  It returns the final state of the canceled job.
            Please, mind that if the job is already in a final state (FINISHEDDIRTY, FINISHED, FAILED),
            this command will return this state.
            """,
            example="""
            $ %(prog)s -s https://fts3-devel.cern.ch:8446 c079a636-c363-11e3-b7e5-02163e009f5a
            FINISHED
            """
        )

    def run(self):
        job_id = self.args[0]
        context = self._create_context()
        submitter = Submitter(context)
        job = submitter.cancel(job_id)
        self.logger.info(job['job_state'])

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
            You can additionally cancel only a subset appending a comma-separated list of file ids
            """,
            example="""
            $ %(prog)s -s https://fts3-devel.cern.ch:8446 c079a636-c363-11e3-b7e5-02163e009f5a
            FINISHED
            $ %(prog)s -s https://fts3-devel.cern.ch:8446 c079a636-c363-11e3-b7e5-02163e009f5a:5658,5659,5670
            CANCELED, CANCELED, CANCELED
            """
        )

    def run(self):
        if ':' in self.args[0]:
            job_id, file_ids = self.args[0].split(':')
            file_ids = file_ids.split(',')
        else:
            job_id = self.args[0]
            file_ids = None

        context = self._create_context()
        submitter = Submitter(context)
        result = submitter.cancel(job_id, file_ids)
        if file_ids:
            if isinstance(result, basestring):
                self.logger.info(result)
            else:
                self.logger.info('\n'.join(result))
        else:
            self.logger.info(result['job_state'])

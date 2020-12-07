#   Copyright notice:
#   Copyright CERN, 2014.
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

from datetime import timedelta
try:
    import simplejson as json
except:
    import json 
import logging
import sys
import time

from base import Base
from fts3.rest.client import Submitter, Delegator, Inquirer


def _metadata(data):
    try:
        return json.loads(data)
    except:
        return str(data)


class JobDeletionSubmitter(Base):
    def __init__(self):
        super(JobDeletionSubmitter, self).__init__(
            extra_args='SURL1 [SURL2] [SURL3] [...]',
            description="""
            This command can be used to submit a deletion job to FTS3. It supports simple and bulk submissions.
            """,
            example="""
            $ %(prog)s -s https://fts3-devel.cern.ch:8446 gsiftp://source.host/file1 gsiftp://source.host/file2
            Job successfully submitted.
            Job id: 9fee8c1e-c46d-11e3-8299-02163e00a17a

            $ %(prog)s -s https://fts3-devel.cern.ch:8446 -f bulk.list
            Job successfully submitted.
            Job id: 9fee8c1e-c46d-11e3-8299-02163e00a17a
            """
        )

        # Specific options
        self.opt_parser.add_option('-b', '--blocking', dest='blocking', default=False, action='store_true',
                                   help='blocking mode. Wait until the operation completes.')
        self.opt_parser.add_option('-i', '--interval', dest='poll_interval', type='int', default=30,
                                   help='interval between two poll operations in blocking mode.')
        self.opt_parser.add_option('-e', '--expire', dest='proxy_lifetime', type='int', default=420,
                                   help='expiration time of the delegation in minutes.')
        self.opt_parser.add_option('--job-metadata', dest='job_metadata',
                                   help='transfer job metadata.')
        self.opt_parser.add_option('--file-metadata', dest='file_metadata',
                                   help='file metadata.')
        self.opt_parser.add_option('-S', '--spacetoken', dest='spacetoken',
                                   help='the space token or its description.')
        self.opt_parser.add_option('--dry-run', dest='dry_run', default=False, action='store_true',
                                   help='do not send anything, just print the JSON message.')
        self.opt_parser.add_option('-f', '--file', dest='bulk_file', type='string',
                                   help='Name of configuration file')
        self.opt_parser.add_option('--retry', dest='retry', type='int', default=0,
                                   help='Number of retries. If 0, the server default will be used.'
                                        'If negative, there will be no retries.')
        self.opt_parser.add_option('--cloud-credentials', dest='cloud_cred', default=None,
                                   help='use cloud credentials for the job (i.e. dropbox).')

    def validate(self):
        if not self.options.bulk_file:
            if len(self.args) < 1:
                self.logger.critical("Need at least a surl")
                sys.exit(1)

        if self.options.verbose:
            self.logger.setLevel(logging.DEBUG)

    def _build_delete(self):
        if self.options.bulk_file:
            files = filter(len, open(self.options.bulk_file).readlines())
            if len(files):
                return files
            else:
                self.logger.critical("Could not find any file to delete")
                sys.exit(1)
        else:
            return self.args

    def _do_submit(self, context):

        delegator = Delegator(context)
        delegator.delegate(timedelta(minutes=self.options.proxy_lifetime))

        submitter = Submitter(context)

        job_id = submitter.submit(
            delete=self._build_delete(),
            spacetoken=self.options.spacetoken,
            job_metadata=_metadata(self.options.job_metadata),
            retry=self.options.retry,
            credential=self.options.cloud_cred
        )

        if self.options.json:
            self.logger.info(json.dumps(job_id))
        else:
            self.logger.info("Job successfully submitted.")
            self.logger.info("Job id: %s" % job_id)

        if job_id and self.options.blocking:
            inquirer = Inquirer(context)
            job = inquirer.get_job_status(job_id)
            while job['job_state'] in ['SUBMITTED', 'READY', 'STAGING', 'ACTIVE', 'DELETE', 'ARCHIVING', 'QOS_TRANSITION', 'QOS_REQUEST_SUBMITTED']:
                self.logger.info("Job in state %s" % job['job_state'])
                time.sleep(self.options.poll_interval)
                job = inquirer.get_job_status(job_id)

            self.logger.info("Job finished with state %s" % job['job_state'])
            if job['reason']:
                self.logger.info("Reason: %s" % job['reason'])

        return job_id

    def _do_dry_run(self, context):

        submitter = Submitter(context)
        print submitter.build_submission(
            delete=self._build_delete(),
            spacetoken=self.options.spacetoken,
            job_metadata=_metadata(self.options.job_metadata),
            retry=self.options.retry,
            credential=self.options.cloud_cred
        )
        return None

    def run(self):
        context = self._create_context()
        if not self.options.dry_run:
            return self._do_submit(context)
        else:
            return self._do_dry_run(context)

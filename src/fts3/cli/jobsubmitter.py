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

from datetime import timedelta
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


class JobSubmitter(Base):
    def __init__(self):
        super(JobSubmitter, self).__init__(extra_args='SOURCE DESTINATION [CHECKSUM]')

        # Specific options
        self.opt_parser.add_option('-b', '--blocking', dest='blocking', default=False, action='store_true',
                                   help='blocking mode. Wait until the operation completes.')
        self.opt_parser.add_option('-i', '--interval', dest='poll_interval', type='int', default=30,
                                   help='interval between two poll operations in blocking mode.')
        self.opt_parser.add_option('-e', '--expire', dest='proxy_lifetime', type='int', default=420,
                                   help='expiration time of the delegation in minutes.')
        self.opt_parser.add_option('-o', '--overwrite', dest='overwrite', default=False, action='store_true',
                                   help='overwrite files.')
        self.opt_parser.add_option('-r', '--reuse', dest='reuse', default=False, action='store_true',
                                   help='enable session reuse for the transfer job.')
        self.opt_parser.add_option('--job-metadata', dest='job_metadata',
                                   help='transfer job metadata.')
        self.opt_parser.add_option('--file-metadata', dest='file_metadata',
                                   help='file metadata.')
        self.opt_parser.add_option('--file-size', dest='file_size', type='long',
                                   help='file size (in Bytes)')
        self.opt_parser.add_option('-g', '--gparam', dest='gridftp_params',
                                   help='GridFTP parameters.')
        self.opt_parser.add_option('-t', '--dest-token', dest='destination_token',
                                   help='the destination space token or its description.')
        self.opt_parser.add_option('-S', '--source-token', dest='source_token',
                                   help='the source space token or its description.')
        self.opt_parser.add_option('-K', '--compare-checksum', dest='compare_checksum',
                                   help='compare checksums between source and destination.')
        self.opt_parser.add_option('--copy-pin-lifetime', dest='pin_lifetime', type='long', default=-1,
                                   help='pin lifetime of the copy in seconds.')
        self.opt_parser.add_option('--bring-online', dest='bring_online', type='long', default=None,
                                   help='bring online timeout in seconds.')
        self.opt_parser.add_option('--fail-nearline', dest='fail_nearline', default=False, action='store_true',
                                   help='fail the transfer is the file is nearline.')
        self.opt_parser.add_option('--dry-run', dest='dry_run', default=False, action='store_true',
                                   help='do not send anything, just print the JSON message.')
        self.opt_parser.add_option('-f', '--file', dest='bulk_file', type='string',
                                   help='Name of configuration file')
        self.opt_parser.add_option('--retry', dest='retry', type='int', default=0,
                                   help='Number of retries. If 0, the server default will be used.'
                                        'If negative, there will be no retries.')
        self.opt_parser.add_option('-m', '--multi-hop', dest='multihop', default=False, action='store_true',
                                   help='submit a multihop transfer.')

    def validate(self):
        if not self.options.bulk_file:
            if len(self.args) < 2:
                self.logger.critical("Need a source and a destination")
                sys.exit(1)
            elif len(self.args) == 2:
                (self.source, self.destination) = self.args
                self.checksum = None
            elif len(self.args) == 3:
                (self.source, self.destination, self.checksum) = self.args
            else:
                self.logger.critical("Too many parameters")
                sys.exit(1)
        else:
            self.checksum = None

        if self.options.verbose:
            self.logger.setLevel(logging.DEBUG)

    def _build_transfers(self):
        if self.options.bulk_file:
            filecontent = open(self.options.bulk_file).read()
            bulk = json.loads(filecontent)
            if "files" in bulk:
                return bulk["files"]
            elif "Files" in bulk:
                return bulk["Files"]
            else:
                self.logger.critical("Could not find any transfers")
                sys.exit(1)
        else:
            return [{"sources": [self.source], "destinations": [self.destination]}]

    def _do_submit(self, context):
        verify_checksum = None
        if self.options.compare_checksum:
            verify_checksum = True

        delegator = Delegator(context)
        delegator.delegate(timedelta(minutes=self.options.proxy_lifetime))

        submitter = Submitter(context)

        job_id = submitter.submit(
            self._build_transfers(),
            checksum=self.checksum,
            bring_online=self.options.bring_online,
            verify_checksum=verify_checksum,
            spacetoken=self.options.destination_token,
            source_spacetoken=self.options.source_token,
            fail_nearline=self.options.fail_nearline,
            file_metadata=_metadata(self.options.file_metadata),
            filesize=self.options.file_size,
            gridftp=self.options.gridftp_params,
            job_metadata=_metadata(self.options.job_metadata),
            overwrite=self.options.overwrite,
            copy_pin_lifetime=self.options.pin_lifetime,
            reuse=self.options.reuse,
            retry=self.options.retry,
            multihop=self.options.multihop
        )

        if self.options.json:
            self.logger.info(json.dumps(job_id))
        else:
            self.logger.info("Job successfully submitted.")
            self.logger.info("Job id: %s" % job_id)

        if job_id and self.options.blocking:
            inquirer = Inquirer(context)
            job = inquirer.get_job_status(job_id)
            while job['job_state'] in ['SUBMITTED', 'READY', 'STAGING', 'ACTIVE']:
                self.logger.info("Job in state %s" % job['job_state'])
                time.sleep(self.options.poll_interval)
                job = inquirer.get_job_status(job_id)

            self.logger.info("Job finished with state %s" % job['job_state'])
            if job['reason']:
                self.logger.info("Reason: %s" % job['reason'])

        return job_id

    def _do_dry_run(self, context):
        verify_checksum = None
        if self.options.compare_checksum:
            verify_checksum = True

        submitter = Submitter(context)
        print submitter.build_submission(
            self._build_transfers(),
            checksum=self.checksum,
            bring_online=self.options.bring_online,
            verify_checksum=verify_checksum,
            spacetoken=self.options.destination_token,
            source_spacetoken=self.options.source_token,
            fail_nearline=self.options.fail_nearline,
            file_metadata=_metadata(self.options.file_metadata),
            filesize=self.options.file_size,
            gridftp=self.options.gridftp_params,
            job_metadata=_metadata(self.options.job_metadata),
            overwrite=self.options.overwrite,
            copy_pin_lifetime=self.options.pin_lifetime,
            reuse=self.options.reuse,
            retry=self.options.retry,
            multihop=self.options.multihop
        )
        return None

    def run(self):
        context = self._create_context()
        if not self.options.dry_run:
            return self._do_submit(context)
        else:
            return self._do_dry_run(context)

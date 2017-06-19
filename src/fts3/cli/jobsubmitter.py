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
try:
    import simplejson as json
except:
    import json
import logging
import sys
import time

from base import Base
from fts3.rest.client import Submitter, Delegator, Inquirer

DEFAULT_CHECKSUM = 'ADLER32' 

def _metadata(data):
    try:
        return json.loads(data)
    except:
        return str(data)


class JobSubmitter(Base):
    def __init__(self):
        super(JobSubmitter, self).__init__(
            extra_args='SOURCE DESTINATION [CHECKSUM]',
            description="""
            This command can be used to submit new jobs to FTS3. It supports simple and bulk submissions. The bulk
            format is as follows:

            ```json
            {
              "files": [
                {
                  "sources": [
                    "gsiftp://source.host/file"
                  ],
                  "destinations": [
                    "gsiftp://destination.host/file"
                  ],
                  "metadata": "file-metadata",
                  "checksum": "ADLER32:1234",
                  "filesize": 1024
                },
                {
                  "sources": [
                    "gsiftp://source.host/file2"
                  ],
                  "destinations": [
                    "gsiftp://destination.host/file2"
                  ],
                  "metadata": "file2-metadata",
                  "checksum": "ADLER32:4321",
                  "filesize": 2048,
                  "activity": "default"
                }
              ]
            }
            ```
            """,
            example="""
            $ %(prog)s -s https://fts3-devel.cern.ch:8446 gsiftp://source.host/file gsiftp://destination.host/file
            Job successfully submitted.
            Job id: 9fee8c1e-c46d-11e3-8299-02163e00a17a

            $ %(prog)s -s https://fts3-devel.cern.ch:8446 -f bulk.json
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
        self.opt_parser.add_option('--delegate-when-lifetime-lt', type=int, default=120,
                                   help='delegate the proxy when the remote lifetime is less than this value (in minutes)')
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
        self.opt_parser.add_option('-K', '--compare-checksum', dest='compare_checksum', default=False, action='store_true',
                                   help='deprecated: compare checksums between source and destination.')
        self.opt_parser.add_option('-C', '--checksum-mode', dest='checksum_mode', type='string', default='none',
                                   help='compare checksums in source, target, both or none.')
        self.opt_parser.add_option('--copy-pin-lifetime', dest='pin_lifetime', type='long', default=-1,
                                   help='pin lifetime of the copy in seconds.')
        self.opt_parser.add_option('--bring-online', dest='bring_online', type='long', default=None,
                                   help='bring online timeout in seconds.')
        self.opt_parser.add_option('--timeout', dest='timeout', type='long', default=None,
                                   help='transfer timeout in seconds.')
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
        self.opt_parser.add_option('--cloud-credentials', dest='cloud_cred', default=None,
                                   help='use cloud credentials for the job (i.e. dropbox).')
        self.opt_parser.add_option('--nostreams', dest='nostreams', default=None,
                                   help='number of streams')
        self.opt_parser.add_option('--ipv4', dest='ipv4', default=False, action='store_true',
                                   help='force ipv4')
        self.opt_parser.add_option('--ipv6', dest='ipv6', default=False, action='store_true',
                                   help='force ipv6')

    def validate(self):
        self.checksum = None
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

        if self.options.ipv4 and self.options.ipv6:
            self.opt_parser.error('ipv4 and ipv6 can not be used at the same time')

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
        #Backwards compatibility: compare_checksum parameter 
        if self.options.compare_checksum:
            checksum_mode = 'both' 
        else:
            if self.checksum:
                checksum_mode = 'target'
            else: 
                checksum = 'none'  
        #Compare checksum has major priority than checksum_mode     
        if not self.options.compare_checksum:   
            if len(self.options.checksum_mode) > 0:
                checksum_mode = self.options.checksum_mode   
            else:
                 checksum_mode = 'none'        
        
        if not self.checksum:
            self.checksum = DEFAULT_CHECKSUM
            
        delegator = Delegator(context)
        delegator.delegate(
            timedelta(minutes=self.options.proxy_lifetime),
            delegate_when_lifetime_lt=timedelta(minutes=self.options.delegate_when_lifetime_lt)
        )

        submitter = Submitter(context)

        job_id = submitter.submit(
            self._build_transfers(),
            checksum=self.checksum,
            bring_online=self.options.bring_online,
            timeout = self.options.timeout,
            verify_checksum=checksum_mode[0],
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
            multihop=self.options.multihop,
            credential=self.options.cloud_cred,
            nostreams=self.options.nostreams,
            ipv4=self.options.ipv4,
            ipv6=self.options.ipv6
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
        #Backwards compatibility: compare_checksum parameter 
        if self.options.compare_checksum:
            checksum_mode = 'both' 
        else:
            if self.checksum:
                checksum_mode = 'target'
            else: 
                checksum = 'none'  
        #Compare checksum has major priority than checksum_mode     
        if not self.options.compare_checksum:   
            if len(self.options.checksum_mode) > 0:
                checksum_mode = self.options.checksum_mode   
            else:
                 checksum_mode = 'none'        
        
        if not self.checksum:
            self.checksum = DEFAULT_CHECKSUM
                
        submitter = Submitter(context)
        print submitter.build_submission(
            self._build_transfers(),
            checksum=self.checksum,
            bring_online=self.options.bring_online,
            timeout = self.options.timeout,
            verify_checksum=checksum_mode,
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
            multihop=self.options.multihop,
            credential=self.options.cloud_cred,
            nostreams=self.options.nostreams,
            ipv4=self.options.ipv4,
            ipv6=self.options.ipv6
        )
        return None

    def run(self):
        context = self._create_context()
        if not self.options.dry_run:
            return self._do_submit(context)
        else:
            return self._do_dry_run(context)

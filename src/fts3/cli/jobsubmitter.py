from base import Base
from datetime import timedelta
from fts3.rest.client import Submitter, Delegator, Inquirer, Context
import logging
import sys
import time



class JobSubmitter(Base):
	
	def __init__(self, argv = sys.argv[1:]):
		super(JobSubmitter, self).__init__(extra_args = 'SOURCE DESTINATION [CHECKSUM]')
		
		# Specific options
		self.optParser.add_option('-b', '--blocking', dest = 'blocking', default = False, action = 'store_true',
								  help = 'blocking mode. Wait until the operation completes.')
		self.optParser.add_option('-i', '--interval', dest = 'poll_interval', type = 'int', default = 30,
								  help = 'interval between two poll operations in blocking mode.')
		self.optParser.add_option('-e', '--expire', dest = 'proxy_lifetime', type = 'int', default = 420,
								  help = 'expiration time of the delegation in minutes.')
		self.optParser.add_option('-o', '--overwrite', dest = 'overwrite', default = False, action = 'store_true',
								  help = 'overwrite files.')
		self.optParser.add_option('-r', '--reuse', dest = 'reuse', default = False, action = 'store_true',
								  help = 'enable session reuse for the transfer job.')
		self.optParser.add_option('--job-metadata', dest = 'job_metadata',
								  help = 'transfer job metadata.')
		self.optParser.add_option('--file-metadata', dest = 'file_metadata',
								  help = 'file metadata.')
		self.optParser.add_option('--file-size', dest = 'file_size', type = 'long',
								  help = 'file size (in Bytes)')
		self.optParser.add_option('-g', '--gparam', dest = 'gridftp_params',
								  help = 'GridFTP parameters.')
		self.optParser.add_option('-t', '--dest-token', dest = 'destination_token',
								  help = 'the destination space token or its description.')
		self.optParser.add_option('-S', '--source-token', dest = 'source_token',
								  help = 'the source space token or its description.')
		self.optParser.add_option('-K', '--compare-checksum', dest = 'compare_checksum',
								  help = 'compare checksums between source and destination.')
		self.optParser.add_option('--copy-pin-lifetime', dest = 'pin_lifetime', type = 'long', default = -1,
								  help = 'pin lifetime of the copy in seconds.')
		self.optParser.add_option('--bring-online',  dest = 'bring_online', type = 'long', default = None,
								  help = 'bring online timeout in seconds.')
		self.optParser.add_option('--fail-nearline', dest = 'fail_nearline', default = False, action = 'store_true',
								  help = 'fail the transfer is the file is nearline.')
		self.optParser.add_option('--dry-run', dest = 'dry_run', default = False, action = 'store_true',
								  help = 'do not send anything, just print the JSON message.')
		
		(self.options, self.args) = self.optParser.parse_args(argv)
		
		if self.options.endpoint is None:
			self.logger.critical('Need an endpoint')
			sys.exit(1)
			
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
				
		if self.options.verbose:
			self.logger.setLevel(logging.DEBUG)


	def _doSubmit(self):	
		checksum_method = None
		if self.options.compare_checksum:
			self.options.compare_checksum = 'compare'
		
		delegator = Delegator(self.context)
		delegationId = delegator.delegate(timedelta(minutes = self.options.proxy_lifetime))
		
		submitter = Submitter(self.context)	
		jobId = submitter.submit(self.source, self.destination,
								 checksum          = self.checksum,
								 bring_online      = self.options.bring_online,
								 checksum_method   = checksum_method,
								 spacetoken        = self.options.destination_token,
								 source_spacetoken = self.options.source_token,
								 fail_nearline     = self.options.fail_nearline,
								 file_metadata     = self.options.file_metadata,
								 filesize          = self.options.file_size,
								 gridftp           = self.options.gridftp_params,
								 job_metadata      = self.options.job_metadata,
								 overwrite         = self.options.overwrite,
								 copy_pin_lifetime = self.options.pin_lifetime,
								 reuse             = self.options.reuse
							 	)
		
		if self.options.json:
			self.logger.info(jobId)
		else:
			self.logger.info("Job successfully submitted.")
			self.logger.info("Job id: %s" % jobId)
	
		if jobId and self.options.blocking:
			inquirer = Inquirer(self.context)
			while True:
				time.sleep(self.options.poll_interval)
				job = inquirer.getJobStatus(jobId)
				if job['job_state'] not in ['SUBMITTED', 'READY', 'STAGING', 'ACTIVE']:
					break
				self.logger.info("Job in state %s" % job['job_state'])
			
			self.logger.info("Job finished with state %s" % job['job_state'])
			if job['reason']:
				self.logger.info("Reason: %s" % job['reason'])
				
		return jobId


	def _doDryRun(self):
		checksum_method = None
		if self.options.compare_checksum:
			self.options.compare_checksum = 'compare'
			
		submitter = Submitter(self.context)
		print submitter.buildSubmission(self.source, self.destination,
								 checksum          = self.checksum,
								 bring_online      = self.options.bring_online,
								 checksum_method   = checksum_method,
								 spacetoken        = self.options.destination_token,
								 source_spacetoken = self.options.source_token,
								 fail_nearline     = self.options.fail_nearline,
								 file_metadata     = self.options.file_metadata,
								 filesize          = self.options.file_size,
								 gridftp           = self.options.gridftp_params,
								 job_metadata      = self.options.job_metadata,
								 overwrite         = self.options.overwrite,
								 copy_pin_lifetime = self.options.pin_lifetime,
								 reuse             = self.options.reuse
							 	)
		return None


	def __call__(self):
		self.context = Context(self.options.endpoint)
		
		if not self.options.dry_run:
			return self._doSubmit()
		else:
			return self._doDryRun()


from datetime import datetime, timedelta
from fts3.orm import Job, File, JobActiveStates
from fts3.orm import Credential, BannedSE
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.middleware.fts3auth import authorize, authorized
from fts3rest.lib.middleware.fts3auth.constants import *
from pylons import request
from pylons.controllers.util import abort
import json
import re
import socket
import types
import uuid


DEFAULT_PARAMS = {
	'bring_online'     : -1,
	'checksum_method'  : '',
	'copy_pin_lifetime': -1,
	'fail_nearline'    : 'N',
	'gridftp'          : '',
	'job_metadata'     : None,
	'lan_connection'   : 'N',
	'overwrite'        : 'N',
	'reuse'            : '',
	'source_spacetoken': '',
	'spacetoken'       : ''
}


class JobsController(BaseController):
	
	def _getJob(self, id):
		job = Session.query(Job).get(id)
		if job is None:
			abort(404, 'No job with the id "%s" has been found' % id)
		if not authorized(TRANSFER, resource_owner = job.user_dn, resource_vo = job.vo_name):
			abort(403, 'Not enough permissions to check the job "%s"' % id)
		return job
		
	@authorize(TRANSFER)
	@jsonify
	def index(self, **kwargs):
		"""GET /jobs: All jobs in the collection"""
		jobs = Session.query(Job).filter(Job.job_state.in_(JobActiveStates))
		
		# Filtering
		if 'user_dn' in request.params:
			jobs = jobs.filter(Job.user_dn == request.params['user_dn'])
		if 'vo_name' in request.params:
			jobs = jobs.filter(Job.vo_name == request.params['vo_name'])
		
		# Return
		return jobs.all()
	
	@jsonify
	def cancel(self, id, **kwargs):
		"""DELETE /jobs/id: Delete an existing item"""
		job = self._getJob(id)
		
		if job.job_state in JobActiveStates:
			now = datetime.now()
			
			job.job_state    = 'CANCELED'
			job.finish_time  = now
			job.job_finished = now
			job.reason       = 'Job canceled by the user'
			
			for f in job.files:
				if f.file_state in JobActiveStates:
					f.file_state   = 'CANCELED'
					f.job_finished = now
					f.finish_time  = now
					f.reason       = 'Job canceled by the user'
				
			Session.merge(job)
			Session.commit()
			
			job = self._getJob(id)

		files = job.files
		return job
	
	@jsonify
	def show(self, id, **kwargs):
		"""GET /jobs/id: Show a specific item"""
		job = self._getJob(id)
		files = job.files # Trigger the query, so it is serialized
		return job
	
	@authorize(TRANSFER)
	@jsonify
	def submit(self, **kwargs):
		"""PUT /jobs: Submits a new job"""
		# First, the request has to be valid JSON
		try:
			submittedDict = json.loads(request.body)
		except ValueError, e:
			abort(400, 'Badly formatted JSON request')

		# The auto-generated delegation id must be valid
		user = request.environ['fts3.User.Credentials']
		credential = Session.query(Credential).get((user.delegation_id, user.user_dn))
		if credential is None:
			abort(403, 'No delegation id found for "%s"' % user.user_dn)
		if credential.expired():
			abort(403, 'The delegated credentials expired %d seconds ago' % credential.remaining().total_seconds())
		if credential.remaining() < timedelta(hours = 1):
			abort(403, 'The delegated credentials has less than one hour left')
		
		# Populate the job and file
		job = self._setupJobFromDict(submittedDict, user)
		
		# Banned?
		if self._isSeBanned(job.source_se):
			abort(403, 'Source storage element is banned')
		if self._isSeBanned(job.dest_se):
			abort(403, 'Destination storage element is banned')
		
		# Return it
		Session.merge(job)
		Session.commit()
		return job


	def _setupJobFromDict(self, json, user):
		try:
			if len(json['transfers']) == 0:
				abort(400, 'No transfers specified')
				
			# Get source and destination se, and validate
			source_se = self._getSE(json['transfers'][0]['source'])
			dest_se   = self._getSE(json['transfers'][0]['destination'])
			
			for t in json['transfers']:
				if self._getSE(t['source']) != source_se:
					abort(400, 'Not all source files belong to the same storage elements')
				if self._getSE(t['destination']) != dest_se:
					abort(400, 'Not all destination files belong to the same storage elements')
								
			# Initialize defaults
			# If the client is giving a NULL for a parameter with a default,
			# use the default
			params = dict()
			params.update(DEFAULT_PARAMS)
			if 'params' in json:
				params.update(json['params'])
				for (k, v) in params.iteritems():
					if v is None and k in DEFAULT_PARAMS:
						params[k] = DEFAULT_PARAMS[k]
			
			# Create
			job = Job()
			
			# Job
			job.job_id                   = str(uuid.uuid1())
			job.job_state                = 'SUBMITTED'
			job.reuse_job                = self._yesOrNo(params['reuse'])
			job.job_params               = params['gridftp']
			job.submit_host              = socket.getfqdn() 
			job.source_se                = source_se
			job.dest_se                  = dest_se
			job.user_dn                  = user.user_dn
			
			if 'credential' in json:
				job.user_cred  = json['credential']
				job.cred_id    = str()
			else:
				job.user_cred  = str()
				job.cred_id    = user.delegation_id
			
			job.voms_cred                = ' '.join(user.voms_cred)
			job.vo_name                  = user.vos[0]
			job.submit_time              = datetime.now()
			job.priority                 = 3
			job.space_token              = params['spacetoken']
			job.overwrite_flag           = self._yesOrNo(params['overwrite'])
			job.source_space_token       = params['source_spacetoken'] 
			job.copy_pin_lifetime        = int(params['copy_pin_lifetime'])
			job.lan_connection           = self._yesOrNo(params['lan_connection'])
			job.fail_nearline            = self._yesOrNo(params['fail_nearline'])
			job.checksum_method          = params['checksum_method']
			job.bring_online             = int(params['bring_online'])
			job.job_metadata             = params['job_metadata']
			job.job_params               = str()
			
			# Files
			for t in json['transfers']:
				file = File()
				
				file.file_state    = 'SUBMITTED'
				file.source_surl   = t['source']
				file.dest_surl     = t['destination']
				
				if 'checksum' in t and t['checksum']:
					file.checksum = t['checksum']
				else:
					file.checksum = str()
					
				if 'filesize' in t:
					file.user_filesize = t['filesize']
				if 'metadata' in t:
					file.file_metadata = t['metadata']
				
				job.files.append(file)
			
			return job
		
		except ValueError:
			abort(400, 'Invalid value within the request')
		except TypeError, e:
			abort(400, 'Malformed request: %s' % str(e))
		except KeyError, e:
			abort(400, 'Missing parameter: %s' % str(e))

			
	def _getSE(self, uri):
		match = re.match('.+://([a-zA-Z0-9\\.-]+)(:\\d+)?/.+', uri)
		if not match:
			raise ValueError('"%s" is an invalid SURL' % uri)
		return match.group(1)

	
	def _isSeBanned(self, se):
		banned = Session.query(BannedSE).get(se)
		return banned is not None
	
	
	def _yesOrNo(self, value):
		if type(value) is types.StringType:
			if len(value) == 0:
				return 'N'
			else:
				return value[0] 
		elif value:
			return 'Y'
		else:
			return 'N'

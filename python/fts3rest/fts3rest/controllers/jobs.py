from datetime import datetime
from fts3.orm import Job, File, JobActiveStates
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.middleware.fts3auth import authorize, authorized
from fts3rest.lib.middleware.fts3auth.constants import *
from pylons.controllers.util import abort


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
		jobs = Session.query(Job).filter(Job.job_state.in_(JobActiveStates)).all()
		return jobs 
	
	@jsonify
	def cancel(self, id):
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
	def show(self, id):
		"""GET /jobs/id: Show a specific item"""
		job = self._getJob(id)
		files = job.files # Trigger the query, so it is serialized
		return job

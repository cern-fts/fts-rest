from fts3.orm import Job, File, JobActiveStates
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from pylons.controllers.util import abort
from fts3rest.lib.middleware.fts3auth import authorize, authorized
from fts3rest.lib.middleware.fts3auth.constants import *


class JobsController(BaseController):

	@authorize(TRANSFER)
	@jsonify
	def index(self, **kwargs):
		"""GET /jobs: All jobs in the collection"""
		jobs = Session.query(Job).filter(Job.job_state.in_(JobActiveStates)).all()
		return jobs 

	def create(self):
		"""POST /jobs: Create a new job"""
        pass

	def new(self, format='html'):
		"""GET /jobs/new: Form to create a new item"""
		pass

	def update(self, id):
		"""PUT /jobs/id: Update an existing item"""
		abort(400, 'Jobs can not be modified')
	
	def delete(self, id):
		"""DELETE /jobs/id: Delete an existing item"""
		pass
	
	@jsonify
	def show(self, id):
		"""GET /jobs/id: Show a specific item"""
		job   = Session.query(Job).get(id)
		if job is None:
			abort(404, 'No job with the id "%s" has been found' % id)
			
		if not authorized(TRANSFER, resource_owner = job.user_dn, resource_vo = job.vo_name):
			abort(403, 'Not enough permissions to check the job "%s"' % id)
			
		files = job.files # Trigger the query, so it is serialized
		return job
	
	def edit(self, id, format='html'):
		"""GET /jobs/id/edit: Form to edit an existing item"""
		# url('edit_job', id=ID)
		pass

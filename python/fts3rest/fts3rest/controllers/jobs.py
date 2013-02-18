from fts3.orm import Job, File, JobActiveStates
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from pylons.controllers.util import abort



class JobsController(BaseController):

	@jsonify
	def index(self):
		"""GET /jobs: All jobs in the collection"""
		return Session.query(Job).filter(Job.job_state.in_(JobActiveStates)).all()

	def create(self):
		"""POST /jobs: Create a new job"""
        pass

	def new(self, format='html'):
		"""GET /jobs/new: Form to create a new item"""
		pass

	def update(self, id):
		"""PUT /jobs/id: Update an existing item"""
		# Forms posted to this method should contain a hidden field:
		#    <input type="hidden" name="_method" value="PUT" />
		# Or using helpers:
		#    h.form(url('job', id=ID),
		#           method='put')
		# url('job', id=ID)
		pass
	
	def delete(self, id):
		"""DELETE /jobs/id: Delete an existing item"""
		# Forms posted to this method should contain a hidden field:
		#    <input type="hidden" name="_method" value="DELETE" />
		# Or using helpers:
		#    h.form(url('job', id=ID),
		#           method='delete')
		# url('job', id=ID)
		pass
	
	@jsonify
	def show(self, id):
		"""GET /jobs/id: Show a specific item"""
		job   = Session.query(Job).get(id)
		if job is None:
			abort(404)
			
		files = job.files # Trigger the query, so it is serialized
		return job
	
	def edit(self, id, format='html'):
		"""GET /jobs/id/edit: Form to edit an existing item"""
		# url('edit_job', id=ID)
		pass

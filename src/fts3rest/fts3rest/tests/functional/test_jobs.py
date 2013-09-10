from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import Job, File
from routes import url_for
import json


class TestJobs(TestController):
	
	def test_submit_no_creds(self):
		assert 'GRST_CRED_AURI_0' not in self.app.extra_environ
		self.app.put(url = url_for(controller = 'jobs', action = 'submit'),
					 params = 'thisXisXnotXjson',
					 status = 403)

	def test_submit_no_delegation(self):
		self.setupGridsiteEnvironment()
		
		job = {'Files': [{'sources': ['root://source/file'],
						  'destinations': ['root://dest/file'],
						 }]}
		
		self.app.put(url = url_for(controller = 'jobs', action = 'submit'),
					 params = json.dumps(job),
					 status = 403)


	def _validateSubmitted(self, job, noVo = False):
		assert job is not None
		files = job.files
		assert files is not None
		
		assert job.user_dn   == '/DC=ch/DC=cern/OU=Test User'
		if noVo:
			assert job.vo_name   == ''
		else:
			assert job.vo_name   == 'testvo'
		assert job.job_state == 'SUBMITTED'
		
		assert job.source_se == 'root://source.es'
		assert job.dest_se   == 'root://dest.ch'
		assert job.overwrite_flag == True
		assert job.verify_checksum == True
		assert job.reuse_job == False

		assert len(files) == 1
		assert files[0].file_state  == 'SUBMITTED'
		assert files[0].source_surl == 'root://source.es/file'
		assert files[0].dest_surl   == 'root://dest.ch/file'
		assert files[0].source_se   == 'root://source.es'
		assert files[0].dest_se     == 'root://dest.ch'
		assert files[0].file_index  == 0
		assert files[0].selection_strategy == 'orderly'
		assert files[0].user_filesize == 1024
		assert files[0].checksum      == 'adler32:1234'
		assert files[0].file_metadata['mykey'] == 'myvalue'


	def test_submit(self):
		self.setupGridsiteEnvironment()
		self.pushDelegation()
		
		job = {'files': [{'sources':      ['root://source.es/file'],
						  'destinations': ['root://dest.ch/file'],
						  'selection_strategy': 'orderly',
						  'checksum':   'adler32:1234',
						  'filesize':    1024,
						  'metadata':    {'mykey': 'myvalue'},
						  }],
			  'params': {'overwrite': True, 'verify_checksum': True}}
		
		answer = self.app.put(url = url_for(controller = 'jobs', action = 'submit'),
							  params = json.dumps(job),
							  status = 200)
		
		# Make sure it was commited to the DB
		jobId = json.loads(answer.body)['job_id']
		assert len(jobId) > 0
		
		self._validateSubmitted(Session.query(Job).get(jobId))
		
		return jobId

	
	def test_submit_reuse(self):
		self.setupGridsiteEnvironment()
		self.pushDelegation()
		
		job = {'files': [{'sources':      ['root://source.es/file'],
						  'destinations': ['root://dest.ch/file'],
						  'selection_strategy': 'orderly',
						  'checksum':   'adler32:1234',
						  'filesize':    1024,
						  'metadata':    {'mykey': 'myvalue'},
						  }],
			  'params': {'overwrite': True, 'verify_checksum': True, 'reuse': True}}
		
		answer = self.app.put(url = url_for(controller = 'jobs', action = 'submit'),
							  params = json.dumps(job),
							  status = 200)
		
		# Make sure it was commited to the DB
		jobId = json.loads(answer.body)['job_id']
		assert len(jobId) > 0
		
		job = Session.query(Job).get(jobId)
		assert job.reuse_job == True
		
		return jobId
	
	
	def test_submit_post(self):
		self.setupGridsiteEnvironment()
		self.pushDelegation()
		
		job = {'files': [{'sources':      ['root://source.es/file'],
						  'destinations': ['root://dest.ch/file'],
						  'selection_strategy': 'orderly',
						  'checksum':   'adler32:1234',
						  'filesize':    1024,
						  'metadata':    {'mykey': 'myvalue'},
						  }],
			  'params': {'overwrite': True, 'verify_checksum': True}}
		
		answer = self.app.post(url = url_for(controller = 'jobs', action = 'submit'),
							   content_type = 'application/json',
							   params = json.dumps(job),
							   status = 200)
		
		# Make sure it was committed to the DB
		jobId = json.loads(answer.body)['job_id']
		assert len(jobId) > 0
		
		self._validateSubmitted(Session.query(Job).get(jobId))
		
		return jobId


	def test_submit_with_port(self):
		self.setupGridsiteEnvironment()
		self.pushDelegation()
		
		job = {'files': [{'sources':      ['srm://source.es:8446/file'],
						  'destinations': ['srm://dest.ch:8447/file'],
						  'selection_strategy': 'orderly',
						  'checksum':    'adler32:1234',
						  'filesize':    1024,
						  'metadata':    {'mykey': 'myvalue'},
						  }],
			  'params': {'overwrite': True, 'verify_checksum': True}}
		
		answer = self.app.post(url = url_for(controller = 'jobs', action = 'submit'),
							   content_type = 'application/json',
							   params = json.dumps(job),
							   status = 200)
		
		# Make sure it was committed to the DB
		jobId = json.loads(answer.body)['job_id']
		assert len(jobId) > 0
		
		dbJob = Session.query(Job).get(jobId)
		
		assert dbJob.source_se == 'srm://source.es'
		assert dbJob.dest_se   == 'srm://dest.ch'
		
		assert dbJob.files[0].source_se == 'srm://source.es'
		assert dbJob.files[0].dest_se   == 'srm://dest.ch'
		
		return jobId


	def test_submit_to_staging(self):
		self.setupGridsiteEnvironment()
		self.pushDelegation()
		
		job = {'files': [{'sources':      ['root://source.es/file'],
						  'destinations': ['root://dest.ch/file'],
						  'selection_strategy': 'orderly',
						  'checksum':    'adler32:1234',
						  'filesize':    1024,
						  'metadata':    {'mykey': 'myvalue'},
						  }],
			  'params': {'overwrite': True, 'copy_pin_lifetime': 3600, 'bring_online': 60,
						 'verify_checksum': True}}
		
		answer = self.app.post(url = url_for(controller = 'jobs', action = 'submit'),
							   content_type = 'application/json',
							   params = json.dumps(job),
							   status = 200)
		
		# Make sure it was committed to the DB
		jobId = json.loads(answer.body)['job_id']
		assert len(jobId) > 0
		
		dbJob = Session.query(Job).get(jobId)
		assert dbJob.job_state == 'STAGING'
		assert dbJob.files[0].file_state == 'STAGING'
		
		return jobId
	
	
	def test_submit_only_query(self):
		self.setupGridsiteEnvironment()
		self.pushDelegation()
		
		job = {'files': [{'sources':      ['http://source.es/?SFN=/path/'],
						  'destinations': ['http://dest.ch/file'],
						  'selection_strategy': 'orderly',
						  'checksum':    'adler32:1234',
						  'filesize':    1024,
						  'metadata':    {'mykey': 'myvalue'},
						  }],
			  'params': {'overwrite': True, 'copy_pin_lifetime': 3600, 'bring_online': 60,
						 'verify_checksum': True}}
		
		answer = self.app.post(url = url_for(controller = 'jobs', action = 'submit'),
							   content_type = 'application/json',
							   params = json.dumps(job),
							   status = 200)
		
		# Make sure it was committed to the DB
		jobId = json.loads(answer.body)['job_id']
		assert len(jobId) > 0
		
		dbJob = Session.query(Job).get(jobId)
		assert dbJob.job_state == 'STAGING'
		assert dbJob.files[0].file_state == 'STAGING'
		
		return jobId


	def test_cancel(self):
		jobId = self.test_submit()
		answer = self.app.delete(url = url_for(controller = 'jobs', action = 'cancel', id = jobId),
								 status = 200)
		job = json.loads(answer.body)
		
		assert job['job_id'] == jobId
		assert job['job_state'] == 'CANCELED'
		for f in job['files']:
			assert f['file_state'] == 'CANCELED'
		
		# Is it in the database?
		job = Session.query(Job).get(jobId)
		assert job.job_state == 'CANCELED'
		for f in job.files:
			assert f.file_state == 'CANCELED'


	def test_show_job(self):
		jobId = self.test_submit()
		answer = self.app.get(url = url_for(controller = 'jobs', action = 'show', id = jobId),
							  status = 200)
		job = json.loads(answer.body)
		
		assert job['job_id'] == jobId
		assert job['job_state'] == 'SUBMITTED'


	def test_list_job(self):
		jobId = self.test_submit()
		answer = self.app.get(url = url_for(controller = 'jobs', action = 'index'),
							  status = 200)
		jobList = json.loads(answer.body)
		
		assert jobId in map(lambda j: j['job_id'], jobList)


	def test_null_checksum(self):
		self.setupGridsiteEnvironment()
		self.pushDelegation()
		
		job = {'files': [{'sources':      ['root://source.es/file'],
						  'destinations': ['root://dest.ch/file'],
						  'selection_strategy': 'orderly',
						  'checksum':   None,
						  'filesize':    1024,
						  'metadata':    {'mykey': 'myvalue'},
						  }],
			  'params': {'overwrite': True, 'verify_checksum': True}}
		
		answer = self.app.post(url = url_for(controller = 'jobs', action = 'submit'),
							   content_type = 'application/json',
							   params = json.dumps(job),
							   status = 200)
		
		# Make sure it was committed to the DB
		jobId = json.loads(answer.body)['job_id']
		assert len(jobId) > 0
		
		job = Session.query(Job).get(jobId)
		assert job.files[0].checksum  == None
		
		return jobId
	
	
	def test_null_user_filesize(self):
		self.setupGridsiteEnvironment()
		self.pushDelegation()
		
		job = {'files': [{'sources':      ['root://source.es/file'],
						  'destinations': ['root://dest.ch/file'],
						  'selection_strategy': 'orderly',
						  'filesize':    None,
						  'metadata':    {'mykey': 'myvalue'},
						  }],
			  'params': {'overwrite': True, 'verify_checksum': True}}
		
		answer = self.app.post(url = url_for(controller = 'jobs', action = 'submit'),
							   content_type = 'application/json',
							   params = json.dumps(job),
							   status = 200)
		
		# Make sure it was committed to the DB
		jobId = json.loads(answer.body)['job_id']
		assert len(jobId) > 0
		
		job = Session.query(Job).get(jobId)
		assert job.files[0].user_filesize == 0
		
		return jobId
		
		
	def test_no_vo(self):
		self.setupGridsiteEnvironment(noVo = True)
		self.pushDelegation()
		
		job = {'files': [{'sources':      ['root://source.es/file'],
						  'destinations': ['root://dest.ch/file'],
						  'selection_strategy': 'orderly',
						  'checksum':   'adler32:1234',
						  'filesize':    1024,
						  'metadata':    {'mykey': 'myvalue'},
						  }],
			  'params': {'overwrite': True, 'verify_checksum': True}}
		
		answer = self.app.put(url = url_for(controller = 'jobs', action = 'submit'),
							  params = json.dumps(job),
							  status = 200)
		
		# Make sure it was commited to the DB
		jobId = json.loads(answer.body)['job_id']
		assert len(jobId) > 0
		
		self._validateSubmitted(Session.query(Job).get(jobId), noVo = True)


	def test_retry(self):
		self.setupGridsiteEnvironment()
		self.pushDelegation()
		
		job = {'files': [{'sources':      ['root://source.es/file'],
						  'destinations': ['root://dest.ch/file'],
						  'selection_strategy': 'orderly',
						  'checksum':   'adler32:1234',
						  'filesize':    1024,
						  'metadata':    {'mykey': 'myvalue'},
						  }],
			  'params': {'overwrite': True, 'verify_checksum': True, 'retry': 42}}
		
		answer = self.app.put(url = url_for(controller = 'jobs', action = 'submit'),
							  params = json.dumps(job),
							  status = 200)
		
		# Make sure it was commited to the DB
		jobId = json.loads(answer.body)['job_id']
		assert len(jobId) > 0
		
		job = Session.query(Job).get(jobId)
		self._validateSubmitted(job)
		assert job.retry == 42
		
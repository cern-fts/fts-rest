from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import Job, File
import hashlib
from routes import url_for
import json


class TestJobs(TestController):
	
	def test_submit_no_creds(self):
		self.assertFalse('GRST_CRED_AURI_0' in self.app.extra_environ)
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


	def _hashedId(self, id):
		digest = hashlib.md5(str(id)).digest()
		b16digest = ''.join(map(lambda c: "%02x" % ord(c), digest))
		return int(b16digest[:4], 16)


	def _validateSubmitted(self, job, noVo = False):
		self.assertNotEqual(job, None)
		files = job.files
		self.assertNotEqual(files, None)
		
		self.assertEqual(job.user_dn, '/DC=ch/DC=cern/OU=Test User')
		if noVo:
			self.assertEqual(job.vo_name, 'nil')
		else:
			self.assertEqual(job.vo_name, 'testvo')
		self.assertEqual(job.job_state, 'SUBMITTED')
		
		self.assertEqual(job.source_se, 'root://source.es') 
		self.assertEqual(job.dest_se, 'root://dest.ch') 
		self.assertEqual(job.overwrite_flag, True)
		self.assertEqual(job.verify_checksum, True)
		self.assertEqual(job.reuse_job, False)

		self.assertEqual(len(files), 1)
		self.assertEqual(files[0].file_state, 'SUBMITTED') 
		self.assertEqual(files[0].source_surl, 'root://source.es/file')
		self.assertEqual(files[0].dest_surl, 'root://dest.ch/file') 
		self.assertEqual(files[0].source_se, 'root://source.es') 
		self.assertEqual(files[0].dest_se, 'root://dest.ch') 
		self.assertEqual(files[0].file_index, 0)
		self.assertEqual(files[0].selection_strategy, 'orderly') 
		self.assertEqual(files[0].user_filesize, 1024) 
		self.assertEqual(files[0].checksum, 'adler32:1234') 
		self.assertEqual(files[0].file_metadata['mykey'], 'myvalue') 

		self.assertEquals(self._hashedId(files[0].file_id), files[0].hashed_id) 


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
		self.assertTrue(len(jobId) > 0)
		
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
		self.assertTrue(len(jobId) > 0)
		
		job = Session.query(Job).get(jobId)
		self.assertEqual(job.reuse_job, True)
		
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
		self.assertTrue(len(jobId) > 0)
		
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
		self.assertTrue(len(jobId) > 0)
		
		dbJob = Session.query(Job).get(jobId)
		
		self.assertEqual(dbJob.source_se, 'srm://source.es')
		self.assertEqual(dbJob.dest_se, 'srm://dest.ch') 
		
		self.assertEqual(dbJob.files[0].source_se, 'srm://source.es') 
		self.assertEqual(dbJob.files[0].dest_se, 'srm://dest.ch') 
		
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
		self.assertTrue(len(jobId) > 0)
		
		dbJob = Session.query(Job).get(jobId)
		self.assertEqual(dbJob.job_state, 'STAGING') 
		self.assertEqual(dbJob.files[0].file_state, 'STAGING') 
		
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
		self.assertTrue(len(jobId) > 0)
		
		dbJob = Session.query(Job).get(jobId)
		self.assertEqual(dbJob.job_state, 'STAGING') 
		self.assertEqual(dbJob.files[0].file_state, 'STAGING') 
		
		return jobId


	def test_cancel(self):
		jobId = self.test_submit()
		answer = self.app.delete(url = url_for(controller = 'jobs', action = 'cancel', id = jobId),
								 status = 200)
		job = json.loads(answer.body)
		
		self.assertEqual(job['job_id'], jobId) 
		self.assertEqual(job['job_state'], 'CANCELED') 
		for f in job['files']:
			self.assertEqual(f['file_state'], 'CANCELED') 
		
		# Is it in the database?
		job = Session.query(Job).get(jobId)
		self.assertEqual(job.job_state,'CANCELED')
		for f in job.files:
			self.assertEqual(f.file_state, 'CANCELED')


	def test_show_job(self):
		jobId = self.test_submit()
		answer = self.app.get(url = url_for(controller = 'jobs', action = 'show', id = jobId),
							  status = 200)
		job = json.loads(answer.body)
		
		self.assertEqual(job['job_id'], jobId) 
		self.assertEqual(job['job_state'], 'SUBMITTED') 


	def test_list_job(self):
		jobId = self.test_submit()
		answer = self.app.get(url = url_for(controller = 'jobs', action = 'index'),
							  status = 200)
		jobList = json.loads(answer.body)
		
		self.assertTrue(jobId in map(lambda j: j['job_id'], jobList))


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
		self.assertTrue(len(jobId) > 0)
		
		job = Session.query(Job).get(jobId)
		self.assertEqual(job.files[0].checksum, None)
		
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
		self.assertTrue(len(jobId) > 0) 
		
		job = Session.query(Job).get(jobId)
		self.assertEqual(job.files[0].user_filesize, 0)
		
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
		self.assertTrue(len(jobId) > 0)
		
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
		self.assertTrue(len(jobId) > 0)
		
		job = Session.query(Job).get(jobId)
		self._validateSubmitted(job)
		self.assertEqual(job.retry, 42)
		
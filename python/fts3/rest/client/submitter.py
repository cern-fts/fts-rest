from base import Actor
from exceptions import *
import json
import urllib



class Submitter(Actor):
	
	def __init__(self, *args, **kwargs):
		super(Submitter, self).__init__(*args, **kwargs)


	def _buildSubmission(self, source, destination, **kwargs):
		job = dict()

		job['transfers'] = []
		
		transfer = {'source': source, 'destination': destination}
		if 'checksum' in kwargs:
			transfer['checksum'] = kwargs['checksum']
		if 'filesize' in kwargs:
			transfer['filesize'] = kwargs['filesize']
		if 'file_metadata' in kwargs:
			transfer['metadata'] = kwargs['file_metadata']
		
		job['transfers'].append(transfer)		
		
		
		job['params'] = dict()
		job['params'].update(kwargs)
		del job['params']['checksum']
		del job['params']['filesize']
		del job['params']['file_metadata']		
		
		return json.dumps(job, indent = 2)


	def submit(self, source, destination, **kwargs):
		job = self._buildSubmission(source, destination, **kwargs)
		r = json.loads(self.requester.put("%s/jobs" % self.endpoint, job))
		return r['job_id']

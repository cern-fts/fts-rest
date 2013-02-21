from base import Actor
from exceptions import *
import json



class JobInquirer(Actor):
	
	def __init__(self, *args, **kwargs):
		super(JobInquirer, self).__init__(*args, **kwargs)


	def getJobStatus(self, jobId):
		url = "%s/jobs/%s" % (self.endpoint, jobId)
		
		try:
			return json.loads(self.requester.get(url))
		except NotFound:
			raise NotFound(jobId)

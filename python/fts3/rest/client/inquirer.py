from base import Actor
from exceptions import *
import json
import urllib


class Inquirer(Actor):
	
	def __init__(self, *args, **kwargs):
		super(Inquirer, self).__init__(*args, **kwargs)


	def getJobStatus(self, jobId):
		url = "%s/jobs/%s" % (self.endpoint, jobId)
		
		try:
			return json.loads(self.requester.get(url))
		except NotFound:
			raise NotFound(jobId)


	def getJobList(self, userDn = None, voName = None):
		url = "%s/jobs?" % self.endpoint	
		args = {}
		if userDn: args['user_dn'] = userDn
		if voName: args['vo_name'] = voName
		
		query = '&'.join(map(lambda (k, v): "%s=%s" % (k, urllib.quote(v, '')), args.iteritems()))
		url += query
		
		return json.loads(self.requester.get(url))

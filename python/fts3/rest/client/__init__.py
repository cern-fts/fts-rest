import json
import urllib2



class ClientV1(object):
	
	def __init__(self, endpoint):
		self.endpoint = endpoint
		if self.endpoint.endswith('/'):
			self.endpoint = self.endpoint[:-1]
	
			
	
	def getEndpointInfo(self):
		url = "%s/ping" % (self.endpoint)
		
		try:
			f = urllib2.urlopen(url)
			j = json.loads(f.read())
			return {'url': self.endpoint,
			    	'version': j['api'],
			    	'schema': j['schema']}
		except Exception, e:
			raise IOError(e)
		
	
		
	def getJobStatus(self, jobId):
		url = "%s/job/%s/" % (self.endpoint, jobId)
		
		try:
			f = urllib2.urlopen(url)
			return json.loads(f.read())
		except urllib2.HTTPError, e:
			if e.code == 404:
				raise KeyError("requestID <%s> was not found" % jobId)
			else:
				raise IOError(e)
		except Exception, e:
			raise IOError(e)
	
	
	def getJobTransfers(self, jobId):
		url = "%s/job/%s/files/" % (self.endpoint, jobId)
		try:
			f = urllib2.urlopen(url)
			return json.loads(f.read())['objects']
		except urllib2.HTTPError, e:
			if e.code == 404:
				raise KeyError("requestID <%s> was not found" % jobId)
			else:
				raise IOError(e)
		except Exception, e:
			raise IOError(e)

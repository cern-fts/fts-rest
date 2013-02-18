
class FTS3ClientException(Exception):
	pass



class BadEndpoint(FTS3ClientException):
	def __init__(self, endpoint):
		self.endpoint = endpoint
		
	def __str__(self):
		return "Bad endpoint: %s" % self.endpoint



class Unauthorized(FTS3ClientException):
	def __str__(self):
		return "Unauthorized"



class ClientError(FTS3ClientException):
	def __init__(self, reason):
		self.reason = reason
		
	def __str__(self):
		return "Client error: %s" % self.reason



class ServerError(FTS3ClientException):
	def __init__(self, reason):
		self.reason = reason
		
	def __str__(self):
		return "Server error: %s" % self.reason
	


class NotFound(FTS3ClientException):
	def __init__(self, resource):
		self.resource = resource
		
	def __str__(self):
		return "Not found: %s" % self.resource

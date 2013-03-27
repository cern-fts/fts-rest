from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3.model import CredentialVersion, SchemaVersion
from pylons import request

class MiscController(BaseController):
	
	@jsonify
	def apiVersion(self):
		credV   = Session.query(CredentialVersion)[0]
		schemaV = Session.query(SchemaVersion)[0]
		return {'api': '0.0.1',
			    'schema': credV,
			    'delegation': schemaV}

	@jsonify
	def whoami(self):
		return request.environ['fts3.User.Credentials']

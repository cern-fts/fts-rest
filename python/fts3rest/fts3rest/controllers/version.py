from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3.orm import CredentialVersion, SchemaVersion


class VersionController(BaseController):
	
	@jsonify
	def api(self):
		credV   = Session.query(CredentialVersion)[0]
		schemaV = Session.query(SchemaVersion)[0]
		return {'api': 'Mk.1',
			    'schema': credV,
			    'delegation': schemaV}

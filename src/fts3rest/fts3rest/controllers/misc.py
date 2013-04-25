from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3.model import CredentialVersion, SchemaVersion
from pylons import request


class _Version:
	def __init__(self, major, minor, patch):
		self.major = major
		self.minor = minor
		self.patch = patch


class MiscController(BaseController):
	
	@jsonify
	def apiVersion(self):
		credV   = Session.query(CredentialVersion)[0]
		schemaV = Session.query(SchemaVersion)[0]
		return {'api': _Version(0, 2, 0),
			    'schema': credV,
			    'delegation': schemaV,
			    '_links': {
					'curies': [{'name': 'fts', 'href': 'https://svnweb.cern.ch/trac/fts3'}],
					
					'fts:whoami': {'href': '/whoami', 'title': 'Check user certificate'},
					
					'fts:joblist': {'href': '/jobs{?vo_name,user_dn}', 'title': 'List of active jobs', 'templated': True},
					'fts:job': {
						'href': '/jobs/{id}',
						'title': 'Job information',
						'templated': True,
						'hints': {
							'allow': ['GET', 'DELETE']
						}
					},
					
					
					'fts:configaudit': {'href': '/config/audit', 'title': 'Configuration'},
					
					'fts:submitschema': {'href': '/schema/submit', 'title': 'JSON schema of messages'},
					'fts:jobsubmit': {
						'href': '/jobs',
						'hints': {
							'allow': ['POST'],
							'representations': ['fts:submitschema']
						}
					},
				}
			}

	@jsonify
	def whoami(self):
		return request.environ['fts3.User.Credentials']

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
    def api_version(self):
        cred_v = Session.query(CredentialVersion)[0]
        schema_v = Session.query(SchemaVersion)[0]
        return {
            'api': _Version(3, 2, 0),
            'schema': cred_v,
            'delegation': schema_v,
            '_links': {
                'curies': [{'name': 'fts', 'href': 'https://svnweb.cern.ch/trac/fts3'}],

                'fts:whoami': {'href': '/whoami', 'title': 'Check user certificate'},

                'fts:joblist': {
                    'href': '/jobs{?vo_name,user_dn,dlg_id,state_in}',
                    'title': 'List of active jobs',
                    'templated': True
                },
                'fts:job': {
                    'href': '/jobs/{id}',
                    'title': 'Job information',
                    'templated': True,
                    'hints': {
                        'allow': ['GET', 'DELETE']
                    }
                },


                'fts:configaudit': {'href': '/config/audit', 'title': 'Configuration'},

                'fts:submitschema': {'href': '/api-docs/schema/submit', 'title': 'JSON schema of messages'},
                'fts:apidocs': {'href': '/api-docs/', 'title': 'API Documentation'},
                'fts:jobsubmit': {
                    'href': '/jobs',
                    'hints': {
                        'allow': ['POST'],
                        'representations': ['fts:submitschema']
                    }
                },

                'fts:optimizer': {'href': '/optimizer/', 'title': 'Optimizer'},

                'fts:archive':  {'href': '/archive/', 'title': 'Archive'}
            }
        }

    @jsonify
    def whoami(self):
        """
        Returns the active credentials of the user
        """
        return request.environ['fts3.User.Credentials']

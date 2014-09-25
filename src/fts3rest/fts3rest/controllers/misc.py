#   Copyright notice:
#   Copyright  Members of the EMI Collaboration, 2013.
#
#   See www.eu-emi.eu for details on the copyright holders
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.middleware.fts3auth import require_certificate
from fts3.model import CredentialVersion, SchemaVersion
from pylons import request, response


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
            'api': _Version(3, 2, 28),
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

    @require_certificate
    def certificate(self):
        """
        Returns the user certificate
        """
        response.headers['Content-Type'] = 'application/x-pem-file'
        return request.environ.get('SSL_CLIENT_CERT', None)

    @jsonify
    def whoami(self):
        """
        Returns the active credentials of the user
        """
        return request.environ['fts3.User.Credentials']

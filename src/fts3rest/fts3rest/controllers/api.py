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

import pylons

from routes import request_config
from webob.exc import HTTPNotFound

from fts3.model import CredentialVersion, SchemaVersion

from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib import api

API_VERSION = dict(major=3, minor=5, patch=0)


class ApiController(BaseController):
    """
    API documentation
    """

    def __init__(self):
        self.resources, self.apis, self.models = api.introspect()
        self.resources.sort(key=lambda res: res['id'])
        for r in self.apis.values():
            r.sort(key=lambda a: a['path'])
        # Add path to each resource
        for r in self.resources:
            r['path'] = '/' + r['id']

    @jsonify
    def api_version(self):
        cred_v = Session.query(CredentialVersion).all()
        cred_v = cred_v[0] if cred_v else None
        schema_v = Session.query(SchemaVersion).all()
        schema_v = schema_v[0] if schema_v else None
        return {
            'api': API_VERSION,
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
    def submit_schema(self):
        """
        Json-schema for the submission operation

        This can be used to validate the submission. For instance, in Python,
        jsonschema.validate
        """
        return api.SubmitSchema

    @jsonify
    def api_docs(self):
        """
        Auto-generated API documentation

        Compatible with Swagger-UI
        """
        return {
            'swaggerVersion': '1.2',
            'apis': self.resources,
            'info': {
                'title': 'FTS3 RESTful API',
                'description': 'FTS3 RESTful API documentation',
                'contact': 'fts-devel@cern.ch',
                'license': 'Apache 2.0',
                'licenseUrl': 'http://www.apache.org/licenses/LICENSE-2.0.html'
            }
        }

    @doc.response(404, 'The resource can not be found')
    @jsonify
    def resource_doc(self, resource):
        """
        Auto-generated API documentation for a specific resource
        """
        if resource not in self.apis:
            raise HTTPNotFound('API not found: ' + resource)
        return {
            'basePath': '/',
            'swaggerVersion': '1.2',
            'produces': ['application/json'],
            'resourcePath': '/' + resource,
            'authorizations': {},
            'apis': self.apis.get(resource, []),
            'models': self.models.get(resource, []),
        }

    def options_handler(self, path, environ):
        """
        Generates a response for an OPTIONS request
        """
        mapper = request_config(original=False).mapper
        mapper.create_regs()

        full_path = '/' + path
        routes = list()
        for route in mapper.matchlist:
            match = route.match(full_path)
            if isinstance(match, dict) or match:
                routes.append(route)

        if len(routes) == 0:
            raise HTTPNotFound()

        allowed = set()
        for route in routes:
            if route.conditions and 'method' in route.conditions:
                allowed.update(set(route.conditions['method']))

        # If only this handler matches, consider this a Not Found
        if allowed == set(['OPTIONS']):
            raise HTTPNotFound()

        pylons.response.headers['Allow'] = ', '.join(allowed)
        return None

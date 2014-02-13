from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib import api
from pylons import request
from pylons.controllers.util import abort


class ApiController(BaseController):
    
    def __init__(self):
        self.resources, self.apis, self.models = api.introspect() 
     
    @jsonify
    def submit_schema(self):
        """
        Return the json-schema for the submission operation, so it can
        be used to validate
        """
        return api.SubmitSchema

    @jsonify
    def api_docs(self):
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

    @jsonify
    def resource_doc(self, resource):
        resource_path = '/' + resource
        if resource_path not in self.apis:
            abort(404, 'API not found: ' + resource) 
        return {
           'basePath': '/',
           'swaggerVersion': '1.2',
           'produces': ['application/json'],
           'resourcePath': '/' + resource,
           'authorizations': {},
           'apis': self.apis.get(resource_path, []),
           'models': self.models.get(resource_path, []),
        }

from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController
from fts3rest.lib.helpers import jsonify
from fts3rest.lib import api
from pylons.controllers.util import abort


class ApiController(BaseController):
    """
    API documentation
    """
    
    def __init__(self):
        self.resources, self.apis, self.models = api.introspect()
        self.resources.sort(key=lambda res: res['path'])
        for r in self.apis.values():
            r.sort(key=lambda a: a['path'])
     
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

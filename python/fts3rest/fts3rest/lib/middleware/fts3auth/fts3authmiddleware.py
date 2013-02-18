from fts3rest.lib.base import Session
from credentials import UserCredentials
from webob.exc import HTTPForbidden


class FTS3AuthMiddleware(object):
    
    def __init__(self, wrap_app, config):
        self.app    = wrap_app
        self.config = config
        
        
    def __call__(self, environ, start_response):
        credentials = UserCredentials(environ, self.config['fts3.Roles'])
        
        if not credentials.user_dn:
            return HTTPForbidden('A valid X509 certificate or proxy is needed')(environ, start_response)
            
        environ['fts3.User.Credentials'] = credentials
        
        return self.app(environ, start_response)

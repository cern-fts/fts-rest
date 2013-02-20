from fts3rest.lib.base import Session
from fts3.orm import BannedDN
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
		
		if not self._hasAuthorizedVo(credentials):
			return HTTPForbidden('The user does not belong to any authorized vo')(environ, start_response)
		
		if self._isBanned(credentials):
			return HTTPForbidden('The user has been banned')(environ, start_response)
		
		environ['fts3.User.Credentials'] = credentials
		
		return self.app(environ, start_response)
	
	
	def _hasAuthorizedVo(self, credentials):
		if '*' in self.config['fts3.AuthorizedVO']:
			return True
		
		for v in credentials.vos:
			if v in self.config['fts3.AuthorizedVO']:
				return True 
		return False

	
	def _isBanned(self, credentials):
		banned = Session.query(BannedDN).get(credentials.user_dn)
		return banned is not None

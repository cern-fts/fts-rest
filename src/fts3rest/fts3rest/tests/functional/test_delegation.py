from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import CredentialCache
from routes import url_for
import json


class TestDelegation(TestController):
    
    def test_put_cred_without_cache(self):
        # This is a regression test. It tries to PUT directly
        # credentials without the previous negotiation, so there is no
        # CredentialCache in the database
        Session.query(CredentialCache).delete()
        self.setupGridsiteEnvironment()
        
        creds = self.getUserCredentials()
        
        answer = self.app.put(url = url_for(controller = 'delegation', action = 'credential', id = creds.delegation_id),
                              params = self.getX509Proxy(),
                              status = 400)


    def test_put_malformed_pem(self):
        self.setupGridsiteEnvironment()       
        creds = self.getUserCredentials()
        
        request = self.app.get(url = url_for(controller = 'delegation', action = 'request', id = creds.delegation_id),
                               status = 200)
                
        answer = self.app.put(url = url_for(controller = 'delegation', action = 'credential', id = creds.delegation_id),
                              params = 'MALFORMED!!!1',
                              status = 400)
        
        
    def test_valid_proxy(self):
        self.setupGridsiteEnvironment()
        creds = self.getUserCredentials()
        proxy = self.getX509Proxy()
        
        request = self.app.get(url = url_for(controller = 'delegation', action = 'request', id = creds.delegation_id),
                               status = 200)
        
        answer = self.app.put(url = url_for(controller = 'delegation', action = 'credential', id = creds.delegation_id),
                              params = proxy,
                              status = 201)
    
        
    def test_dn_mismatch(self):
        self.setupGridsiteEnvironment()
        creds = self.getUserCredentials()
        proxy = self.getX509Proxy([('DC', 'dummy')])
        
        request = self.app.get(url = url_for(controller = 'delegation', action = 'request', id = creds.delegation_id),
                               status = 200)
        
        answer = self.app.put(url = url_for(controller = 'delegation', action = 'credential', id = creds.delegation_id),
                              params = proxy,
                              status = 400)

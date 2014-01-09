from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import Credential, CredentialCache
from routes import url_for
from datetime import datetime
import json
import pytz
import time


class TestDelegation(TestController):
    
    def _get_termination_time(self, dlg_id):
        answer = self.app.get(url = url_for(controller = 'delegation', action = 'view', id = dlg_id))
        tt = datetime.strptime(str(json.loads(answer.body)['termination_time']), '%Y-%m-%dT%H:%M:%S')
        return tt.replace(tzinfo = pytz.UTC)


    def test_put_cred_without_cache(self):
        """
        This is a regression test. It tries to PUT directly
        credentials without the previous negotiation, so there is no
        CredentialCache in the database. This attempt must fail.
        """
        self.setupGridsiteEnvironment()
        creds = self.getUserCredentials()
        
        request = self.app.get(url = url_for(controller = 'delegation', action = 'request', id = creds.delegation_id),
                               status = 200)
        proxy = self.getX509Proxy(request.body)
        
        Session.delete(Session.query(CredentialCache).get((creds.delegation_id, creds.user_dn)))
        
        answer = self.app.put(url = url_for(controller = 'delegation', action = 'credential', id = creds.delegation_id),
                              params = proxy,
                              status = 400)


    def test_put_malformed_pem(self):
        """
        Putting a malformed proxy must fail
        """
        self.setupGridsiteEnvironment()       
        creds = self.getUserCredentials()
        
        request = self.app.get(url = url_for(controller = 'delegation', action = 'request', id = creds.delegation_id),
                               status = 200)
                
        answer = self.app.put(url = url_for(controller = 'delegation', action = 'credential', id = creds.delegation_id),
                              params = 'MALFORMED!!!1',
                              status = 400)
        
        
    def test_valid_proxy(self):
        """
        Putting a well-formed proxy with all the right steps must succeed
        """
        self.setupGridsiteEnvironment()
        creds = self.getUserCredentials()
        
        request = self.app.get(url = url_for(controller = 'delegation', action = 'request', id = creds.delegation_id),
                               status = 200)
        proxy = self.getX509Proxy(request.body)
        
        answer = self.app.put(url = url_for(controller = 'delegation', action = 'credential', id = creds.delegation_id),
                              params = proxy,
                              status = 201)
        
        cred = Session.query(Credential).get((creds.delegation_id, creds.user_dn))
        self.assertNotEqual(None, cred)
        return cred

        
    def test_dn_mismatch(self):
        """
        A well-formed proxy with mismatching issuer and subject must fail
        """
        self.setupGridsiteEnvironment()
        creds = self.getUserCredentials()
        
        request = self.app.get(url = url_for(controller = 'delegation', action = 'request', id = creds.delegation_id),
                               status = 200)
        
        proxy = self.getX509Proxy(request.body, subject = [('DC', 'dummy')])
        
        answer = self.app.put(url = url_for(controller = 'delegation', action = 'credential', id = creds.delegation_id),
                              params = proxy,
                              status = 400)


    def test_get_request_different_dlg_id(self):
        """
        A user should be able only to get his/her own proxy request,
        and be denied any other.
        """
        self.setupGridsiteEnvironment()
        creds = self.getUserCredentials()

        request = self.app.get(url = url_for(controller = 'delegation', action = 'request', id = '12345xx'),
                               status = 403)

    def test_view_different_dlg_id(self):
        """
        A user should be able only to get his/her own delegation information.
        """
        self.setupGridsiteEnvironment()
        creds = self.getUserCredentials()

        request = self.app.get(url = url_for(controller = 'delegation', action = 'view', id = '12345xx'),
                               status = 403)

    def test_remove_delegation(self):
        """
        A user should be able to remove his/her proxy
        """
        self.setupGridsiteEnvironment()
        creds = self.getUserCredentials()
        
        self.test_valid_proxy()
        
        request = self.app.delete(url = url_for(controller = 'delegation', action = 'delete', id = creds.delegation_id),
                                  status = 204)
        
        request = self.app.delete(url = url_for(controller = 'delegation', action = 'delete', id = creds.delegation_id),
                                  status = 404)
        
        cred = Session.query(Credential).get((creds.delegation_id, creds.user_dn))
        self.assertEqual(None, cred)

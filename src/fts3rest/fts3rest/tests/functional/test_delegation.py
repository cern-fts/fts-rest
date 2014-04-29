from datetime import datetime, timedelta
from M2Crypto import EVP
from nose.plugins.skip import SkipTest
import json
import time

from fts3rest.controllers.delegation import _generate_proxy_request
from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import Credential, CredentialCache


class TestDelegation(TestController):
    """
    Tests for the delegation controller
    """

    def test_get_termination_time_not_existing(self):
        """
        Get the termination time for a dlg_id that hasn't delegated yet
        """
        self.setup_gridsite_environment()
        creds = self.get_user_credentials()

        answer = self.app.get(url="/delegation/%s" % creds.delegation_id, status=200)

        self.assertEqual(json.loads(answer.body), None)

    def test_get_termination_time(self):
        self.test_valid_proxy()
        creds = self.get_user_credentials()

        answer = self.app.get(url="/delegation/%s" % creds.delegation_id, status=200)

        termination = datetime.strptime(json.loads(answer.body)['termination_time'], '%Y-%m-%dT%H:%M:%S')
        self.assertGreater(termination, datetime.utcnow() + timedelta(hours=2, minutes=58))

    def test_put_cred_without_cache(self):
        """
        This is a regression test. It tries to PUT directly
        credentials without the previous negotiation, so there is no
        CredentialCache in the database. This attempt must fail.
        """
        self.setup_gridsite_environment()
        creds = self.get_user_credentials()

        request = self.app.get(url="/delegation/%s/request" % creds.delegation_id,
                               status=200)
        proxy = self.get_x509_proxy(request.body)

        Session.delete(Session.query(CredentialCache).get((creds.delegation_id, creds.user_dn)))

        self.app.put(url="/delegation/%s/credential" % creds.delegation_id,
                     params=proxy,
                     status=400)

    def test_put_malformed_pem(self):
        """
        Putting a malformed proxy must fail
        """
        self.setup_gridsite_environment()
        creds = self.get_user_credentials()

        self.app.get(url="/delegation/%s/request" % creds.delegation_id,
                     status=200)

        self.app.put(url="/delegation/%s/credential" % creds.delegation_id,
                     params='MALFORMED!!!1',
                     status=400)

    def test_valid_proxy(self):
        """
        Putting a well-formed proxy with all the right steps must succeed
        """
        self.setup_gridsite_environment()
        creds = self.get_user_credentials()

        request = self.app.get(url="/delegation/%s/request" % creds.delegation_id,
                               status=200)
        proxy = self.get_x509_proxy(request.body)

        self.app.put(url="/delegation/%s/credential" % creds.delegation_id,
                     params=proxy,
                     status=201)

        proxy = Session.query(Credential).get((creds.delegation_id, creds.user_dn))
        self.assertNotEqual(None, proxy)
        return proxy

    def test_dn_mismatch(self):
        """
        A well-formed proxy with mismatching issuer and subject must fail
        """
        self.setup_gridsite_environment()
        creds = self.get_user_credentials()

        request = self.app.get(url="/delegation/%s/request" % creds.delegation_id,
                               status=200)

        proxy = self.get_x509_proxy(request.body, subject=[('DC', 'dummy')])

        self.app.put(url="/delegation/%s/credential" % creds.delegation_id,
                     params=proxy,
                     status=400)

    def test_signed_wrong_priv_key(self):
        """
        Regression for FTS-30
        If a proxy is signed with an invalid private key, reject it
        """
        self.setup_gridsite_environment()
        creds = self.get_user_credentials()

        request = self.app.get(url="/delegation/%s/request" % creds.delegation_id,
                               status=200)

        proxy = self.get_x509_proxy(request.body, private_key=EVP.PKey())

        self.app.put(url="/delegation/%s/credential" % creds.delegation_id,
                     params=proxy,
                     status=400)

    def test_wrong_request(self):
        """
        Get a request, sign a different request and send it
        """
        self.setup_gridsite_environment()
        creds = self.get_user_credentials()

        self.app.get(url="/delegation/%s/request" % creds.delegation_id,
                     status=200)

        (different_request, _) = _generate_proxy_request()
        proxy = self.get_x509_proxy(different_request.as_pem(), private_key=EVP.PKey())

        self.app.put(url="/delegation/%s/credential" % creds.delegation_id,
                     params=proxy,
                     status=400)

    def test_get_request_different_dlg_id(self):
        """
        A user should be able only to get his/her own proxy request,
        and be denied any other.
        """
        self.setup_gridsite_environment()

        self.app.get(url="/delegation/12345xx/request",
                     status=403)

    def test_view_different_dlg_id(self):
        """
        A user should be able only to get his/her own delegation information.
        """
        self.setup_gridsite_environment()

        self.app.get(url="/delegation/12345x",
                     status=403)

    def test_remove_delegation(self):
        """
        A user should be able to remove his/her proxy
        """
        self.setup_gridsite_environment()
        creds = self.get_user_credentials()

        self.test_valid_proxy()

        self.app.delete(url="/delegation/%s" % creds.delegation_id,
                        status=204)

        self.app.delete(url="/delegation/%s" % creds.delegation_id,
                        status=404)

        proxy = Session.query(Credential).get((creds.delegation_id, creds.user_dn))
        self.assertEqual(None, proxy)

    def test_set_voms(self):
        """
        The server must regenerate a proxy with VOMS extensions
        Need a real proxy for this one
        """
        self.setup_gridsite_environment()
        creds = self.get_user_credentials()

        # Need to push a real proxy :/
        proxy_pem = self.get_real_x509_proxy()
        if proxy_pem is None:
            raise SkipTest('Could not get a valid real proxy for test_set_voms')

        proxy = Credential()
        proxy.dn = creds.user_dn
        proxy.dlg_id = creds.delegation_id
        proxy.termination_time = datetime.utcnow() + timedelta(hours=1)
        proxy.proxy = proxy_pem
        Session.merge(proxy)
        Session.commit()

        # Now, request the voms extensions
        self.app.post(url="/delegation/%s/voms" % creds.delegation_id,
                      content_type='application/json',
                      params=json.dumps(['dteam:/dteam/Role=lcgadmin']),
                      status=203)

        # And validate
        proxy2 = Session.query(Credential).get((creds.delegation_id, creds.user_dn))
        self.assertNotEqual(proxy.proxy, proxy2.proxy)
        self.assertEqual('dteam:/dteam/Role=lcgadmin', proxy2.voms_attrs)

    def test_delegate_rfc(self):
        """
        Delegate an RFC-like proxy
        """
        self.setup_gridsite_environment()
        creds = self.get_user_credentials()

        request = self.app.get(url="/delegation/%s/request" % creds.delegation_id,
                               status=200)

        proxy = self.get_x509_proxy(
            request.body,
            subject=[('DC', 'ch'), ('DC', 'cern'), ('OU', 'Test User'), ('CN', str(int(time.time())))]
        )

        self.app.put(url="/delegation/%s/credential" % creds.delegation_id,
                     params=proxy,
                     status=201)

        proxy = Session.query(Credential).get((creds.delegation_id, creds.user_dn))
        self.assertNotEqual(None, proxy)

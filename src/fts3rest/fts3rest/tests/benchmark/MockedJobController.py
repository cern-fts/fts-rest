from datetime import datetime, timedelta
from paste.registry import Registry
from pylons import request, response

from fts3.model import Credential
from fts3rest.controllers.jobs import JobsController
from fts3rest.lib.middleware import fts3auth
from fts3rest.model import Session


class MockCredentials:
    def __init__(self):
        self.delegation_id = '12345'
        self.user_dn = '/DN=1234'
        self.voms_cred = []
        self.vos = []

    def get_granted_level_for(self, operation):
        return fts3auth.constants.ALL


class MockRequest(object):
    def __init__(self):
        self.environ = {
            'fts3.User.Credentials': MockCredentials()
        }


class MockResponse(object):
    def __init__(self):
        self.headers = {}


class MockedJobController(JobsController):
    """
    Inherit from JobsController and mock some required objects
    """

    def __init__(self):
        super(MockedJobController, self).__init__()
        # Register into paste the fake request and response objects
        registry = Registry()
        registry.prepare()
        registry.register(request, MockRequest())
        registry.register(response, MockResponse())

        # This is expected to be set by Pylons, so we set it here
        self._py_object = type("", (), {
            "__init__": (lambda s, **kwargs: s.__dict__.update(kwargs))
        })(request=request, response=response)

        # Inject fake proxy, so the submission works
        delegated = Credential(
            dlg_id='12345', dn='/DN=1234', proxy='',
            termination_time=datetime.utcnow() + timedelta(hours=5)
        )
        Session.merge(delegated)
        Session.commit()


__all__ = ["MockedJobController"]

from fts3.model import ConfigAudit
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.middleware.fts3auth import authorize
from fts3rest.lib.middleware.fts3auth.constants import *


class ConfigController(BaseController):
    """
    Operations on the config audit
    """

    @doc.return_type(array_of=ConfigAudit)
    @authorize(CONFIG)
    @jsonify
    def audit(self, **kwargs):
        """
        Returns the last 100 entries of the config audit tables
        """
        return Session.query(ConfigAudit).limit(100).all()

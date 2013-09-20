from fts3.model import ConfigAudit
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.middleware.fts3auth import authorize, authorized
from fts3rest.lib.middleware.fts3auth.constants import *


class ConfigController(BaseController):

    @authorize(CONFIG)
    @jsonify
    def audit(self, **kwargs):
        auditList = Session.query(ConfigAudit)
        return list(auditList)

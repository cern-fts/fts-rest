#   Copyright notice:
#
#   Copyright CERN 2013-2015
#
#   Copyright Members of the EMI Collaboration, 2013.
#       See www.eu-emi.eu for details on the copyright holders
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

try:
    import simplejson as json
except:
    import json
import logging
from numbers import Number
from pylons import request

from fts3.model import *
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import accept
from fts3rest.lib.http_exceptions import HTTPBadRequest
from fts3rest.lib.middleware.fts3auth import authorize
from fts3rest.lib.middleware.fts3auth.constants import CONFIG


log = logging.getLogger(__name__)


def audit_configuration(action, config):
    """
    Logs and stores in the DB a configuration action
    """
    audit = ConfigAudit(
        datetime=datetime.utcnow(),
        dn=request.environ['fts3.User.Credentials'].user_dn,
        config=config,
        action=action
    )
    Session.add(audit)
    log.info(action)


def validate_type(Type, key, value):
    """
    Validate that value is of a suitable type of the attribute key of the type Type
    """
    column = Type.__table__.columns.get(key, None)
    if column is None:
        raise HTTPBadRequest('Field %s unknown' % key)

    type_map = {
        Integer: int,
        String: basestring,
        Flag: bool,
        DateTime: basestring,
        Float: Number,
    }

    expected_type = type_map.get(type(column.type), str)
    if not isinstance(value, expected_type):
        # Attempt to cast if a string
        if isinstance(value, basestring):
            try:
                if expected_type == bool:
                    value = value.lower() in ['true', 'yes', 'on']
                else:
                    value = expected_type(value)
            except:
                raise HTTPBadRequest('Field %s is expected to be %s' % (key, expected_type.__name__))
        else:
            raise HTTPBadRequest('Field %s is expected to be %s' % (key, expected_type.__name__))
    return value


class ConfigController(BaseController):
    """
    Configuration entry point
    """

    @authorize(CONFIG)
    @accept(html_template='/config/index.html')
    def index(self):
        """
        Entry point. Only makes sense with html
        """
        return Session.query(Host).order_by(Host.hostname, Host.service_name).all()

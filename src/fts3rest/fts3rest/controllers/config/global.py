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
from pylons import request

from fts3.model import *
from fts3rest.controllers.config import audit_configuration, validate_type
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify, accept, get_input_as_dict, to_json
from fts3rest.lib.http_exceptions import *
from fts3rest.lib.middleware.fts3auth import authorize
from fts3rest.lib.middleware.fts3auth.constants import *


__controller__ = 'GlobalConfigController'
log = logging.getLogger(__name__)


class GlobalConfigController(BaseController):
    """
    Server-wide configuration
    """

    @doc.response(400, 'Invalid values passed in the request')
    @doc.response(403, 'The user is not allowed to query the configuration')
    @authorize(CONFIG)
    @accept(html_template='/config/global.html')
    def get_global_config(self):
        """
        Get the global configuration
        """
        # Only retry, is bound to VO, the others are global (no VO)
        rows = Session.query(ServerConfig).all()
        result = {'*': ServerConfig()}
        for r in rows:
            if r:
                if r.vo_name in (None, '*'):
                    result['*'] = r
                else:
                    result[r.vo_name] = dict(retry=r.retry)
        return result

    @doc.response(400, 'Invalid values passed in the request')
    @doc.response(403, 'The user is not allowed to query the configuration')
    @authorize(CONFIG)
    @jsonify
    def set_global_config(self):
        """
        Set the global configuration
        """
        cfg = get_input_as_dict(request)

        vo_name = cfg.get('vo_name', '*')
        db_cfg = Session.query(ServerConfig).get(vo_name)
        if not db_cfg:
            db_cfg = ServerConfig(vo_name=vo_name)

        for key, value in cfg.iteritems():
            value = validate_type(ServerConfig, key, value)
            setattr(db_cfg, key, value)

        Session.merge(db_cfg)
        audit_configuration('set-globals', to_json(db_cfg, indent=None))
        try:
            Session.commit()
        except:
            Session.rollback()
            raise

        return self.get_global_config()

    @doc.response(400, 'Invalid values passed in the request')
    @doc.response(403, 'The user is not allowed to query the configuration')
    @authorize(CONFIG)
    @jsonify
    def delete_vo_global_config(self, start_response):
        """
        Delete the global configuration for the given VO
        """
        input_dict = get_input_as_dict(request, from_query=True)
        vo_name = input_dict.get('vo_name')
        if not vo_name or vo_name == '*':
            raise HTTPBadRequest('Missing VO name')

        try:
            Session.query(ServerConfig).filter(ServerConfig.vo_name == vo_name).delete()
            Session.commit()
        except:
            Session.rollback()
            raise

        start_response('204 No Content', [])

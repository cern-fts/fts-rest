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
from fts3rest.lib.helpers import jsonify, accept, get_input_as_dict
from fts3rest.lib.http_exceptions import *
from fts3rest.lib.middleware.fts3auth import authorize
from fts3rest.lib.middleware.fts3auth.constants import *


__controller__ = 'SeConfigurationController'
log = logging.getLogger(__name__)


class SeConfigurationController(BaseController):
    """
    Grid storage configuration
    """

    @doc.response(400, 'Invalid values passed in the request')
    @doc.response(403, 'The user is not allowed to query the configuration')
    @authorize(CONFIG)
    @jsonify
    def set_se_config(self):
        """
        Set the configuration parameters for a given SE
        """
        input_dict = get_input_as_dict(request)

        try:
            for storage, cfg in input_dict.iteritems():
               log.debug("Storage %s" % storage)
               log.debug("cfg %s" % cfg)
               se_info_new = cfg.get('se_info', None)
               log.debug("se_info new %s" %se_info_new)
               if se_info_new:
                se_info = Session.query(ServerConfig).get(storage)
                if not se_info:
                    se_info = ServerConfig(storage=storage)
                log.debug("Se info %s" % se_info)
                for key, value in se_info_new.iteritems():
                    log.debug("key %s" % key)
                    log.debug("value %s" % value)
                    value = validate_type(Se, key, value)
                    log.debug("value %s" % value)
                    setattr(se_info, key, value)
                    
                audit_configuration('set-se-config', 'Set config %s: %s' % (storage, json.dumps(cfg)))
                Session.merge(se_info)
                
                # Operation limits
                operations = cfg.get('operations', None)
                if operations:
                    for vo, limits in operations.iteritems():
                        for op, limit in limits.iteritems():
                            limit = int(limit)
                            new_limit = Session.query(OperationConfig).get((vo, storage, op))
                            if limit > 0:
                                if not new_limit:
                                    new_limit = OperationConfig(
                                        vo_name=vo, host=storage, operation=op
                                    )
                                new_limit.concurrent_ops = limit
                                Session.merge(new_limit)
                            elif new_limit:
                                Session.delete(new_limit)
                    audit_configuration('set-se-limits', 'Set limits for %s: %s' % (storage, json.dumps(operations)))
            Session.commit()
        except (AttributeError, ValueError):
            Session.rollback()
            raise HTTPBadRequest('Malformed configuration')
        except:
            Session.rollback()
            raise
        return None

    @doc.query_arg('se', 'Storage element', required=False)
    @doc.response(403, 'The user is not allowed to query the configuration')
    @authorize(CONFIG)
    @accept(html_template='/config/se.html')
    def get_se_config(self):
        """
        Get the configurations status for a given SE
        """
        se = request.params.get('se', None)
        from_se = Session.query(Se)
        from_ops = Session.query(OperationConfig)
        if se:
            from_se = from_se.filter(Se.storage == se)
            from_ops = from_ops.filter(OperationConfig.host == se)

        # Merge both
        response = dict()
        for opt in from_se:
            se = opt.storage
            config = response.get(se, dict())
            link_config = dict()
            for attr in ['inbound_max_active', 'inbound_max_throughput', 'outbound_max_active', 'outbound_max_throughput', 'udt', 'ipv6', 'se_metadata', 'site', 'debug_level']:
                link_config[attr] = getattr(opt, attr)
                config['se_info'] = link_config
            response[se] = config

        for op in from_ops:
            config = response.get(op.host, dict())
            if 'operations' not in config:
                config['operations'] = dict()
            if op.vo_name not in config['operations']:
                config['operations'][op.vo_name] = dict()
            config['operations'][op.vo_name][op.operation] = op.concurrent_ops
            response[op.host] = config

        return response

    @doc.query_arg('se', 'Storage element', required=True)
    @doc.response(403, 'The user is not allowed to modify the configuration')
    @authorize(CONFIG)
    def delete_se_config(self, start_response):
        """
        Delete the configuration for a given SE
        """
        se = request.params.get('se', None)
        if not se:
            raise HTTPBadRequest('Missing storage (se)')

        try:
            Session.query(Se).filter(Se.storage == se).delete()
            Session.query(OperationConfig).filter(OperationConfig.host == se).delete()
            Session.commit()
        except:
            Session.rollback()
            raise

        start_response('204 No Content', [])
        return ['']

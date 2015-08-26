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
                # As source
                as_source_new = cfg.get('as_source', None)
                if as_source_new:
                    as_source = Session.query(Optimize).filter(Optimize.source_se == storage).first()
                    if not as_source:
                        as_source = Optimize(source_se=storage)
                    for key, value in as_source_new.iteritems():
                        value = validate_type(Optimize, key, value)
                        setattr(as_source, key, value)
                    audit_configuration('set-se-config', 'Set config as source %s: %s' % (storage, json.dumps(cfg)))
                    Session.merge(as_source)
                # As destination
                as_dest_new = cfg.get('as_destination', None)
                if as_dest_new:
                    as_dest = Session.query(Optimize).filter(Optimize.dest_se == storage).first()
                    if not as_dest:
                        as_dest = Optimize(dest_se=storage)
                    for key, value in as_dest_new.iteritems():
                        value = validate_type(Optimize, key, value)
                        setattr(as_dest, key, value)
                    audit_configuration('set-se-config', 'Set config as destination %s: %s' % (storage, json.dumps(cfg)))
                    Session.merge(as_dest)
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
        from_optimize = Session.query(Optimize)
        from_ops = Session.query(OperationConfig)
        if se:
            from_optimize = from_optimize.filter((Optimize.source_se == se) | (Optimize.dest_se == se))
            from_ops = from_ops.filter(OperationConfig.host == se)

        # Merge both
        response = dict()
        for opt in from_optimize:
            se = opt.source_se if opt.source_se else opt.dest_se
            config = response.get(se, dict())
            link_config = dict()
            for attr in ['active', 'throughput', 'udt', 'ipv6']:
                link_config[attr] = getattr(opt, attr)
            if opt.source_se:
                config['as_source'] = link_config
            else:
                config['as_destination'] = link_config
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
            Session.query(Optimize).filter((Optimize.source_se == se) | (Optimize.dest_se == se)).delete()
            Session.query(OperationConfig).filter(OperationConfig.host == se).delete()
            Session.commit()
        except:
            Session.rollback()
            raise

        start_response('204 No Content', [])
        return ['']

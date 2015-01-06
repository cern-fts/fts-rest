#   Copyright notice:
#   Copyright  Members of the EMI Collaboration, 2013.
#
#   See www.eu-emi.eu for details on the copyright holders
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

import json
import logging

from pylons import request
from fts3.model import ConfigAudit, DebugConfig
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.http_exceptions import *
from fts3rest.lib.middleware.fts3auth import authorize
from fts3rest.lib.middleware.fts3auth.constants import *


log = logging.getLogger(__name__)


class ConfigController(BaseController):
    """
    Operations on the config audit
    """

    @doc.return_type(array_of=ConfigAudit)
    @authorize(CONFIG)
    @jsonify
    def audit(self):
        """
        Returns the last 100 entries of the config audit tables
        """
        return Session.query(ConfigAudit).limit(100).all()

    @doc.response(403, 'The user is not allowed to change the configuration')
    @authorize(CONFIG)
    @jsonify
    def set_debug(self):
        """
        Sets the debug level status for a storage
        """
        if request.content_type == 'application/json':
            try:
                input_dict = json.loads(request.body)
            except Exception:
                raise HTTPBadRequest('Malformed input')
        else:
            input_dict = request.params

        source = input_dict.get('source', None)
        destin = input_dict.get('destination', None)
        try:
            level  = int(input_dict.get('level', 1))
        except:
            raise HTTPBadRequest('Invalid parameters')

        if source:
            source = str(source)
            if level:
                src_debug = DebugConfig(
                    source_se=source,
                    dest_se='',
                    debug_level=level
                )
                Session.merge(src_debug)
                log.info('Set debug for source %s to level %d' % (src_debug.source_se, src_debug.debug_level))
            else:
                Session.query(DebugConfig).filter(DebugConfig.source_se == source).delete()
                log.info('Delete debug for source %s' % (source))
        if destin:
            destin = str(destin)
            if level:
                dst_debug = DebugConfig(
                    source_se='',
                    dest_se=destin,
                    debug_level=level
                )
                Session.merge(dst_debug)
                log.info('Set debug for destination %s to level %d' % (dst_debug.dest_se, dst_debug.debug_level))
            else:
                Session.query(DebugConfig).filter(DebugConfig.dest_se == destin).delete()
                log.info('Delete debug for destination %s' % (destin))

        try:
            Session.commit()
        except:
            Session.rollback()
            raise
        return input_dict

    @doc.response(403, 'The user is not allowed to change the configuration')
    @authorize(CONFIG)
    def delete_debug(self, start_response):
        """
        Removes a debug entry
        """
        if request.content_type == 'application/json':
            try:
                input_dict = json.loads(request.body)
            except Exception:
                raise HTTPBadRequest('Malformed input')
        else:
            input_dict = request.params

        source = input_dict.get('source', None)
        destin = input_dict.get('destination', None)

        if source:
            source = str(source)
            debug = Session.query(DebugConfig).get((source, ''))
            Session.delete(debug)
            log.info('Delete debug for source %s' % (source))
        if destin:
            destin = str(destin)
            debug = Session.query(DebugConfig).get(('', destin))
            Session.delete(debug)
            log.info('Delete debug for destination %s' % (destin))

        try:
            Session.commit()
        except:
            Session.rollback()
            raise

        start_response('204 No Content', [])
        return ['']

    @doc.response(403, 'The user is not allowed to query the configuration')
    @authorize(CONFIG)
    @jsonify
    def list_debug(self):
        """
        Return the debug settings
        """
        return Session.query(DebugConfig).all()

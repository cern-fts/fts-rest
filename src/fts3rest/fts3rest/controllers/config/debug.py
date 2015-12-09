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
from urlparse import urlparse

from fts3.model import *
from fts3rest.controllers.config import audit_configuration
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify, accept, get_input_as_dict
from fts3rest.lib.http_exceptions import *
from fts3rest.lib.middleware.fts3auth import authorize
from fts3rest.lib.middleware.fts3auth.constants import *


__controller__ = 'DebugConfigController'
log = logging.getLogger(__name__)


class DebugConfigController(BaseController):
    """
    Operations on the config audit
    """

    @doc.response(403, 'The user is not allowed to change the configuration')
    @authorize(CONFIG)
    @jsonify
    def set_debug(self):
        """
        Sets the debug level status for a storage
        """
        input_dict = get_input_as_dict(request)

        source = input_dict.get('source_se', None)
        destin = input_dict.get('dest_se', None)
        try:
            level  = int(input_dict.get('debug_level', 1))
        except:
            raise HTTPBadRequest('Invalid parameters')

        if source:
            source = urlparse(source)
            if not source.scheme or not source.hostname:
                raise HTTPBadRequest('Invalid storage')
            source = "%s://%s" % (source.scheme, source.hostname)

            if level:
                src_debug = DebugConfig(
                    source_se=source,
                    dest_se='',
                    debug_level=level
                )
                Session.merge(src_debug)
                audit_configuration(
                    'debug', 'Set debug for source %s to level %d' % (src_debug.source_se, src_debug.debug_level)
                )
            else:
                Session.query(DebugConfig).filter(DebugConfig.source_se == source).delete()
                audit_configuration(
                    'debug', 'Delete debug for source %s' % (source)
                )
        if destin:
            destin = urlparse(destin)
            if not destin.scheme or not destin.hostname:
                raise HTTPBadRequest('Invalid storage')
            destin = "%s://%s" % (destin.scheme, destin.hostname)

            if level:
                dst_debug = DebugConfig(
                    source_se='',
                    dest_se=destin,
                    debug_level=level
                )
                Session.merge(dst_debug)
                audit_configuration(
                    'debug', 'Set debug for destination %s to level %d' % (dst_debug.dest_se, dst_debug.debug_level)
                )
            else:
                Session.query(DebugConfig).filter(DebugConfig.dest_se == destin).delete()
                audit_configuration('debug', 'Delete debug for destination %s' % (destin))

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
        input_dict = get_input_as_dict(request, from_query=True)

        source = input_dict.get('source_se', None)
        destin = input_dict.get('dest_se', None)

        if source:
            source = str(source)
            debug = Session.query(DebugConfig).get((source, ''))
            if debug:
                Session.delete(debug)
                audit_configuration('debug', 'Delete debug for source %s' % (source))
        if destin:
            destin = str(destin)
            debug = Session.query(DebugConfig).get(('', destin))
            if debug:
                Session.delete(debug)
                audit_configuration('debug', 'Delete debug for destination %s' % (destin))

        try:
            Session.commit()
        except:
            Session.rollback()
            raise

        start_response('204 No Content', [])
        return ['']

    @doc.response(403, 'The user is not allowed to query the configuration')
    @authorize(CONFIG)
    @accept(html_template='/config/debug.html')
    def list_debug(self):
        """
        Return the debug settings
        """
        return Session.query(DebugConfig).all()

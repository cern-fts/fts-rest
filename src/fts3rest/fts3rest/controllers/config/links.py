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


__controller__ = 'LinkConfigController'
log = logging.getLogger(__name__)


class LinkConfigController(BaseController):
    """
    Link configuration
    """

    @doc.response(400, 'Invalid values passed in the request')
    @doc.response(403, 'The user is not allowed to query the configuration')
    @authorize(CONFIG)
    @jsonify
    def set_link_config(self):
        """
        Set the configuration for a given link
        """
        input_dict = get_input_as_dict(request)

        source = input_dict.get('source', '*')
        destination = input_dict.get('destination', '*')
        symbolicname = input_dict.get('symbolicname', None)
        
        if not symbolicname:
            raise HTTPBadRequest('Missing symbolicname')
        if source == '*' and destination == '*':
            raise HTTPBadRequest('Can not use wildcard for both source and destination')
        
        
        link_cfg = Session.query(LinkConfig).filter(LinkConfig.symbolicname == symbolicname).first()
        if not link_cfg:
            link_cfg = LinkConfig(
                source=source,
                destination=destination,
                symbolicname=symbolicname,
            )

        for key, value in input_dict.iteritems():
            value = validate_type(LinkConfig, key, value)
            setattr(link_cfg, key, value)

        audit_configuration('link', json.dumps(input_dict))

        Session.merge(link_cfg)
        try:
            Session.commit()
        except:
            Session.rollback()
            raise

        return link_cfg

    @doc.response(403, 'The user is not allowed to query the configuration')
    @authorize(CONFIG)
    @accept(html_template='/config/links.html')
    def get_all_link_configs(self):
        """
        Get a list of all the links configured
        """
        return Session.query(LinkConfig).all()

    @doc.response(403, 'The user is not allowed to query the configuration')
    @doc.response(404, 'The group or the member does not exist')
    @authorize(CONFIG)
    @jsonify
    def get_link_config(self, sym_name):
        """
        Get the existing configuration for a given link
        """
        link = Session.query(LinkConfig).filter(LinkConfig.symbolicname == sym_name).first()
        if not link:
            raise HTTPNotFound('Link %s does not exist' % sym_name)
        return link

    @doc.response(204, 'Link removed')
    @doc.response(403, 'The user is not allowed to query the configuration')
    @doc.response(404, 'The group or the member does not exist')
    @authorize(CONFIG)
    @jsonify
    def delete_link_config(self, sym_name, start_response):
        """
        Deletes an existing link configuration
        """
        try:
            Session.query(LinkConfig).filter(LinkConfig.symbolicname == sym_name).delete()
            audit_configuration('link-delete', 'Link %s has been deleted' % sym_name)
            Session.commit()
        except:
            Session.rollback()
            raise
        start_response('204 No Content', [])
        return ['']

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
from fts3rest.lib.helpers import jsonify, get_input_as_dict
from fts3rest.lib.http_exceptions import *
from fts3rest.lib.middleware.fts3auth import authorize
from fts3rest.lib.middleware.fts3auth.constants import *


__controller__ = 'VoShareConfigController'
log = logging.getLogger(__name__)


class VoShareConfigController(BaseController):
    """
    VO Share configuration
    """

    @doc.response(403, 'The user is not allowed to modify the configuration')
    @authorize(CONFIG)
    @jsonify
    def set_share(self, start_response):
        """
        Add or modify a share
        """
        input_dict = get_input_as_dict(request)
        source = input_dict.get('source')
        destination = input_dict.get('destination')
        vo = input_dict.get('vo')
        try:
            share = int(input_dict.get('share'))
        except:
            raise HTTPBadRequest('Bad share value')

        if not source or not destination or not vo or not share:
            raise HTTPBadRequest('Missing source, destination, vo and/or share')

        source = urlparse(source)
        if not source.scheme or not source.hostname:
            raise HTTPBadRequest('Invalid source')
        source = "%s://%s" % (source.scheme, source.hostname)

        destination = urlparse(destination)
        if not destination.scheme or not destination.hostname:
            raise HTTPBadRequest('Invalid source')
        destination = "%s://%s" % (destination.scheme, destination.hostname)

        try:
            share_cfg = ShareConfig(
                source=source, destination=destination, vo=vo, share=share
            )
            Session.merge(share_cfg)
            audit_configuration(
                'share-set', 'Share %s, %s, %s has been set to %d' % (source, destination, vo, share)
            )
            Session.commit()
        except:
            Session.rollback()
            raise

        return share

    @doc.response(403, 'The user is not allowed to query the configuration')
    @authorize(CONFIG)
    @jsonify
    def get_shares(self):
        """
        List the existing shares
        """
        return Session.query(ShareConfig).all()

    @doc.response(403, 'The user is not allowed to modify the configuration')
    @authorize(CONFIG)
    @jsonify
    def delete_share(self, start_response):
        """
        Delete a share
        """
        input_dict = get_input_as_dict(request, from_query=True)
        source = input_dict.get('source')
        destination = input_dict.get('destination')
        vo = input_dict.get('vo')

        if not source or not destination or not vo:
            raise HTTPBadRequest('Missing source, destination and/or vo')

        try:
            share = Session.query(ShareConfig).get((source, destination, vo))
            if share:
                Session.delete(share)
                audit_configuration(
                    'share-delete', 'Share %s, %s, %s has been deleted' % (source, destination, vo)
                )
                Session.commit()
        except:
            Session.rollback()
            raise

        start_response('204 No Content', [])
        return ['']

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

try:
    import simplejson as json
except:
    import json
import logging
from pylons import request

from fts3.model import *
from fts3rest.controllers.config import audit_configuration
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify, accept, get_input_as_dict
from fts3rest.lib.http_exceptions import *
from fts3rest.lib.middleware.fts3auth import authorize
from fts3rest.lib.middleware.fts3auth.constants import *


__controller__ = 'ActivitiesConfigController'
log = logging.getLogger(__name__)


def _normalize_activity_share_format(share):
    """
    Convert the input share format to the internally format expected by FTS3
    {"A": 1, "B": 2} => [{"A": 1}, {"B": 2}]
    [{"A": 1}, {"B": 2}] => [{"A": 1}, {"B": 2}]
    """
    if isinstance(share, list):
        return share
    new_share = list()
    for key, value in share.iteritems():
        new_share.append({key: value})
    return new_share


def _new_activity_share_format(share):
    """
    Convert the share from the internal format used by FTS3 to the RESTful one
    [{"A": 1}, {"B": 2}] => {"A": 1, "B": 2}
    """
    new_share = dict()
    for entry in share:
        new_share.update(entry)
    return new_share


class ActivitiesConfigController(BaseController):
    """
    Activity shares configuration
    """

    @doc.response(403, 'The user is not allowed to see the configuration')
    @authorize(CONFIG)
    @accept(html_template='/config/activity_shares.html')
    def get_activity_shares(self):
        """
        Get all activity shares
        """
        response = dict()
        for activity_share in Session.query(ActivityShare):
            response[activity_share.vo] = dict(
                share=_new_activity_share_format(activity_share.activity_share),
                active=activity_share.active
            )
        return response

    @doc.response(403, 'The user is not allowed to see the configuration')
    @authorize(CONFIG)
    @jsonify
    def get_activity_shares_vo(self, vo_name):
        """
        Get activity shares for a given VO
        """
        activity_share = Session.query(ActivityShare).get(vo_name)
        return dict(
            share=_new_activity_share_format(activity_share.activity_share),
            active=activity_share.active
        )

    @doc.response(400, 'Malformed activity share request')
    @doc.response(403, 'The user is not allowed to modify the configuration')
    @authorize(CONFIG)
    @jsonify
    def set_activity_shares(self):
        """
        Set a new/modify an activity share
        """
        input_dict = get_input_as_dict(request)
        if not input_dict.get('vo', None):
            raise HTTPBadRequest('Missing VO')
        if not input_dict.get('share', None):
            raise HTTPBadRequest('Missing share')
        if 'active' not in input_dict:
            input_dict['active'] = True

        input_dict['share'] = _normalize_activity_share_format(input_dict['share'])

        # Make sure the share weights are numbers
        for entry in input_dict['share']:
            for key, value in entry.iteritems():
                if not type(value) in (float, int):
                    raise HTTPBadRequest('Share weight must be a number')

        try:
            activity_share = ActivityShare(
                vo=input_dict['vo'], active=input_dict['active'], activity_share=input_dict['share']
            )

            Session.merge(activity_share)
            audit_configuration('activity-share', json.dumps(input_dict))
            Session.commit()
        except ValueError, e:
            raise HTTPBadRequest(str(e))
        except:
            Session.rollback()
            raise
        return activity_share

    @doc.response(403, 'The user is not allowed to modify the configuration')
    @authorize(CONFIG)
    def delete_activity_shares(self, vo_name, start_response):
        """
        Delete an existing activity share
        """
        activity_share = Session.query(ActivityShare).get(vo_name)
        if activity_share is None:
            raise HTTPNotFound('No activity shares for %s' % vo_name)
        try:
            Session.delete(activity_share)
            audit_configuration('activity-share', 'Activity share removed for "%s"' % (vo_name))
            Session.commit()
        except:
            Session.rollback()
            raise
        start_response('204 No Content', [])
        return ['']

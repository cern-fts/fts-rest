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
from fts3rest.controllers.config import audit_configuration
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify, accept, get_input_as_dict
from fts3rest.lib.http_exceptions import *
from fts3rest.lib.middleware.fts3auth import authorize
from fts3rest.lib.middleware.fts3auth.constants import *


__controller__ = 'SeGroupConfigController'
log = logging.getLogger(__name__)


class SeGroupConfigController(BaseController):
    """
    Storage group configuration
    """

    @doc.response(400, 'Invalid values passed in the request')
    @doc.response(403, 'The user is not allowed to query the configuration')
    @authorize(CONFIG)
    @jsonify
    def add_to_group(self):
        """
        Add a SE to a group
        """
        input_dict = get_input_as_dict(request)

        member = input_dict.get('member', None)
        groupname = input_dict.get('groupname', None)

        if not member or not groupname:
            raise HTTPBadRequest('Missing values')

        # Check the member is in t_se
        if not Session.query(Se).get(member):
            se = Se(storage=member)
            Session.merge(se)

        new_member = Member(groupname=groupname, member=member)
        audit_configuration('member-add', 'Added member %s to %s' % (member, groupname))
        try:
            Session.merge(new_member)
            Session.commit()
        except:
            Session.rollback()
            raise
        return new_member

    @doc.response(403, 'The user is not allowed to query the configuration')
    @authorize(CONFIG)
    @accept(html_template='/config/groups.html')
    def get_all_groups(self):
        """
        Get a list with all group names
        """
        return Session.query(Member).order_by(Member.groupname).all()

    @doc.response(403, 'The user is not allowed to query the configuration')
    @doc.response(404, 'The group does not exist')
    @authorize(CONFIG)
    @jsonify
    def get_group(self, group_name):
        """
        Get the members of a group
        """
        members = Session.query(Member).filter(Member.groupname == group_name).all()
        if len(members) == 0:
            raise HTTPNotFound('Group %s does not exist' % group_name)
        return [m.member for m in members]

    @doc.query_arg('member', 'Storage to remove. All group if left empty or absent', required=False)
    @doc.response(204, 'Member removed')
    @doc.response(403, 'The user is not allowed to query the configuration')
    @doc.response(404, 'The group or the member does not exist')
    @authorize(CONFIG)
    def delete_from_group(self, group_name, start_response):
        """
        Delete a member from a group. If the group is left empty, the group will be removed
        """
        input_dict = get_input_as_dict(request, from_query=True)

        storage = input_dict.get('member', None)
        if storage:
            Session.query(Member).filter((Member.groupname == group_name) & (Member.member == storage)).delete()
            audit_configuration('group-delete', 'Member %s removed from group %s' % (storage, group_name))
        else:
            Session.query(Member).filter(Member.groupname == group_name).delete()
            audit_configuration('group-delete', 'Group %s removed' % group_name)

        try:
            Session.commit()
        except:
            Session.rollback()
            raise

        start_response('204 No Content', [])
        return ['']

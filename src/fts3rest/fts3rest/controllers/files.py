#   Copyright notice:
#   Copyright CERN, 2015.
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

from datetime import datetime, timedelta
from pylons import request
from urlparse import urlparse

try:
    import simplejson as json
except:
    import json
import logging

from fts3.model import File
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.JobBuilder import get_storage_element
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.middleware.fts3auth import authorize
from fts3rest.lib.middleware.fts3auth.constants import *
from fts3rest.lib.http_exceptions import *


log = logging.getLogger(__name__)


class FilesController(BaseController):
    """
    Operations on Files
    """

    @doc.query_arg('vo_name', 'Filter by VO')
    @doc.query_arg('state_in', 'Comma separated list of job states to filter. ACTIVE only by default')
    @doc.query_arg('source_se', 'Source storage element')
    @doc.query_arg('dest_se', 'Destination storage element')
    @doc.query_arg('dest_surl', 'Destination SURL')
    @doc.query_arg('limit', 'Limit the number of results')
    @doc.query_arg('time_window', 'For terminal states, limit results to hours[:minutes] into the past')
    @doc.response(403, 'Operation forbidden')
    @doc.response(400, 'DN and delegation ID do not match')
    @doc.return_type(array_of=File)
    @authorize(TRANSFER)
    @jsonify
    def index(self):
        """
        Get a list of active jobs, or those that match the filter requirements
        """
        user = request.environ['fts3.User.Credentials']

        filter_vo = request.params.get('vo_name', None)
        filter_state = request.params.get('state_in', None)
        filter_source = request.params.get('source_se', None)
        filter_dest = request.params.get('dest_se', None)
        filter_dest_surl = request.params.get('dest_surl', None)

        try:
            filter_limit = max(1, min(int(request.params['limit']), 1000))
        except:
            filter_limit = 1000

        try:
            components = request.params['time_window'].split(':')
            hours = components[0]
            minutes = components[1] if len(components) > 1 else 0
            filter_time = timedelta(hours=int(hours), minutes=int(minutes))
        except:
            filter_time = None

        if filter_dest is None and filter_dest_surl is not None:
            filter_dest = get_storage_element(urlparse(filter_dest_surl))

        # Automatically apply filters depending on granted level
        granted_level = user.get_granted_level_for(TRANSFER)
        if granted_level in (PRIVATE, VO):
            filter_vo = user.vos[0]
        elif granted_level == NONE:
            raise HTTPForbidden('User not allowed to list jobs')

        files = Session.query(File)
        if filter_vo:
            files = files.filter(File.vo_name == filter_vo)
        if filter_state:
            files = files.filter(File.file_state.in_(filter_state.split(',')))
        if filter_source:
            files = files.filter(File.source_se == filter_source)
        if filter_dest:
            files = files.filter(File.dest_se == filter_dest)
        if filter_dest_surl:
            files = files.filter(File.dest_surl == filter_dest_surl)
        if filter_time:
            filter_not_before = datetime.utcnow() - filter_time
            files = files.filter(File.job_finished >= filter_not_before)
        else:
            files = files.filter(File.finish_time == None)

        return files[:filter_limit]

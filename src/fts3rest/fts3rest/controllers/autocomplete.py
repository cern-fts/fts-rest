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

from pylons import request

from fts3.model import Credential, LinkConfig, Job
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.middleware.fts3auth import authorize
from fts3rest.lib.middleware.fts3auth.constants import *


class AutocompleteController(BaseController):
    """
    Autocomplete API
    """

    @doc.query_arg('term', 'Beginning of the DN')
    @authorize(CONFIG)
    @jsonify
    def autocomplete_dn(self):
        """
    	Autocomplete for users' dn
    	"""
        term = request.params.get('term', '/DC=cern.ch')
        matches = Session.query(Credential.dn).filter(Credential.dn.startswith(term)).distinct().all()
        return map(lambda r: r[0], matches)

    @doc.query_arg('term', 'Beginning of the source storage')
    @authorize(CONFIG)
    @jsonify
    def autocomplete_source(self):
        """
        Autocomplete source SE
        """
        term = request.params.get('term', 'srm://')
        matches = Session.query(LinkConfig.source)\
            .filter(LinkConfig.source.startswith(term)).distinct().all()
        return map(lambda r: r[0], matches)

    @doc.query_arg('term', 'Beginning of the destination storage')
    @authorize(CONFIG)
    @jsonify
    def autocomplete_destination(self):
        """
        Autocomplete destination SE
        """
        term = request.params.get('term', 'srm://')
        matches = Session.query(LinkConfig.destination)\
            .filter(LinkConfig.destination.startswith(term)).distinct().all()
        return map(lambda r: r[0], matches)

    @doc.query_arg('term', 'Beginning of the destination storage')
    @authorize(CONFIG)
    @jsonify
    def autocomplete_storage(self):
        """
        Autocomplete a storage, regardless of it being source or destination
        """
        term = request.params.get('term', 'srm://')
        src_matches = Session.query(LinkConfig.source)\
            .filter(LinkConfig.source.startswith(term)).distinct().all()
        dest_matches = Session.query(LinkConfig.destination)\
            .filter(LinkConfig.destination.startswith(term)).distinct().all()

        srcs = map(lambda r: r[0], src_matches)
        dsts = map(lambda r: r[0], dest_matches)

        return set(srcs).union(set(dsts))

    @doc.query_arg('term', 'Beginning of the VO')
    @authorize(CONFIG)
    @jsonify
    def autocomplete_vo(self):
        """
        Autocomplete VO
        """
        term = request.params.get('term', 'srm://')
        matches = Session.query(Job.vo_name)\
            .filter(Job.vo_name.startswith(term)).distinct().all()
        return map(lambda r: r[0], matches)

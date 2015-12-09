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


__controller__ = 'FixConfigController'
log = logging.getLogger(__name__)


class FixConfigController(BaseController):
    """
    Configure fixed limits
    """

    @doc.response(403, 'The user is not allowed to modify the configuration')
    @authorize(CONFIG)
    @jsonify
    def fix_active(self):
        """
        Fixes the number of actives for a pair
        """
        input_dict = get_input_as_dict(request)
        source = input_dict.get('source_se')
        destination = input_dict.get('dest_se')
        try:
            active = int(input_dict.get('active', 0))
        except Exception, e:
            raise HTTPBadRequest('Active must be an integer (%s)' % str(e))

        if not source or not destination:
            raise HTTPBadRequest('Missing source and/or destination')
        if active is None:
            raise HTTPBadRequest('Missing active')

        opt_active = Session.query(OptimizerActive).get((source, destination))
        if not opt_active:
            opt_active = OptimizerActive(
                source_se=source,
                dest_se=destination
            )

        try:
            if active > 0:
                opt_active.active = active
                opt_active.fixed = True
                audit_configuration('fix-active', '%s => %s actives fixed to %s' % (source, destination, active))
            else:
                opt_active.active = 2
                opt_active.fixed = False
                audit_configuration('fix-active', '%s => %s actives unfixed' % (source, destination))
            Session.merge(opt_active)
            Session.commit()
        except:
            Session.rollback()
            raise
        return opt_active

    @doc.response(403, 'The user is not allowed to query the configuration')
    @authorize(CONFIG)
    @accept(html_template='/config/fixed.html')
    def get_fixed_active(self):
        """
        Gets the fixed pairs
        """
        input_dict = get_input_as_dict(request, from_query=True)
        source = input_dict.get('source_se')
        destination = input_dict.get('dest_se')

        fixed = Session.query(OptimizerActive).filter(OptimizerActive.fixed == True)
        if source:
            fixed = fixed.filter(OptimizerActive.source_se == source)
        if destination:
            fixed = fixed.filter(OptimizerActive.dest_se == destination)

        return fixed.all()

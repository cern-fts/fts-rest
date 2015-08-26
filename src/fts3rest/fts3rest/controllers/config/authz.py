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
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify, accept, get_input_as_dict
from fts3rest.lib.http_exceptions import *
from fts3rest.lib.middleware.fts3auth import authorize, require_certificate
from fts3rest.lib.middleware.fts3auth.constants import CONFIG
from fts3rest.controllers.config import audit_configuration


__controller__ = 'AuthzConfigController'
log = logging.getLogger(__name__)


class AuthzConfigController(BaseController):
    """
    Static authorizations
    """

    @doc.response(403, 'The user is not allowed to modify the configuration')
    @require_certificate
    @authorize(CONFIG)
    @jsonify
    def add_authz(self):
        """
        Give special access to someone
        """
        input_dict = get_input_as_dict(request)
        dn = input_dict.get('dn')
        op = input_dict.get('operation')
        if not dn or not op:
            raise HTTPBadRequest('Missing dn and/or operation')

        try:
            authz = Session.query(AuthorizationByDn).get((dn, op))
            if not authz:
                authz = AuthorizationByDn(dn=dn, operation=op)
                audit_configuration('authorize', '%s granted to "%s"' % (op, dn))
                Session.merge(authz)
                Session.commit()
        except:
            Session.rollback()
            raise

        return authz

    @doc.query_arg('dn', 'Filter by DN')
    @doc.query_arg('operation', 'Filter by operation')
    @doc.response(403, 'The user is not allowed to query the configuration')
    @require_certificate
    @authorize(CONFIG)
    @accept(html_template='/config/authz.html')
    def list_authz(self):
        """
        List granted accesses
        """
        input_dict = get_input_as_dict(request, from_query=True)
        dn = input_dict.get('dn')
        op = input_dict.get('operation')
        authz = Session.query(AuthorizationByDn)
        if dn:
            authz = authz.filter(AuthorizationByDn.dn == dn)
        if op:
            authz = authz.filter(AuthorizationByDn.operation == op)
        return authz.all()

    @doc.query_arg('dn', 'The user DN to be removed', required=True)
    @doc.query_arg('operation', 'The operation to be removed', required=False)
    @doc.response(403, 'The user is not allowed to modify the configuration')
    @require_certificate
    @authorize(CONFIG)
    def remove_authz(self, start_response):
        """
        Revoke access for a DN for a given operation, or all
        """
        input_dict = get_input_as_dict(request, from_query=True)
        dn = input_dict.get('dn')
        op = input_dict.get('operation')
        if not dn:
            raise HTTPBadRequest('Missing DN parameter')

        to_be_removed = Session.query(AuthorizationByDn).filter(AuthorizationByDn.dn == dn)
        if op:
            to_be_removed = to_be_removed.filter(AuthorizationByDn.operation == op)

        try:
            to_be_removed.delete()
            if op:
                audit_configuration('revoke', '%s revoked for "%s"' % (op, dn))
            else:
                audit_configuration('revoke', 'All revoked for "%s"' % dn)
            Session.commit()
        except:
            Session.rollback()
            raise

        start_response('204 No Content', [])
        return ['']

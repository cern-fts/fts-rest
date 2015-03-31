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

from fts3.model import AuthorizationByDn
from fts3rest.lib.base import Session
from constants import *
from decorator import decorator
from pylons.controllers.util import abort
import logging
import pylons

log = logging.getLogger(__name__)


def _is_dn_authorized_in_db(user_dn, operation):
    """
    Returns a boolean indicating if user_dn is configured in the database as
    allowed to peform operation
    """
    authz_entry = Session.query(AuthorizationByDn).get((user_dn, operation))
    if authz_entry is not None:
        log.info('%s granted to "%s" because it is configured in the database' % (operation, user_dn))
        return True
    return False


def authorized(operation, resource_owner=None, resource_vo=None, env=None):
    """
    Check if the user has enough privileges for a given operation

    Args:
        op:             The operation to perform
        resource_owner: Who owns the resource
        resource_vo:    VO of the owner of the resource
        env:            Environment (i.e. os.environ)

    Returns:
        True if the logged user has enough rights to perform the
        operation 'op' over a resource whose owner is resource_owner:resource_vo
    """
    if env is None:
        env = pylons.request.environ

    if not 'fts3.User.Credentials' in env:
        return False

    user = env['fts3.User.Credentials']
    granted_level = user.get_granted_level_for(operation)

    if granted_level == ALL:
        return True
    elif granted_level == VO:
        return resource_vo is None or user.has_vo(resource_vo)
    elif granted_level == PRIVATE:
        return resource_owner is None or resource_owner == user.user_dn
    else:
        # Give it a last try querying the DB for admin dns
        return _is_dn_authorized_in_db(user.user_dn, operation)


def authorize(op, env=None):
    """
    Decorator to check if the user has enough privileges to perform a given operation

    Args:
        op: The required operation level

    Returns:
        A method that can be used to decorate the resource/method
    """
    @decorator
    def authorize_inner(f, *args, **kwargs):
        if not authorized(op, env=env):
            abort(403, 'Not enough permissions')
        return f(*args, **kwargs)
    return authorize_inner


@decorator
def require_certificate(f, *args, **kwargs):
    """
    If the authentication method is not via certificate, deny access
    """
    user = pylons.request.environ['fts3.User.Credentials']
    if user.method != 'certificate':
        abort(403, 'Certificate required')
    return f(*args, **kwargs)

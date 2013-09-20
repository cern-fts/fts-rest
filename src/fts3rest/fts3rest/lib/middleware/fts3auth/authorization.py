from constants import *
from decorator import decorator
from pylons import request
from pylons.controllers.util import abort
import functools


# Returns True if the logged user has enough rights to perform the
# operation 'op' over a resource whose owner is resource_owner:resource_vo
def authorized(op, resource_owner=None, resource_vo=None, env=None):
    if env is None:
        env = request.environ

    if not 'fts3.User.Credentials' in env:
        return False

    user = env['fts3.User.Credentials']
    grantedLevel = user.getGrantedLevelFor(op)

    if grantedLevel == ALL:
        return True
    elif grantedLevel == VO:
        return resource_vo is None or user.hasVo(resource_vo)
    elif grantedLevel == PRIVATE:
        return resource_owner is None or resource_owner == user.user_dn
    else:
        return False


# The same as before, but it can be used as a decorator instead
def authorize(op, env=None):
    def authorize_inner(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if not authorized(op, env=env):
                abort(403, 'Not enough permissions')
            return f(*args, **kwargs)
        return wrapper
    return authorize_inner

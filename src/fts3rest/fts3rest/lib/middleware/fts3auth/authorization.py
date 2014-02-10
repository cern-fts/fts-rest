from constants import *
from decorator import decorator
from pylons import request
from pylons.controllers.util import abort
import functools


def authorized(op, resource_owner=None, resource_vo=None, env=None):
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


def authorize(op, env=None):
    """
    Decorator to check if the user has enough privileges to perform a given operation
    
    Args:
        op: The required operation level
    
    Returns:
        A method that can be used to decorate the resource/method
    """
    def authorize_inner(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if not authorized(op, env=env):
                abort(403, 'Not enough permissions')
            return f(*args, **kwargs)
        return wrapper
    return authorize_inner

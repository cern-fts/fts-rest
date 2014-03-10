from datetime import datetime
from decorator import decorator
from fts3.model.base import Base
from pylons.decorators.util import get_pylons
from webob.exc import HTTPException
from webob import Response
import json


class ClassEncoder(json.JSONEncoder):

    def __init__(self, *args, **kwargs):
        super(ClassEncoder, self).__init__(*args, **kwargs)
        self.visited = []

    def default(self, obj):
        if isinstance(obj, Base):
            self.visited.append(obj)

        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S%z')
        elif isinstance(obj, Base) or isinstance(obj, object):
            values = {}
            for (k, v) in obj.__dict__.iteritems():
                if not k.startswith('_') and v not in self.visited:
                    values[k] = v
                    if isinstance(v, Base):
                        self.visited.append(v)
            return values
        else:
            return super(ClassEncoder, self).default(obj)


@decorator
def jsonify(f, *args, **kwargs):
    """
    Decorates methods in the controllers, and converts the output to a JSON
    serialization

    Args:
        f:      The method to be called
        args:   Parameters for f
        kwargs: Named parameters for f

    Returns:
        A string with the JSON representation of the value returned by f()
    """
    pylons = get_pylons(args)
    pylons.response.headers['Content-Type'] = 'application/json'

    data = f(*args, **kwargs)
    return [json.dumps(data, cls=ClassEncoder, indent=2, sort_keys=True)]

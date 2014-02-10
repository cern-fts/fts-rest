from datetime import datetime
from decorator import decorator
from fts3.model.base import Base
from pylons.decorators.util import get_pylons
from webob.exc import HTTPException
from webob import Response
import json
import os


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
    pylons = get_pylons(args)
    pylons.response.headers['Content-Type'] = 'application/json'

    try:
        data = f(*args, **kwargs)
        return [json.dumps(data, cls=ClassEncoder, indent=2, sort_keys=True)]
    except HTTPException, e:
        jsonError = {'status': e.status, 'message': e.detail}
        resp = Response(json.dumps(jsonError),
                        status=e.status,
                        content_type='application/json')
        return resp(kwargs['environ'], kwargs['start_response'])

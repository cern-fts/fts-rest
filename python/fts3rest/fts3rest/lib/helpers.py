from datetime import datetime
from decorator import decorator
from fts3.orm.base import Base
from pylons.decorators.util import get_pylons
import json


class ClassEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, Base) or isinstance(obj, object):
			values = {}
			for (k, v) in obj.__dict__.iteritems():
				if not k.startswith('_'):
					if isinstance(v, datetime):
						values[k] = str(v)
					else:
						values[k] = v
			return values
		else:
			return super(ClassEncoder, self).default(obj)


@decorator
def jsonify(f, *args, **kwargs):
	pylons = get_pylons(args)
	pylons.response.headers['Content-Type'] = 'application/json'
	
	data = f(*args, **kwargs)
	
	return json.dumps(data, cls = ClassEncoder, indent = 2, sort_keys = True)
	
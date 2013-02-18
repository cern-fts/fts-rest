from ConfigParser import SafeConfigParser
from datetime import datetime
from decorator import decorator
from fts3.orm.base import Base
from pylons.decorators.util import get_pylons
from StringIO import StringIO
import json


class ClassEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime):
			return obj.strftime('%Y-%m-%dT%H:%M:%S%z')
		elif isinstance(obj, Base) or isinstance(obj, object):
			values = {}
			for (k, v) in obj.__dict__.iteritems():
				if not k.startswith('_'):
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


def fts3_config_load(path = '/etc/fts3/fts3config'):
	# Dirty workaroundpython o: ConfigParser doesn't like files without
	# headers, so fake one (since FTS3 config file doesn't have a
	# default one)
	content = "[DEFAULT]\n" + open(path).read()
	io = StringIO(content)
	
	parser = SafeConfigParser()
	parser.readfp(io)

	dbType = parser.get('DEFAULT', 'DbType')
	dbUser = parser.get('DEFAULT', 'DbUserName')
	dbPass = parser.get('DEFAULT', 'DbPassword')
	dbConn = parser.get('DEFAULT', 'DbConnectString')
	
	fts3cfg = {}
	
	if dbType.lower() == 'mysql':
		fts3cfg['sqlalchemy.url'] = "mysql://%s:%s@%s" % (dbUser, dbPass, dbConn)
	else:
		raise ValueError("Database type '%s' is not recognized" % dbType)
	
	fts3cfg['fts3.Db.Type']             = dbType
	fts3cfg['fts3.Db.Username']         = dbUser
	fts3cfg['fts3.Db.Password']         = dbPass
	fts3cfg['fts3.Db.ConnectionString'] = dbConn
	fts3cfg['fts3.AuthorizedVO']        = parser.get('DEFAULT', 'AuthorizedVO')
	
	return fts3cfg

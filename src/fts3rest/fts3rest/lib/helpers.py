from ConfigParser import SafeConfigParser
from datetime import datetime
from decorator import decorator
from fts3.model.base import Base
from pylons.decorators.util import get_pylons
from StringIO import StringIO
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
        return json.dumps(data, cls=ClassEncoder, indent=2, sort_keys=True)
    except HTTPException, e:
        jsonError = {'status': e.status, 'message': e.detail}
        resp = Response(json.dumps(jsonError),
                        status=e.status,
                        content_type='application/json')
        return resp(kwargs['environ'], kwargs['start_response'])


def fts3_config_load(path='/etc/fts3/fts3config'):
    # Dirty workaroundpython o: ConfigParser doesn't like files without
    # headers, so fake one (since FTS3 config file doesn't have a
    # default one)
    content = "[fts3]\n" + open(path).read()
    io = StringIO(content)

    parser = SafeConfigParser()
    parser.readfp(io)

    dbType = parser.get('fts3', 'DbType')
    dbUser = parser.get('fts3', 'DbUserName')
    dbPass = parser.get('fts3', 'DbPassword')
    dbConn = parser.get('fts3', 'DbConnectString')

    if dbConn[0] == '"' and dbConn[-1] == '"':
        dbConn = dbConn[1:-1]

    fts3cfg = {}

    if dbType.lower() == 'mysql':
        fts3cfg['sqlalchemy.url'] = "mysql://%s:%s@%s" % (dbUser, dbPass,
                                                          dbConn)
    elif dbType.lower() == 'sqlite':
        if not dbConn.startswith('/'):
            dbConn = os.path.abspath(dbConn)
        fts3cfg['sqlalchemy.url'] = "sqlite:///%s" % (dbConn)
    elif dbType.lower() == 'oracle':
        fts3cfg['sqlalchemy.url'] = "oracle://%s:%s@%s" % (dbUser, dbPass,
                                                           dbConn)
    else:
        raise ValueError("Database type '%s' is not recognized" % dbType)

    fts3cfg['fts3.Db.Type']             = dbType
    fts3cfg['fts3.Db.Username']         = dbUser
    fts3cfg['fts3.Db.Password']         = dbPass
    fts3cfg['fts3.Db.ConnectionString'] = dbConn

    authorizedVO = parser.get('fts3', 'AuthorizedVO').split(';')
    fts3cfg['fts3.AuthorizedVO'] = authorizedVO

    fts3cfg['fts3.Roles'] = {}
    for role in parser.options('roles'):
        grantedArray = parser.get('roles', role).split(';')
        for granted in grantedArray:
            (level, operation) = granted.split(':')
            if role not in fts3cfg['fts3.Roles']:
                fts3cfg['fts3.Roles'][role] = {}
            fts3cfg['fts3.Roles'][role][operation] = level

    fts3cfg['fts3.Optimizer'] = parser.getboolean('fts3', 'Optimizer')

    return fts3cfg

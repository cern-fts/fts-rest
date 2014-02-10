from ConfigParser import ConfigParser
from StringIO import StringIO
from urllib import quote_plus


def fts3_config_load(path='/etc/fts3/fts3config'):
    # Dirty workaroundpython o: ConfigParser doesn't like files without
    # headers, so fake one (since FTS3 config file doesn't have a
    # default one)
    content = "[fts3]\n" + open(path).read()
    io = StringIO(content)

    parser = ConfigParser()
    parser.readfp(io)

    dbType = parser.get('fts3', 'DbType')
    dbUser = parser.get('fts3', 'DbUserName')
    dbPass = parser.get('fts3', 'DbPassword')
    dbConn = parser.get('fts3', 'DbConnectString')

    if dbConn[0] == '"' and dbConn[-1] == '"':
        dbConn = dbConn[1:-1]

    fts3cfg = {}

    if dbType.lower() == 'mysql':
        fts3cfg['sqlalchemy.url'] = "mysql://%s:%s@%s" % (dbUser, quote_plus(dbPass),
                                                          dbConn)
    elif dbType.lower() == 'sqlite':
        if not dbConn.startswith('/'):
            dbConn = os.path.abspath(dbConn)
        fts3cfg['sqlalchemy.url'] = "sqlite:///%s" % (dbConn)
    elif dbType.lower() == 'oracle':
        fts3cfg['sqlalchemy.url'] = "oracle://%s:%s@%s" % (dbUser, quote_plus(dbPass),
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

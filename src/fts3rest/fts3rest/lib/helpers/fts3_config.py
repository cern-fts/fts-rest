from ConfigParser import ConfigParser
from StringIO import StringIO
from urllib import quote_plus
import os


def fts3_config_load(path='/etc/fts3/fts3config'):
    """
    Read the configuration from the FTS3 configuration file and
    pass it to the Pylons configuration
    """

    # Dirty workaround: ConfigParser doesn't like files without
    # headers, so fake one (since FTS3 config file doesn't have a
    # default one)
    content = "[fts3]\n" + open(path).read()
    io = StringIO(content)

    parser = ConfigParser()
    parser.readfp(io)

    db_type = parser.get('fts3', 'DbType')
    db_user = parser.get('fts3', 'DbUserName')
    db_pass = parser.get('fts3', 'DbPassword')
    db_conn = parser.get('fts3', 'DbConnectString')

    if db_conn[0] == '"' and db_conn[-1] == '"':
        db_conn = db_conn[1:-1]

    fts3cfg = {}

    if db_type.lower() == 'mysql':
        fts3cfg['sqlalchemy.url'] = "mysql://%s:%s@%s" % (db_user, quote_plus(db_pass),
                                                          db_conn)
    elif db_type.lower() == 'sqlite':
        if not db_conn.startswith('/'):
            db_conn = os.path.abspath(db_conn)
        fts3cfg['sqlalchemy.url'] = "sqlite:///%s" % db_conn
    elif db_type.lower() == 'oracle':
        fts3cfg['sqlalchemy.url'] = "oracle://%s:%s@%s" % (db_user, quote_plus(db_pass),
                                                           db_conn)
    else:
        raise ValueError("Database type '%s' is not recognized" % db_type)

    fts3cfg['fts3.Db.Type']             = db_type
    fts3cfg['fts3.Db.Username']         = db_user
    fts3cfg['fts3.Db.Password']         = db_pass
    fts3cfg['fts3.Db.ConnectionString'] = db_conn

    authorized_vos = parser.get('fts3', 'AuthorizedVO').split(';')
    fts3cfg['fts3.AuthorizedVO'] = authorized_vos

    fts3cfg['fts3.Roles'] = {}
    for role in parser.options('roles'):
        granted_array = parser.get('roles', role).split(';')
        for granted in granted_array:
            (level, operation) = granted.split(':')
            if role not in fts3cfg['fts3.Roles']:
                fts3cfg['fts3.Roles'][role] = {}
            fts3cfg['fts3.Roles'][role][operation] = level

    fts3cfg['fts3.Optimizer'] = parser.getboolean('fts3', 'Optimizer')

    return fts3cfg

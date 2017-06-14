#   Copyright notice:
#   Copyright CERN, 2014.
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
import logging
from sqlalchemy.exc import DisconnectionError
try:
    from MySQLdb.connections import Connection as MySQLConnection
except ImportError:
    MySQLConnection = type(None)
try:
    from cx_Oracle import Connection as OracleConnection, DatabaseError
except ImportError:
    OracleConnection = type(None)
    DatabaseError = Exception


log = logging.getLogger(__name__)


def connection_validator(dbapi_con, con_record, con_proxy):
    exc = None
    if isinstance(dbapi_con, MySQLConnection):
        # True will silently reconnect if the connection was lost
        dbapi_con.ping(True)
    elif isinstance(dbapi_con, OracleConnection):
        try:
            dbapi_con.ping()
        except DatabaseError, e:
            exc = DisconnectionError(str(e))

    if exc is not None:
        log.warning(exc.message)
        raise exc


def connection_set_sqlmode(dbapi_con, con_record):
    cur = dbapi_con.cursor()
    if isinstance(dbapi_con, MySQLConnection):
        cur.execute("SET SESSION sql_mode='STRICT_TRANS_TABLES'")

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
from sqlalchemy.interfaces import PoolListener
from sqlalchemy.exc import DisconnectionError
from MySQLdb.connections import Connection as MySQLConnection
try:
    from cx_Oracle import Connection as OracleConnection, DatabaseError
except:
    OracleConnection = type(None)
    DatabaseError = Exception


log = logging.getLogger(__name__)


class ConnectionValidator(PoolListener):
    """
    Pool listener that validates a connection before using it
    """

    def checkout(self, dbapi_con, con_record, con_proxy):
        exc = None
        if isinstance(dbapi_con, MySQLConnection):
            dbapi_con.ping(True)  # True will silently reconnect if the connection was lost
        elif isinstance(dbapi_con, OracleConnection):
            try:
                dbapi_con.ping()
            except DatabaseError, e:
                exc = DisconnectionError(str(e))

        if exc is not None:
            log.warning(exc.message)
            raise exc

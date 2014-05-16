#   Copyright notice:
#   Copyright  Members of the EMI Collaboration, 2010.
# 
#   See www.eu-emi.eu for details on the copyright holders
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

from sqlalchemy.interfaces import ConnectionProxy


class QueryCounter(ConnectionProxy):
    """
    Implementation of ConnectionProxy that counts the number of query types
    executed by SqlAlchemy
    """

    def __init__(self):
        ConnectionProxy.__init__(self)
        self.count = {}

    def _increment(self, key):
        if key not in self.count:
            self.count[key] = 1
        else:
            self.count[key] += 1

    def __iter__(self):
        return self.count.iteritems()

    def execute(self, conn, execute, clauseelement, *multiparams, **params):
        action = str(clauseelement).split()[0]
        self._increment(action)
        return execute(clauseelement, *multiparams, **params)

    def commit(self, conn, commit):
        self._increment("COMMIT")
        return commit()

    def commit_twophase(self, conn, commit_twophase, xid, is_prepared):
        self._increment("COMMIT2")
        return commit_twophase(xid, is_prepared)

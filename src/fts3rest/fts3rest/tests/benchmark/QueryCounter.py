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

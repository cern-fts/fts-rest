

class FTS3ClientException(Exception):
    pass


class BadEndpoint(FTS3ClientException):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return "Bad endpoint: %s" % self.reason


class Unauthorized(FTS3ClientException):
    def __str__(self):
        return "Unauthorized"


class ClientError(FTS3ClientException):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return "Client error: %s" % self.reason


class NeedDelegation(ClientError):
    def __str__(self):
        return "Need to delegate credentials"


class FailedDependency(ClientError):
    def __str__(self):
        return "Failed dependency"


class ServerError(FTS3ClientException):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return "Server error: %s" % self.reason


class TryAgain(ServerError):
    def __str__(self):
        return "Try again: %s" % self.reason


class NotFound(FTS3ClientException):
    def __init__(self, resource):
        self.resource = resource

    def __str__(self):
        return "Not found: %s" % self.resource

#   Copyright notice:
#   Copyright  Members of the EMI Collaboration, 2013.
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

class FTS3ClientException(Exception):
    pass


class BadEndpoint(FTS3ClientException):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return "Bad endpoint: %s" % self.reason


class Unauthorized(FTS3ClientException):
    def __init__(self, reason=None):
        self.reason = reason

    def __str__(self):
        if self.reason:
            return "Unauthorized: %s" % self.reason
        else:
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
    def __init__(self, resource, reason=None):
        self.resource = resource
        self.reason = reason

    def __str__(self):
        if self.reason:
            return self.reason
        else:
            return "Not found: %s" % self.resource

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

from banning import Banning
from delegator import Delegator
from jobcanceller import JobCanceller
from joblister import JobLister
from jobshower import JobShower
from jobsubmitter import JobSubmitter
from jobdeletionsubmitter import JobDeletionSubmitter
from serverstatus import ServerStatus
from whoami import WhoAmI
import logging
import sys


class FTS3CliFormatter(logging.Formatter):
    def format(self, record):

        if record.levelno == logging.CRITICAL:
            self._fmt = 'Error: %(msg)s'
        elif record.levelno == logging.WARNING:
            self._fmt = '# Warning: %(msg)s'
        elif record.levelno == logging.DEBUG:
            self._fmt = '# %(msg)s'
        else:
            self._fmt = '%(msg)s'

        return logging.Formatter.format(self, record)


class FTS3CliFilter(object):

    def __init__(self, includes):
        self.includes = includes

    def filter(self, record):
        return record.levelno in self.includes


class FTS3CliFilterExclude(object):

    def __init__(self, excludes):
        self.excludes = excludes

    def filter(self, record):
        return record.levelno not in self.excludes


fmt = FTS3CliFormatter()
stdout_handler = logging.StreamHandler(sys.stdout)
stderr_handler = logging.StreamHandler(sys.stderr)

stdout_handler.setFormatter(fmt)
stdout_handler.addFilter(FTS3CliFilterExclude([logging.WARNING, logging.DEBUG]))
stderr_handler.setFormatter(fmt)
stderr_handler.addFilter(FTS3CliFilter([logging.WARNING, logging.DEBUG]))

logging.root.addHandler(stdout_handler)
logging.root.addHandler(stderr_handler)

logging.root.setLevel(logging.INFO)

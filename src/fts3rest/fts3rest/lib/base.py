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

"""The base Controller API

Provides the BaseController class for subclassing.
"""

import logging
import types
from pylons.controllers import WSGIController
from fts3rest.model.meta import Session

log = logging.getLogger(__name__)


class DestroySessionWhenDone(object):
    """
    Used when returning a generator, so the Session lives longer, but it still
    destroyed when the WSGI server finishes
    """

    def __init__(self, response):
        log.debug('Wrapping response in DestroySessionWhenDone')
        self.response = iter(response)

    def __iter__(self):
        return self

    def next(self):
        try:
            return self.response.next()
        except StopIteration:
            log.debug('Closing database session')
            Session.rollback()  # Needed explicitly. See FTS-443
            Session.remove()
            raise


class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        try:
            response = WSGIController.__call__(self, environ, start_response)
            if isinstance(response, types.GeneratorType):
                response = DestroySessionWhenDone(response)
            else:
                Session.remove()
            return response
        except:
            Session.remove()
            raise

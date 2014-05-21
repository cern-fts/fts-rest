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

import logging
import pylons

log = logging.getLogger('fts3rest')


class RequestLogger(object):
    """
    This middleware wraps the calls and caught error messages, and send
    them to the logger
    """

    def __init__(self, wrap_app, config):
        self.app = wrap_app

    def __call__(self, environ, start_response):
        self._status_msg = None
        def override_start_response(status, headers, exc_info=None):
            start_response(status, headers, exc_info)
            self._status_msg = status

        response = self.app(environ, override_start_response)
        if hasattr(pylons.response, 'detail'):
            self._log_request(environ, self._status_msg, pylons.response.detail)
        else:
            self._log_request(environ, self._status_msg)
        return response

    def _log_request(self, environ, status, message = None):
        url = environ.get('PATH_INFO')
        query = environ.get('QUERY_STRING', None)
        if query:
            url += '?' + query
        method = environ.get('REQUEST_METHOD')
        if environ.get('HTTP_X_FORWARDED_FOR', None):
            remote_addr = environ['HTTP_X_FORWARDED_FOR']
        elif environ.get('REMOTE_ADDR', None):
            remote_addr = environ['REMOTE_ADDR']
        else:
            remote_addr = '?'

        entry = "[From %s] [%s] \"%s %s\"" % (remote_addr, status, method, url)
        if message:
            entry += ' ' + message
        try:
            code = int(status.split()[0])
        except:
            code = 0

        if code >= 400:
            log.error(entry)
            log.debug('Request params: ' + str(pylons.request.params))
            log.debug('Request content type: ' + pylons.request.content_type)
            if pylons.request.content_type == 'application/json':
                log.debug('Request body: ')
                for line in pylons.request.body.split('\n'):
                    log.debug(line)
        else:
            log.info(entry)

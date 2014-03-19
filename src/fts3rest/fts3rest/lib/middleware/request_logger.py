import logging
import pylons

log = logging.getLogger('fts3rest')


class RequestLogger(object):
    """
    This middleware wraps the calls and catched error messages, and send
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
        else:
            log.info(entry)

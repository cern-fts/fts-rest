import json
import pylons
from webob import Response


class ErrorAsJson(object):
    """
    This middleware encodes an error as a json message if json was
    requested in the headers. Otherwise, let the error go and someone else catch it
    """

    def __init__(self, wrap_app, config):
        self.app = wrap_app

    def __call__(self, environ, start_response):
        accept = environ.get('HTTP_ACCEPT', '*/*')
        is_json_accepted = 'application/json' in accept or '*/*' in accept

        self._status_msg = None
        self._status_code = None

        def override_start_response(status, headers, exc_info=None):
            self._status_code = int(status.split()[0])
            if self._status_code >= 400 and is_json_accepted:
                headers = filter(
                    lambda h: h[0].lower() not in ['content-type', 'content-length'],
                    headers
                )
                headers.append(('Content-Type', 'application/json'))
            start_response(status, headers, exc_info)
            self._status_msg = status

        response = self.app(environ, override_start_response)

        if self._status_code >= 400 and is_json_accepted:
            if hasattr(pylons.response, 'detail'):
                err_msg = pylons.response.detail
            else:
                err_msg = ''.join(response)
            json_error = {
                'status': self._status_msg,
                'message': err_msg
            }
            response = [json.dumps(json_error)]
        return response

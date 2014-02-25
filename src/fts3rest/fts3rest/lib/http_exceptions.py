"""
In order to use some non-standard HTTP status code (i.e. 419),
we need to have the exceptions defined
"""
from webob.exc import *

class HTTPAuthenticationTimeout(HTTPClientError):
    code = 419
    title = 'Authentication Timeout'
    explanation = ('The authentication has expired')

status_map[419] = HTTPAuthenticationTimeout

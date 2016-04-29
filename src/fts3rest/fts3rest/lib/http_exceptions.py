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

"""
In order to use some non-standard HTTP status code (i.e. 419),
we need to have the exceptions defined
"""
from webob.exc import *

class HTTPAuthenticationTimeout(HTTPClientError):
    code = 419
    title = 'Authentication Timeout'
    explanation = ('The authentication has expired')

class HTTPMethodFailure(HTTPClientError):
    code = 424
    title = 'Method Failure'
    explanation = ('Method failure')
    
class HTTPConflict(HTTPClientError):
    code = 409
    title = 'Conflict'
    explanation = ('The request could not be completed due to a conflict with the current state of the target resource.')

status_map[419] = HTTPAuthenticationTimeout
status_map[424] = HTTPMethodFailure
status_map[409] = HTTPConflict
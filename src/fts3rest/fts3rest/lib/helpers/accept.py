#   Copyright notice:
#   Copyright CERN, 2015.
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

import pylons

from decorator import decorator
from fts3rest.lib.http_exceptions import *
from fts3rest.lib.helpers.jsonify import to_json
from pylons.templating import render_mako as render
from pylons.controllers.util import redirect


def accept(html_template=None, html_redirect=None, json=True):
    """
    Depending on the Accept headers returns a different representation of the data
    returned by the decorated method
    """
    assert (html_template and not html_redirect) or (not html_template and html_redirect)

    # We give a higher server quality to json, so */* matches it best
    offers = [('text/html', 0.5)]
    if json:
        offers.append(('application/json', 1))

    @decorator
    def accept_inner(f, *args, **kwargs):
        try:
            best_match = pylons.request.accept.best_match(offers, default_match='application/json')
        except:
            best_match = 'application/json'

        if not best_match:
            raise HTTPNotAcceptable('Available: %s' % ', '.join(offers))

        data = f(*args, **kwargs)
        if best_match == 'text/html':
            if html_template:
                return render(html_template, extra_vars={
                    'data': data, 'config': pylons.config, 'user': pylons.request.environ['fts3.User.Credentials']
                })
            else:
                return redirect(html_redirect, code=HTTPSeeOther.code)
        else:
            pylons.response.headers['Content-Type'] = 'application/json'
            return to_json(data)

    return accept_inner

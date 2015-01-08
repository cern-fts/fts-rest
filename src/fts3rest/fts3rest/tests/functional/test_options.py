#   Copyright notice:
#   Copyright CERN, 2014.
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

import json

from fts3rest.tests import TestController


class TestOptions(TestController):
    """
    Tests for the OPTIONS method
    """

    def test_options_whoami(self):
        """
        Test OPTIONS on whoami
        """
        self.setup_gridsite_environment()

        response = self.app.options('/whoami')#, status=200)
        print response.body
        self.assertItemsEqual(['GET', 'OPTIONS'], response.allow)

        response = self.app.options('/whoami/certificate', status=200)
        self.assertItemsEqual(['GET', 'OPTIONS'], response.allow)

    def test_options_ban(self):
        """
        Test OPTIONS on ban urls
        """
        self.setup_gridsite_environment()

        response = self.app.options('/ban/se', status=200)
        self.assertItemsEqual(['POST', 'GET', 'OPTIONS', 'DELETE'], response.allow)

        response = self.app.options('/ban/dn', status=200)
        self.assertItemsEqual(['POST', 'GET', 'OPTIONS', 'DELETE'], response.allow)

    def test_options_dm(self):
        """
        Test OPTIONS on data management urls
        """
        self.setup_gridsite_environment()

        # Methods for modifications
        for path in ['/dm/unlink', '/dm/rename', '/dm/rmdir', '/dm/mkdir']:
            response = self.app.options(path, status=200)
            self.assertItemsEqual(['POST', 'OPTIONS'], response.allow)

        # Methods for querying
        for path in ['/dm/stat', '/dm/list']:
            response = self.app.options(path, status=200)
            self.assertItemsEqual(['GET', 'OPTIONS'], response.allow)

    def test_options_jobs(self):
        """
        Test OPTIONS on job urls
        """
        self.setup_gridsite_environment()

        response = self.app.options('/jobs', status=200)
        self.assertItemsEqual(['GET', 'POST', 'PUT', 'OPTIONS'], response.allow)

        response = self.app.options('/jobs/1234-56789', status=200)
        self.assertItemsEqual(['GET', 'DELETE', 'OPTIONS'], response.allow)

        response = self.app.options('/jobs/1234-56789/files', status=200)
        self.assertItemsEqual(['GET', 'OPTIONS'], response.allow)

    def test_options_delegation(self):
        """
        Test OPTIONS on delegation urls
        """
        self.setup_gridsite_environment()

        response = self.app.options('/delegation', status=200)
        self.assertItemsEqual(['GET', 'OPTIONS'], response.allow)

        response = self.app.options('/delegation/1234', status=200)
        self.assertItemsEqual(['GET', 'DELETE', 'OPTIONS'], response.allow)

        response = self.app.options('/delegation/1234/request', status=200)
        self.assertItemsEqual(['GET', 'OPTIONS'], response.allow)

        response = self.app.options('/delegation/1234/credential', status=200)
        self.assertItemsEqual(['POST', 'PUT', 'OPTIONS'], response.allow)

    def test_options_optimizer(self):
        """
        Test OPTIONS on optimizer urls
        """
        self.setup_gridsite_environment()

        response = self.app.options('/optimizer', status=200)
        self.assertItemsEqual(['GET', 'OPTIONS'], response.allow)

        response = self.app.options('/optimizer/evolution', status=200)
        self.assertItemsEqual(['GET', 'OPTIONS'], response.allow)

    def test_options_snapshot(self):
        """
        Test OPTIONS on snapshot urls
        """
        self.setup_gridsite_environment()

        response = self.app.options('/snapshot', status=200)
        self.assertItemsEqual(['GET', 'OPTIONS'], response.allow)

    def test_options_404(self):
        """
        Test OPTIONS on a non-existing url
        """
        self.setup_gridsite_environment()

        self.app.options('/thiswouldreallysurpriseme', status=404)

    def test_entry_point(self):
        """
        Test main entry point
        """
        self.setup_gridsite_environment()

        response = self.app.get('/', status=200)
        json_response = json.loads(response.body)
        self.assertIn('api', json_response)

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

from fts3rest.tests import TestController

class TestAutocomplete(TestController):
    """
    Tests for autocompleting
    """

    def setUp(self):
        self.setup_gridsite_environment()

    def test_autocomplete_dn(self):
        """
        Test autocomplete dn
        """
        autocomp = self.app.get(
            url='/autocomplete/dn',
            params={'user_dn': '/DC=cern', 'message': 'term'},
            status=200
        ).json
        self.assertEqual(0, len(autocomp))

    def test_autocomplete_source(self):
        """
        Test autocomplete source
        """
        autocomp = self.app.get(
            url='/autocomplete/source',
            params={'source': 'srm://', 'message': 'term'},
            status=200
        ).json
        self.assertEqual(0, len(autocomp))

    def test_autocomplete_destination(self):
        """
        Test autocomplete destination
        """
        autocomp = self.app.get(
            url='/autocomplete/destination',
            params={'destination': 'srm://', 'message': 'term'},
            status=200
        ).json
        self.assertEqual(0, len(autocomp))

    def test_autocomplete_storage(self):
        """
        Test autocomplete storage
        """
        autocomp = self.app.get(
            url='/autocomplete/storage',
            params={'storage': 'srm://', 'message': 'term'},
            status=200
        ).json
        self.assertEqual(0, len(autocomp))

    def test_autocomplete_vo(self):
        """
        Test autocomplete vo
        """
        autocomp = self.app.get(
            url='/autocomplete/vo',
            params={'vo': 'srm://', 'message': 'term'},
            status=200
        ).json
        self.assertEqual(0, len(autocomp))

    def test_autocomplete_groupname(self):
        """
        Tests autocomplete groupname
        """
        autocomp = self.app.get(
            url='/autocomplete/groupname',
            params={'groupname': 'group', 'message': 'term'},
            status=200
        ).json
        self.assertEqual(0, len(autocomp))
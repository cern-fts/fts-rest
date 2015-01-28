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
from fts3rest.lib.base import Session
from fts3.model import ConfigAudit, LinkConfig, OptimizerActive


class TestConfigLinks(TestController):

    def setUp(self):
        super(TestConfigLinks, self).setUp()
        self.setup_gridsite_environment()
        Session.query(LinkConfig).delete()
        Session.query(ConfigAudit).delete()
        Session.commit()

    def test_config_link_se(self):
        """
        Set a SE link configuration
        """
        self.app.post_json("/config/links", params={
            'symbolicname': 'test-link',
            'source': 'test.cern.ch',
            'destination': 'test2.cern.ch',
            'state': True,
            'nostreams': 16,
            'tcp_buffer_size': 4096,
            'urlcopy_tx_to': 10,
            'auto_tuning': False
        }, status=200)

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(1, len(audits))

        link = Session.query(LinkConfig).get(('test.cern.ch', 'test2.cern.ch'))
        self.assertEqual('test.cern.ch', link.source)
        self.assertEqual('test2.cern.ch', link.destination)
        self.assertEqual(True, link.state)
        self.assertEqual(16, link.nostreams)
        self.assertEqual(4096, link.tcp_buffer_size)
        self.assertEqual(10, link.urlcopy_tx_to)
        self.assertEqual(False, link.auto_tuning)

    def test_reconfig_link_se(self):
        """
        Reset a SE link configuration
        """
        self.test_config_link_se()
        self.app.post_json("/config/links", params={
            'symbolicname': 'test-link',
            'source': 'test.cern.ch',
            'destination': 'test2.cern.ch',
            'state': True,
            'nostreams': 4,
            'tcp_buffer_size': 1024,
            'urlcopy_tx_to': 5,
            'auto_tuning': True
        }, status=200)

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(2, len(audits))

        link = Session.query(LinkConfig).get(('test.cern.ch', 'test2.cern.ch'))
        self.assertEqual('test.cern.ch', link.source)
        self.assertEqual('test2.cern.ch', link.destination)
        self.assertEqual(True, link.state)
        self.assertEqual(4, link.nostreams)
        self.assertEqual(1024, link.tcp_buffer_size)
        self.assertEqual(5, link.urlcopy_tx_to)
        self.assertEqual(True, link.auto_tuning)


    def test_get_link_list(self):
        """
        Get the list of links configured
        """
        self.test_config_link_se()
        response = self.app.get_json("/config/links")
        links = json.loads(response.body)
        self.assertEqual(1, len(links))
        self.assertEqual('test-link', links[0]['symbolicname'])

    def test_get_link(self):
        """
        Get the configuration for a given link
        """
        self.test_config_link_se()
        response = self.app.get_json("/config/links/test-link")
        link = json.loads(response.body)
        self.assertEqual('test.cern.ch', link['source'])
        self.assertEqual('test2.cern.ch', link['destination'])
        self.assertEqual(True, link['state'])
        self.assertEqual(16, link['nostreams'])
        self.assertEqual(4096, link['tcp_buffer_size'])
        self.assertEqual(10, link['urlcopy_tx_to'])
        self.assertEqual(False, link['auto_tuning'])

    def test_delete_link(self):
        """
        Delete an existing link
        """
        self.test_config_link_se()
        self.app.delete("/config/links/test-link", status=204)

        links = Session.query(LinkConfig).all()
        self.assertEqual(0, len(links))

        self.app.get_json("/config/links/test-link", status=404)

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(2, len(audits))

    def test_set_fixed_active(self):
        """
        Set the fixed number of actives for a pair
        """
        self.app.post_json("/config/fixed", params={
            'source_se': 'test.cern.ch',
            'dest_se': 'test2.cern.ch',
            'active': 5
        }, status=200)

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(1, len(audits))

        opt_active = Session.query(OptimizerActive).get(('test.cern.ch', 'test2.cern.ch'))
        self.assertIsNotNone(opt_active)
        self.assertEqual(5, opt_active.active)
        self.assertEqual(True, opt_active.fixed)

    def test_unset_fixed_active(self):
        """
        Unset the fixed number of actives for a pair
        """
        self.test_set_fixed_active()
        self.app.post_json("/config/fixed", params={
            'source_se': 'test.cern.ch',
            'dest_se': 'test2.cern.ch',
            'active': -1
        }, status=200)

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(2, len(audits))

        opt_active = Session.query(OptimizerActive).get(('test.cern.ch', 'test2.cern.ch'))
        self.assertIsNotNone(opt_active)
        self.assertEqual(2, opt_active.active)
        self.assertEqual(False, opt_active.fixed)

    def test_get_fixed_active(self):
        """
        Get the fixed number of active
        """
        response = self.app.get_json("/config/fixed", status=200)
        pairs = json.loads(response.body)
        self.assertEqual(0, len(pairs))

        self.test_set_fixed_active()

        response = self.app.get_json("/config/fixed", status=200)
        pairs = json.loads(response.body)
        self.assertEqual(1, len(pairs))
        self.assertEqual('test.cern.ch', pairs[0]['source_se'])
        self.assertEqual('test2.cern.ch', pairs[0]['dest_se'])
        self.assertEqual(5, pairs[0]['active'])

        response = self.app.get_json("/config/fixed?source_se=test.cern.ch&dest_se=test2.cern.ch", status=200)
        pairs = json.loads(response.body)
        self.assertEqual(1, len(pairs))
        self.assertEqual('test.cern.ch', pairs[0]['source_se'])
        self.assertEqual('test2.cern.ch', pairs[0]['dest_se'])
        self.assertEqual(5, pairs[0]['active'])

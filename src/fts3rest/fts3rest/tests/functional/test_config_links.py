#   Copyright notice:
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
        resp = self.app.post_json("/config/links", params={
            'symbolicname': 'test-link',
            'source': 'test.cern.ch',
            'destination': 'test2.cern.ch',
            'state': True,
            'nostreams': 16,
            'tcp_buffer_size': 4096,
            'urlcopy_tx_to': 10,
            'auto_tuning': False
        }, status=200).json

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

        self.assertEqual(link.symbolicname, resp['symbolicname'])
        self.assertEqual(link.source, resp['source'])
        self.assertEqual(link.destination, resp['destination'])

    def test_wrong_config_link(self):
        """
        Set wrong config
        """
        self.app.post_json("/config/links", params={
            'symbolicname': None,
            'source': 'test.cern.ch',
            'destination': 'test2.cern.ch',
            'state': True,
            'nostreams': 16,
            'tcp_buffer_size': 4096,
            'urlcopy_tx_to': 10,
            'auto_tuning': False
        }, status=400)

        self.app.post_json("/config/links", params={
            'symbolicname': 'test-link',
            'source': '*',
            'destination': '*',
            'state': True,
            'nostreams': 16,
            'tcp_buffer_size': 4096,
            'urlcopy_tx_to': 10,
            'auto_tuning': False
        }, status=400)

    def test_reconfig_link_se(self):
        """
        Reset a SE link configuration
        """
        self.test_config_link_se()
        resp = self.app.post_json("/config/links", params={
            'symbolicname': 'test-link',
            'source': 'test.cern.ch',
            'destination': 'test2.cern.ch',
            'state': True,
            'nostreams': 4,
            'tcp_buffer_size': 1024,
            'urlcopy_tx_to': 5,
            'auto_tuning': True
        }, status=200).json

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

        self.assertEqual(link.symbolicname, resp['symbolicname'])
        self.assertEqual(link.source, resp['source'])
        self.assertEqual(link.destination, resp['destination'])


    def test_get_link_list(self):
        """
        Get the list of links configured
        """
        self.test_config_link_se()
        links = self.app.get_json("/config/links").json
        self.assertEqual(1, len(links))
        self.assertEqual('test-link', links[0]['symbolicname'])

    def test_get_link(self):
        """
        Get the configuration for a given link
        """
        self.test_config_link_se()
        link = self.app.get_json("/config/links/test-link").json
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
        resp = self.app.post_json("/config/fixed", params={
            'source_se': 'test.cern.ch',
            'dest_se': 'test2.cern.ch',
            'min_active': 5,
            'max_active': 100,
        }, status=200).json

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(1, len(audits))

        opt_active = Session.query(OptimizerActive).get(('test.cern.ch', 'test2.cern.ch'))
        self.assertIsNotNone(opt_active)
        self.assertEqual(5, opt_active.min_active)
        self.assertEqual(100, opt_active.max_active)
        self.assertEqual(5, opt_active.active)
        self.assertEqual(True, opt_active.fixed)

        self.assertEqual(opt_active.source_se, resp['source_se'])
        self.assertEqual(opt_active.dest_se, resp['dest_se'])
        self.assertEqual(opt_active.min_active, resp['min_active'])
        self.assertEqual(opt_active.max_active, resp['max_active'])

    def test_set_fixed_active_no_range(self):
        """
        Set the fixed number of actives for a pair
        """
        resp = self.app.post_json("/config/fixed", params={
            'source_se': 'test.cern.ch',
            'dest_se': 'test2.cern.ch',
            'min_active': 10,
            'max_active': 10,
        }, status=200).json

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(1, len(audits))

        opt_active = Session.query(OptimizerActive).get(('test.cern.ch', 'test2.cern.ch'))
        self.assertIsNotNone(opt_active)
        self.assertEqual(10, opt_active.min_active)
        self.assertEqual(10, opt_active.max_active)
        self.assertEqual(10, opt_active.active)
        self.assertEqual(True, opt_active.fixed)

        self.assertEqual(opt_active.source_se, resp['source_se'])
        self.assertEqual(opt_active.dest_se, resp['dest_se'])
        self.assertEqual(opt_active.min_active, resp['min_active'])
        self.assertEqual(opt_active.max_active, resp['max_active'])

    def test_unset_fixed_active(self):
        """
        Unset the fixed number of actives for a pair
        """
        self.test_set_fixed_active()
        self.app.post_json("/config/fixed", params={
            'source_se': 'test.cern.ch',
            'dest_se': 'test2.cern.ch',
            'min_active': -1
        }, status=200)

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(2, len(audits))

        opt_active = Session.query(OptimizerActive).get(('test.cern.ch', 'test2.cern.ch'))
        self.assertIsNotNone(opt_active)
        self.assertEqual(2, opt_active.min_active)
        self.assertEqual(60, opt_active.max_active)
        self.assertEqual(False, opt_active.fixed)

    def test_get_fixed_active(self):
        """
        Get the fixed number of active
        """
        pairs = self.app.get_json("/config/fixed", status=200).json
        self.assertEqual(0, len(pairs))

        self.test_set_fixed_active()

        pairs = self.app.get_json("/config/fixed", status=200).json
        self.assertEqual(1, len(pairs))
        self.assertEqual('test.cern.ch', pairs[0]['source_se'])
        self.assertEqual('test2.cern.ch', pairs[0]['dest_se'])
        self.assertEqual(5, pairs[0]['min_active'])
        self.assertEqual(100, pairs[0]['max_active'])

        pairs = self.app.get_json("/config/fixed?source_se=test.cern.ch&dest_se=test2.cern.ch", status=200).json
        self.assertEqual(1, len(pairs))
        self.assertEqual('test.cern.ch', pairs[0]['source_se'])
        self.assertEqual('test2.cern.ch', pairs[0]['dest_se'])
        self.assertEqual(5, pairs[0]['min_active'])
        self.assertEqual(100, pairs[0]['max_active'])

    def test_update_fixed_active(self):
        """
        Set fixed, update again.
        Number of actives should be bumped to match the minimum.
        """
        resp = self.app.post_json("/config/fixed", params={
            'source_se': 'test.cern.ch',
            'dest_se': 'test2.cern.ch',
            'min_active': 5,
            'max_active': 100,
        }, status=200).json

        self.assertEqual('test.cern.ch', resp['source_se'])

        resp = self.app.post_json("/config/fixed", params={
            'source_se': 'test.cern.ch',
            'dest_se': 'test2.cern.ch',
            'min_active': 20,
            'max_active': 50,
        }, status=200).json

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(2, len(audits))

        opt_active = Session.query(OptimizerActive).get(('test.cern.ch', 'test2.cern.ch'))
        self.assertIsNotNone(opt_active)
        self.assertEqual(20, opt_active.min_active)
        self.assertEqual(50, opt_active.max_active)
        self.assertEqual(20, opt_active.active)
        self.assertEqual(True, opt_active.fixed)

        self.assertEqual(opt_active.source_se, resp['source_se'])
        self.assertEqual(opt_active.dest_se, resp['dest_se'])
        self.assertEqual(opt_active.min_active, resp['min_active'])
        self.assertEqual(opt_active.max_active, resp['max_active'])

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
from fts3.model import ConfigAudit, LinkConfig


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
            'nostreams': 16,
            'tcp_buffer_size': 4096,
            'min_active': 25,
            'max_active': 150,
            'optimizer_mode': 5
            }, status=200).json

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(1, len(audits))

        link = Session.query(LinkConfig).get(('test.cern.ch', 'test2.cern.ch'))
        self.assertEqual('test.cern.ch', link.source)
        self.assertEqual('test2.cern.ch', link.destination)
        self.assertEqual(16, link.nostreams)
        self.assertEqual(4096, link.tcp_buffer_size)
        self.assertEqual(25, link.min_active)
        self.assertEqual(150, link.max_active)
        self.assertEqual(5, link.optimizer_mode)

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
            'nostreams': 16,
            'tcp_buffer_size': 4096,
            'min_active': 25,
            'max_active': 150,
            'optimizer_mode': 5
        }, status=400)

        self.app.post_json("/config/links", params={
            'symbolicname': 'test-link',
            'source': '*',
            'destination': '*',
            'nostreams': 16,
            'tcp_buffer_size': 4096,
            'min_active': 150,
            'max_active': 25,
            'optimizer_mode': 5
            
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
            'nostreams': 4,
            'tcp_buffer_size': 1024,
            'min_active': 25,
            'max_active': 150,
            'optimizer_mode': 5
            
        }, status=200).json

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(2, len(audits))

        link = Session.query(LinkConfig).get(('test.cern.ch', 'test2.cern.ch'))
        self.assertEqual('test.cern.ch', link.source)
        self.assertEqual('test2.cern.ch', link.destination)
        self.assertEqual(4, link.nostreams)
        self.assertEqual(1024, link.tcp_buffer_size)
        self.assertEqual(25, link.min_active)
        self.assertEqual(150, link.max_active)
        self.assertEqual(5, link.optimizer_mode)

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
        self.assertEqual(16, link['nostreams'])
        self.assertEqual(4096, link['tcp_buffer_size'])
        self.assertEqual(25, link['min_active'])
        self.assertEqual(150, link['max_active'])
        self.assertEqual(5, link['optimizer_mode'])

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

    
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
from fts3.model import ConfigAudit, Optimize, OperationConfig


class TestConfigSe(TestController):

    def setUp(self):
        super(TestConfigSe, self).setUp()
        self.setup_gridsite_environment()
        Session.query(Optimize).delete()
        Session.query(ConfigAudit).delete()
        Session.query(OperationConfig).delete()
        Session.commit()


    def test_set_se_config(self):
        """
        Set SE config
        """
        config = {
            'test.cern.ch': {
                'operations': {
                    'atlas': {
                        'delete': 22,
                        'staging': 32,
                    },
                    'dteam': {
                        'delete': 10,
                        'staging': 11
                    }
                },
                'as_source': {
                    'ipv6': True,
                    'active': 55
                },
                'as_destination': {
                    'ipv6': False,
                    'active': 1,
                    'throughput': 33
                }
            }
        }
        self.app.post_json("/config/se",
            params= config,
            status=200
        )

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(3, len(audits))

        ops = Session.query(OperationConfig).filter(OperationConfig.host == 'test.cern.ch').all()
        self.assertEqual(4, len(ops))
        for op in ops:
            self.assertEqual(config[op.host]['operations'][op.vo_name][op.operation], op.concurrent_ops)

        as_source = Session.query(Optimize).filter(Optimize.source_se == 'test.cern.ch').first()
        self.assertIsNotNone(as_source)
        self.assertEqual(True, as_source.ipv6)
        self.assertEqual(55, as_source.active)

        as_dst = Session.query(Optimize).filter(Optimize.dest_se == 'test.cern.ch').first()
        self.assertIsNotNone(as_dst)
        self.assertEqual(False, as_dst.ipv6)
        self.assertEqual(1, as_dst.active)
        self.assertEqual(33, as_dst.throughput)

    def test_reset_se_config(self):
        """
        Reset SE config
        """
        self.test_set_se_config()

        config = {
            'test.cern.ch': {
                'operations': {
                    'atlas': {
                        'delete': 1,
                        'staging': 2,
                    },
                    'dteam': {
                        'delete': 3,
                        'staging': 4
                    }
                },
                'as_source': {
                    'ipv6': False,
                    'active': 88
                },
                'as_destination': {
                    'ipv6': True,
                    'active': 11,
                    'throughput': 10
                }
            }
        }
        self.app.post_json("/config/se",
            params= config,
            status=200
        )

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(6, len(audits))

        ops = Session.query(OperationConfig).filter(OperationConfig.host == 'test.cern.ch').all()
        self.assertEqual(4, len(ops))
        for op in ops:
            self.assertEqual(config[op.host]['operations'][op.vo_name][op.operation], op.concurrent_ops)

        as_source = Session.query(Optimize).filter(Optimize.source_se == 'test.cern.ch').first()
        self.assertIsNotNone(as_source)
        self.assertEqual(False, as_source.ipv6)
        self.assertEqual(88, as_source.active)

        as_dst = Session.query(Optimize).filter(Optimize.dest_se == 'test.cern.ch').first()
        self.assertIsNotNone(as_dst)
        self.assertEqual(True, as_dst.ipv6)
        self.assertEqual(11, as_dst.active)
        self.assertEqual(10, as_dst.throughput)

    def test_get_se_config(self):
        """
        Get SE config
        """
        self.test_set_se_config()

        cfg = self.app.get_json("/config/se?se=test.cern.ch", status=200).json

        self.assertIn('test.cern.ch', cfg.keys())
        se_cfg = cfg['test.cern.ch']

        self.assertIn('operations', se_cfg.keys())
        self.assertIn('as_source', se_cfg.keys())
        self.assertIn('as_destination', se_cfg.keys())

        self.assertEqual(
            {'atlas': {'delete': 22, 'staging': 32}, 'dteam': {'delete': 10, 'staging': 11}},
            se_cfg['operations']
        )

        self.assertEqual(True, se_cfg['as_source']['ipv6'])
        self.assertEqual(55, se_cfg['as_source']['active'])
        self.assertEqual(False, se_cfg['as_destination']['ipv6'])
        self.assertEqual(1, se_cfg['as_destination']['active'])
        self.assertEqual(33, se_cfg['as_destination']['throughput'])

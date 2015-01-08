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
from fts3.model import ConfigAudit, DebugConfig


class TestDebug(TestController):

    def setUp(self):
        super(TestDebug, self).setUp()
        self.setup_gridsite_environment()
        Session.query(DebugConfig).delete()
        Session.query(ConfigAudit).delete()
        Session.commit()

    def tearDown(self):
        super(TestDebug, self).tearDown()

    def test_set_debug_source(self):
        """
        Set the debug level of a storage as a source
        """
        self.app.post_json(url="/config/debug",
            params = {'source': 'gsiftp://nowhere', 'level': 5},
            status=200
        )

        debug = Session.query(DebugConfig).get(('gsiftp://nowhere', ''))
        self.assertEqual(debug.debug_level, 5)
        self.assertEqual(debug.dest_se, '')
        self.assertEqual(debug.source_se, 'gsiftp://nowhere')

        self.app.delete(url="/config/debug?source=gsiftp://nowhere", status=204)
        debug = Session.query(DebugConfig).get(('gsiftp://nowhere', ''))
        self.assertEqual(None, debug)

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(2, len(audits))

    def test_set_debug_destination(self):
        """
        Set the debug level of a storage as a destination
        """
        self.app.post_json(url="/config/debug",
            params = {'destination': 'gsiftp://nowhere', 'level': 6},
            status=200
        )

        debug = Session.query(DebugConfig).get(('', 'gsiftp://nowhere'))
        self.assertEqual(debug.debug_level, 6)
        self.assertEqual(debug.source_se, '')
        self.assertEqual(debug.dest_se, 'gsiftp://nowhere')

        self.app.delete(url="/config/debug?destination=gsiftp://nowhere", status=204)
        debug = Session.query(DebugConfig).get(('', 'gsiftp://nowhere'))
        self.assertEqual(None, debug)

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(2, len(audits))

    def test_set_debug_source_and_dest(self):
        """
        Set the debug level both as source and destination
        """
        self.app.post_json(url="/config/debug",
            params = {'source': 'gsiftp://nowhere', 'level': 5},
            status=200
        )
        self.app.post_json(url="/config/debug",
            params = {'destination': 'gsiftp://nowhere', 'level': 6},
            status=200
        )

        debug = Session.query(DebugConfig).get(('', 'gsiftp://nowhere'))
        self.assertIsNotNone(debug)

        debug = Session.query(DebugConfig).get(('gsiftp://nowhere', ''))
        self.assertIsNotNone(debug)

        self.app.delete(url="/config/debug?destination=gsiftp://nowhere", status=204)

        debug = Session.query(DebugConfig).get(('', 'gsiftp://nowhere'))
        self.assertEqual(None, debug)

        debug = Session.query(DebugConfig).get(('gsiftp://nowhere', ''))
        self.assertIsNotNone(debug)

        self.app.delete(url="/config/debug?source=gsiftp://nowhere", status=204)
        debug = Session.query(DebugConfig).get(('gsiftp://nowhere', ''))
        self.assertEqual(None, debug)

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(4, len(audits))

    def test_set_new_level_source(self):
        """
        Set the debug level, then reset to a new one
        """
        self.app.post_json(url="/config/debug",
            params = {'source': 'gsiftp://nowhere', 'level': 5},
            status=200
        )
        self.app.post_json(url="/config/debug",
            params = {'source': 'gsiftp://nowhere', 'level': 60},
            status=200
        )
        debug = Session.query(DebugConfig).get(('gsiftp://nowhere', ''))
        self.assertEqual(60, debug.debug_level)

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(2, len(audits))

    def test_set_new_level_destination(self):
        """
        Set the debug level, then reset to a new one
        """
        self.app.post_json(url="/config/debug",
            params = {'destination': 'gsiftp://nowhere', 'level': 5},
            status=200
        )
        self.app.post_json(url="/config/debug",
            params = {'destination': 'gsiftp://nowhere', 'level': 60},
            status=200
        )
        debug = Session.query(DebugConfig).get(('', 'gsiftp://nowhere'))
        self.assertEqual(60, debug.debug_level)

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(2, len(audits))

    def test_set_zero_source(self):
        """
        Equivalent to delete
        """
        self.app.post_json(url="/config/debug",
            params = {'source': 'gsiftp://nowhere', 'level': 5},
            status=200
        )
        debug = Session.query(DebugConfig).get(('gsiftp://nowhere', ''))
        self.assertIsNotNone(debug)
        self.app.post_json(url="/config/debug",
            params = {'source': 'gsiftp://nowhere', 'level': 0},
            status=200
        )
        debug = Session.query(DebugConfig).get(('gsiftp://nowhere', ''))
        self.assertEqual(None, debug)

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(2, len(audits))

    def test_set_zero_destination(self):
        """
        Equivalent to delete
        """
        self.app.post_json(url="/config/debug",
            params = {'destination': 'gsiftp://nowhere', 'level': 5},
            status=200
        )
        debug = Session.query(DebugConfig).get(('', 'gsiftp://nowhere'))
        self.assertIsNotNone(debug)
        self.app.post_json(url="/config/debug",
            params = {'destination': 'gsiftp://nowhere', 'level': 0},
            status=200
        )
        debug = Session.query(DebugConfig).get(('', 'gsiftp://nowhere'))
        self.assertEqual(None, debug)

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(2, len(audits))

    def test_debug_list(self):
        """
        Set debug, and then list
        """
        self.app.post_json(url="/config/debug",
            params = {'source': 'gsiftp://nowhere', 'level': 5},
            status=200
        )
        self.app.post_json(url="/config/debug",
            params = {'destination': 'gsiftp://nowhere', 'level': 6},
            status=200
        )

        response = self.app.get(url="/config/debug", status=200)
        debugs = json.loads(response.body)

        self.assertEqual(2, len(debugs))

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(2, len(audits))

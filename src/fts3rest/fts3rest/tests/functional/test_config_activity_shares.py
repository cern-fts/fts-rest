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

from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import ConfigAudit, ActivityShare

class TestConfigActivityShare(TestController):
    """
    Test the configuration of activity shares
    """

    def setUp(self):
        super(TestConfigActivityShare, self).setUp()
        self.setup_gridsite_environment()
        Session.query(ActivityShare).delete()
        Session.query(ConfigAudit).delete()
        Session.commit()

    def test_set_activity_share(self, legacy=False):
        """
        Set a collection of activity shares for a given VO
        """
        self.setup_gridsite_environment()
        if legacy:
            msg = {"vo": "dteam", "active": True, "share": [{"High": 80}, {"Medium": 15}, {"Low": 5}]}
        else:
            msg = {"vo": "dteam", "active": True, "share": {"High": 80, "Medium": 15, "Low": 5}}
        self.app.post_json(url="/config/activity_shares", params=msg, status=200)
        
        activity_share = Session.query(ActivityShare).get("dteam")
        self.assertIsNotNone(activity_share)
        self.assertEqual(activity_share.vo, "dteam")
        self.assertTrue(activity_share.active)
        # Regardless of the submission format, this is what FTS3 expects on the DB
        self.assertEqual(
            activity_share.activity_share,
            [{"High": 80}, {"Medium": 15}, {"Low": 5}]
        )

        audit = Session.query(ConfigAudit).order_by(ConfigAudit.datetime.desc())[0]
        self.assertEqual(audit.action, "activity-share")

    def test_get_all_activity_shares(self, legacy=False):
        """
        Get the activity shares for all vos
        """
        self.test_set_activity_share(legacy)

        shares = self.app.get_json("/config/activity_shares", status=200).json
        self.assertIn("dteam", shares)
        self.assertEqual(shares["dteam"]["share"]["High"], 80)
        self.assertEqual(shares["dteam"]["share"]["Medium"], 15)
        self.assertEqual(shares["dteam"]["share"]["Low"], 5)

    def test_get_vo_activity_shares(self, legacy=False):
        """
        Get the activity shares for a given vo
        """
        self.test_set_activity_share(legacy)
        shares = self.app.get_json("/config/activity_shares/dteam", status=200).json
        self.assertEqual(shares["share"]["High"], 80)
        self.assertEqual(shares["share"]["Medium"], 15)
        self.assertEqual(shares["share"]["Low"], 5)

    def test_modify_activity_share(self, legacy=False):
        """
        Modify the collection of activity shares for a given VO
        """
        self.test_set_activity_share(legacy)
        if legacy:
            msg = {"vo": "dteam", "active": False, "share": [{"A": 1}, {"B": 2}]}
        else:
            msg = {"vo": "dteam", "active": False, "share": {"A": 1, "B": 2}}
        self.app.post_json(url="/config/activity_shares", params=msg, status=200)

        activity_share = Session.query(ActivityShare).get("dteam")
        self.assertEqual(activity_share.vo, "dteam")
        self.assertFalse(activity_share.active)
        # Regardless of the submission format, this is what FTS3 expects on the DB
        self.assertEqual(
            activity_share.activity_share,
            [{"A": 1}, {"B": 2}]
        )

    def test_remove_activity_share(self, legacy=False):
        """
        Remove existing activity shares
        """
        self.test_set_activity_share(legacy)
        self.app.delete(url="/config/activity_shares/dteam", status=204)
        activity_share = Session.query(ActivityShare).get("dteam")
        self.assertIsNone(activity_share)
        self.app.delete(url="/config/activity_shares/xxxx", status=404)
        self.app.delete(url="/config/activity_shares", status=404)

    def test_legacy_activity_share(self, legacy=False):
        """
        All previous tests but using the legacy (gSOAP compatible) syntax:
        "{"vo": "dteam", "active": true, "share": [{"High": 80}, {"Medium": 15}, {"Low": 5}]}"
        """
        self.test_set_activity_share(legacy=True)
        self.test_get_all_activity_shares(legacy=True)
        self.test_get_vo_activity_shares(legacy=True)
        self.test_modify_activity_share(legacy=True)
        self.test_remove_activity_share(legacy=True)

    def test_malformed_activity_share(self):
        """
        Submit a malformed share. Must be refused.
        """
        self.setup_gridsite_environment()
        msg =  {"active": False, "share": [{"A": 1}, {"B": 2}]}
        self.app.post_json("/config/activity_shares", params=msg, status=400)
        msg =  {"vo": "dteam", "active": True}
        self.app.post_json("/config/activity_shares", params=msg, status=400)
        msg =  "this has nothing to do"
        self.app.post_json("/config/activity_shares", params=msg, status=400)
        msg = {"vo": "dteam", "active": False, "share": {"A": 1, "B": 'abc'}}
        self.app.post_json("/config/activity_shares", params=msg, status=400)
        msg = {"vo": "dteam", "active": False, "share": [{"A": 1}, {"B": 'abc'}]}
        self.app.post_json("/config/activity_shares", params=msg, status=400)

    def test_activity_shares_unauthorized(self):
        """
        Try to set an activity share not being allowed to configure
        """
        self.setup_gridsite_environment()
        self.test_set_activity_share()
        self.setup_gridsite_environment(no_vo=True)
        msg = {"vo": "dteam", "active": True, "share": {"High": 80, "Medium": 15, "Low": 5}}
        self.app.post_json(url="/config/activity_shares", params=msg, status=403)
        self.app.delete(url="/config/activity_shares/dteam", status=403)
        self.app.get_json(url="/config/activity_shares", status=403)

    def test_activiy_shares_too_long(self):
        """
        Activity share too long
        """
        self.setup_gridsite_environment()
        shares = {}
        for i in range(100):
            shares["activity%d" % i] = i
        msg = {"vo": "dteam", "active": True, "share": shares}
        self.app.post_json(url="/config/activity_shares", params=msg, status=400)

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
from fts3.model.config import ConfigAudit, Member


class TestConfigGroup(TestController):

    def setUp(self):
        super(TestConfigGroup, self).setUp()
        self.setup_gridsite_environment()
        Session.query(Member).delete()
        Session.query(ConfigAudit).delete()
        Session.commit()

    def test_add_member(self):
        """
        Add a member with no group existing
        """
        self.app.post_json("/config/groups",
            params=dict(member='test.cern.ch', groupname='bahbah'),
            status=200
        )

        group = Session.query(Member).filter(Member.groupname == 'bahbah').all()
        self.assertEqual(1, len(group))
        self.assertEqual('test.cern.ch', group[0].member)

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(1, len(audits))

    def test_add_two_members(self):
        """
        Add two members to a group
        """
        self.app.post_json("/config/groups",
            params=dict(member='test.cern.ch', groupname='bahbah'),
            status=200
        )
        self.app.post_json("/config/groups",
            params=dict(member='test2.cern.ch', groupname='bahbah'),
            status=200
        )

        group = Session.query(Member).filter(Member.groupname == 'bahbah').all()
        self.assertEqual(2, len(group))
        self.assertIn('test.cern.ch', [g.member for g in group])
        self.assertIn('test2.cern.ch', [g.member for g in group])

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(2, len(audits))

    def test_remove_member(self):
        """
        Add a member, remove it.
        """
        self.test_add_member()
        self.app.delete("/config/groups/bahbah?member=test.cern.ch", status=204)

        group = Session.query(Member).filter(Member.groupname == 'bahbah').all()
        self.assertEqual(0, len(group))

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(2, len(audits))

    def test_add_two_remove_one(self):
        """
        Add two members, remove one
        """
        self.test_add_two_members()
        self.app.delete("/config/groups/bahbah?member=test.cern.ch", status=204)

        group = Session.query(Member).filter(Member.groupname == 'bahbah').all()
        self.assertEqual(1, len(group))
        self.assertNotIn('test.cern.ch', [g.member for g in group])

    def test_remove_full_group(self):
        """
        Add two, remove full group
        """
        self.test_add_two_members()
        self.app.delete("/config/groups/bahbah", status=204)

        group = Session.query(Member).filter(Member.groupname == 'bahbah').all()
        self.assertEqual(0, len(group))

        audits = Session.query(ConfigAudit).all()
        self.assertEqual(3, len(audits))

    def test_list_groups(self):
        """
        List groups
        """
        self.test_add_two_members()

        group_list = self.app.get_json("/config/groups", status=200).json

        self.assertEqual(2, len(group_list))

    def test_list_members(self):
        """
        List members of a group
        """
        self.test_add_two_members()

        member_list = self.app.get_json("/config/groups/bahbah", status=200).json

        self.assertEqual(2, len(member_list))
        self.assertIn('test.cern.ch', member_list)
        self.assertIn('test2.cern.ch', member_list)

    def test_list_non_existing(self):
        """
        Try to list members of a non existing group
        """
        self.app.get_json("/config/groups/bahbah", status=404)

    def test_add_member_wrong(self):
        """
        Add missing values
        """

        config = {'member': 'test.cern.ch', 'groupname': 'bahbah'}

        for i in config:
            k = config
            k[i] = ''
            print k
            self.app.post(url="/config/groups", params=k, status=400)
            return config

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
import urllib
from insert_job import insert_job

from fts3.model import Job, File
from fts3rest.tests import TestController
from fts3rest.lib.base import Session


def _group_by_triplet(snapshot):
    new_snapshot = dict()

    for triplet_info in snapshot:
        triplet = (
            str(triplet_info['source_se']),
            str(triplet_info['dest_se']),
            str(triplet_info['vo_name'])
        )
        new_snapshot[triplet] = triplet_info

    return new_snapshot


class TestSnapshot(TestController):
    """
    Test the snapshot API
    """

    def setUp(self):
        """
        Insert some registers into the tables
        """
        TestController.setUp(self)
        # Insert some values into the DB
        insert_job('dteam', 'srm://source.se', 'srm://dest.es', 'ACTIVE')
        insert_job('dteam', 'srm://source.se', 'srm://dest.es', 'SUBMITTED')
        insert_job('dteam', 'srm://source.se', 'srm://dest.es', 'SUBMITTED')
        insert_job(
            'dteam', 'srm://source.se', 'srm://dest.es', 'FINISHED', duration=55, queued=10, thr=10
        )
        insert_job(
            'atlas', 'srm://source.se', 'srm://dest.es', 'FINISHED', duration=100, queued=20, thr=100
        )
        insert_job(
            'atlas', 'srm://source.se', 'srm://dest.es', 'FAILED', duration=150, queued=30, thr=200,
            reason='DESTINATION Something something'
        )
        insert_job(
            'atlas', 'gsiftp://source.se', 'gsiftp://dest.es', 'FAILED', duration=5000, queued=0,
            reason='SOURCE Blah'
        )
        insert_job(
            'atlas', 'srm://source.se', 'gsiftp://dest.es', 'FINISHED', duration=100, queued=20, thr=50
        )

    def test_query_all(self):
        """
        Get snapshot information for all pairs and vos
        """
        self.setup_gridsite_environment()
        answer = self.app.get(url="/snapshot", status=200)
        snapshot_raw = json.loads(answer.body)
        snapshot = _group_by_triplet(snapshot_raw)

        self.assertEqual(4, len(snapshot_raw))

        self.assertEqual(1, snapshot[('srm://source.se', 'srm://dest.es', 'dteam')]['active'])
        self.assertEqual(2, snapshot[('srm://source.se', 'srm://dest.es', 'dteam')]['submitted'])
        self.assertEqual(1, snapshot[('srm://source.se', 'srm://dest.es', 'dteam')]['finished'])
        self.assertEqual(0, snapshot[('srm://source.se', 'srm://dest.es', 'dteam')]['failed'])
        self.assertEqual(None, snapshot[('srm://source.se', 'srm://dest.es', 'dteam')]['frequent_error'])
        self.assertEqual(10, snapshot[('srm://source.se', 'srm://dest.es', 'dteam')]['avg_queued'])
        self.assertEqual(10, snapshot[('srm://source.se', 'srm://dest.es', 'dteam')]['avg_throughput']['60'])
        self.assertEqual(1.0, snapshot[('srm://source.se', 'srm://dest.es', 'dteam')]['success_ratio'])

        self.assertEqual(0, snapshot[('srm://source.se', 'srm://dest.es', 'atlas')]['active'])
        self.assertEqual(0, snapshot[('srm://source.se', 'srm://dest.es', 'atlas')]['submitted'])
        self.assertEqual(1, snapshot[('srm://source.se', 'srm://dest.es', 'atlas')]['finished'])
        self.assertEqual(1, snapshot[('srm://source.se', 'srm://dest.es', 'atlas')]['failed'])
        self.assertEqual(1, snapshot[('srm://source.se', 'srm://dest.es', 'atlas')]['frequent_error']['count'])
        self.assertEqual(
            'DESTINATION Something something',
            snapshot[('srm://source.se', 'srm://dest.es', 'atlas')]['frequent_error']['reason']
        )
        # Note that only FINISHED must be count
        self.assertEqual(25, snapshot[('srm://source.se', 'srm://dest.es', 'atlas')]['avg_queued'])
        self.assertEqual(100, snapshot[('srm://source.se', 'srm://dest.es', 'atlas')]['avg_throughput']['30'])
        self.assertEqual(0.5, snapshot[('srm://source.se', 'srm://dest.es', 'atlas')]['success_ratio'])

        self.assertEqual(1, snapshot[('gsiftp://source.se', 'gsiftp://dest.es', 'atlas')]['frequent_error']['count'])
        self.assertEqual(
            'SOURCE Blah', snapshot[('gsiftp://source.se', 'gsiftp://dest.es', 'atlas')]['frequent_error']['reason']
        )

    def test_query_vo(self):
        """
        Get snapshot for one specific VO
        """
        self.setup_gridsite_environment()
        answer = self.app.get(url="/snapshot?vo_name=dteam", status=200)
        snapshot_raw = json.loads(answer.body)
        snapshot = _group_by_triplet(snapshot_raw)

        self.assertEqual(1, len(snapshot_raw))
        self.assertEqual(('srm://source.se', 'srm://dest.es', 'dteam'), snapshot.keys()[0])
        self.assertEqual(1, snapshot[('srm://source.se', 'srm://dest.es', 'dteam')]['active'])
        self.assertEqual(2, snapshot[('srm://source.se', 'srm://dest.es', 'dteam')]['submitted'])
        self.assertEqual(1, snapshot[('srm://source.se', 'srm://dest.es', 'dteam')]['finished'])
        self.assertEqual(None, snapshot[('srm://source.se', 'srm://dest.es', 'dteam')]['frequent_error'])
        self.assertEqual(10, snapshot[('srm://source.se', 'srm://dest.es', 'dteam')]['avg_queued'])
        self.assertEqual(10, snapshot[('srm://source.se', 'srm://dest.es', 'dteam')]['avg_throughput']['5'])
        self.assertEqual(1.0, snapshot[('srm://source.se', 'srm://dest.es', 'dteam')]['success_ratio'])

    def test_query_source(self):
        """
        Snapshot filtering by source only
        """
        self.setup_gridsite_environment()
        answer = self.app.get(url="/snapshot?source_se=%s" % urllib.quote("srm://source.se", ""), status=200)
        snapshot_raw = json.loads(answer.body)
        snapshot = _group_by_triplet(snapshot_raw)

        self.assertEqual(3, len(snapshot_raw))

    def test_query_destination(self):
        """
        Snapshot filtering by destination only
        """
        self.setup_gridsite_environment()
        answer = self.app.get(url="/snapshot?dest_se=%s" % urllib.quote("srm://dest.es", ""), status=200)
        snapshot_raw = json.loads(answer.body)
        snapshot = _group_by_triplet(snapshot_raw)

        self.assertEqual(2, len(snapshot_raw))

    def test_query_pair(self):
        """
        Snapshot filtering by pair
        """
        self.setup_gridsite_environment()
        answer = self.app.get(
            url="/snapshot?source_se=%s&dest_se=%s" % (
                urllib.quote("srm://source.se", ""), urllib.quote("srm://dest.es", "")
            ),
            status=200
        )
        snapshot_raw = json.loads(answer.body)
        snapshot = _group_by_triplet(snapshot_raw)

        self.assertEqual(2, len(snapshot_raw))

    def test_query_triplet(self):
        """
        Snapshot filtering by source, destination and vo
        """
        self.setup_gridsite_environment()
        answer = self.app.get(
            url="/snapshot?source_se=%s&dest_se=%s&vo_name=%s" % (
                urllib.quote("srm://source.se", ""), urllib.quote("srm://dest.es", ""), "atlas"
            ),
            status=200
        )
        snapshot_raw = json.loads(answer.body)
        snapshot = _group_by_triplet(snapshot_raw)

        self.assertEqual(1, len(snapshot_raw))
        self.assertEqual(('srm://source.se', 'srm://dest.es', 'atlas'), snapshot.keys()[0])

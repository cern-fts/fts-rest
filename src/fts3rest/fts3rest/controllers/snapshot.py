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
import itertools
from datetime import datetime, timedelta
from pylons import request
from sqlalchemy import distinct

from fts3.model import Job, File, OptimizerActive, Optimize
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify, misc


def _get_limits(source, destination):
    source_thr = Session.query(Optimize.throughput)\
        .filter(Optimize.source_se == source).filter(Optimize.throughput != None).all()
    dest_thr = Session.query(Optimize.throughput)\
        .filter(Optimize.dest_se == destination).filter(Optimize.throughput != None).all()

    limits = dict()
    if len(source_thr):
        limits['source'] = source_thr[0][0]
    if len(dest_thr):
        limits['destination'] = dest_thr[0][0]

    return limits


class SnapshotController(BaseController):
    """
    Snapshot API
    """

    @doc.query_arg('vo_name', 'Filter by VO name', required=False)
    @doc.query_arg('source_se', 'Filter by source SE', required=False)
    @doc.query_arg('dest_se', 'Filter by destination SE', required=False)
    @jsonify
    def snapshot(self):
        """
        Get the current status of the server
        """
        filter_source = request.params.get('source_se', None)
        filter_dest = request.params.get('dest_se', None)
        filter_vo = request.params.get('vo_name', None)

        if filter_vo:
            vos = [filter_vo]
        else:
            vos = map(lambda r: r[0], Session.query(distinct(File.vo_name)))

        snapshot_list = list()
        not_before = datetime.utcnow() - timedelta(hours=1)
        for vo in vos:
            pairs = Session.query(File.source_se, File.dest_se)\
                .filter(File.vo_name == vo)\
                .distinct()
            if filter_source:
                pairs = pairs.filter(File.source_se == filter_source)
            if filter_dest:
                pairs = pairs.filter(File.dest_se == filter_dest)

            for source, destination in pairs:
                pair_info = dict(vo_name=vo, source_se=source, dest_se=destination)

                # Maximum allowed number of active
                max_active = Session.query(OptimizerActive.active)\
                    .filter(OptimizerActive.source_se == source)\
                    .filter(OptimizerActive.dest_se == destination).all()
                max_active = max_active[0] if len(max_active) else None
                if max_active:
                    pair_info['max_active'] = max_active[0]
                else:
                    pair_info['max_active'] = None

                # Files for this pair+vo
                files = Session.query(
                    File.file_state, File.tx_duration, File.throughput,
                    File.reason, Job.submit_time, File.start_time, File.finish_time, File.file_id
                )\
                    .filter(File.job_id == Job.job_id)\
                    .filter(File.source_se == source)\
                    .filter(File.dest_se == destination)\
                    .filter(File.vo_name == vo)\
                    .filter((File.finish_time >= not_before) | (File.finish_time == None))\
                    .all()

                # Current number of active
                n_active = len(filter(lambda f: f[0] == 'ACTIVE', files))
                pair_info['active'] = n_active

                # Filter finished and failed
                failed = filter(lambda f: f[0] == 'FAILED', files)
                finished = filter(lambda f: f[0] == 'FINISHED', files)

                # Number of queued
                n_queued = sum(map(lambda f: 1 if f[0] == 'SUBMITTED' else 0, files))
                pair_info['submitted'] = n_queued

                # Average queue time
                queued_times = map(
                    # start_time - submit_time
                    lambda f: (f[5] - f[4]),
                    filter(lambda f: f[6] is None and f[5] is not None, files)
                )
                avg_queued = misc.average(queued_times, timedelta(), misc.timedelta_to_seconds)
                pair_info['avg_queued'] = avg_queued

                # Success rate
                n_failed = len(failed)
                n_finished = len(finished)
                n_total = float(n_failed + n_finished)
                if n_total:
                    pair_info['success_ratio'] = n_finished / n_total
                else:
                    pair_info['success_ratio'] = None

                pair_info['finished'] = n_finished
                pair_info['failed'] = n_failed

                # Average throughput for last 60, 30, 15 and 5 minutes
                avg_thr = dict()
                now = datetime.utcnow()
                for minutes in 60, 30, 15, 5:
                    tail = filter(
                        lambda f: f[2] and f[6] is None or f[6] >= now - timedelta(minutes=minutes),
                        finished
                    )
                    avg_thr[str(minutes)] = misc.average(map(lambda f: f[2], tail))
                pair_info['avg_throughput'] = avg_thr

                # Most frequent error
                reasons = map(lambda f: f[3], failed)
                reasons_count = [(reason, len(list(grouped))) for reason, grouped in itertools.groupby(reasons)]
                reasons_count = sorted(reasons_count, key=lambda p: p[1], reverse=True)

                if len(reasons_count) > 0:
                    pair_info['frequent_error'] = dict(
                        count=reasons_count[0][1],
                        reason=reasons_count[0][0]
                    )
                else:
                    pair_info['frequent_error'] = None

                # Limits
                pair_info['limits'] = _get_limits(source, destination)

                snapshot_list.append(pair_info)

        return snapshot_list

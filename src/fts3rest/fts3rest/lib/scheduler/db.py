import urllib
import json
import operator
import logging

from fts3.model import File
from fts3.model import OptimizerEvolution
from fts3.model import ActivityShare

from sqlalchemy import func

from datetime import datetime
from datetime import timedelta

log = logging.getLogger(__name__)


class Database:
    """
    Database class queries information from FTS3 DB using sqlalchemy 
    """

    def __init__(self, session):
        self.session = session

    def get_submitted(self, src, dst, vo):
        """
        Returns the number of submitted files for a given src, dst and vo.
        """
        queue = self.session.query(func.count(File.source_se))\
                                .filter(File.vo_name == vo)\
                                .filter(File.file_state == 'SUBMITTED')\
                                .filter(File.dest_se == dst)\
                                .filter(File.source_se == src)
        submitted = 0 if queue is None else queue[0][0]
        return submitted

    def get_success_rate(self, src, dst):
        """
        Returns the success rate for a given src, dst pair in the last hour
        """
        sum = 0
        arr = self.session.query(OptimizerEvolution.success)\
                          .filter(OptimizerEvolution.source_se == src)\
                          .filter(OptimizerEvolution.dest_se == dst)\
                          .filter(OptimizerEvolution.datetime >= 
                                 (datetime.utcnow() - timedelta(hours=1)))
        size = 0
        for x in arr:
            sum += x[0]
            size += 1
        return 100 if (sum == 0) else (sum / size)

    def get_throughput(self, src, dst):
        """
        Returns the throughput infomation in the last hour for a src, dst pair.
        """
        total_throughput = 0
        size = 0

        for tp, active in self.session.query\
        (OptimizerEvolution.throughput, OptimizerEvolution.active)\
        .filter(OptimizerEvolution.source_se == src)\
        .filter(OptimizerEvolution.dest_se == dst)\
        .filter(OptimizerEvolution.datetime >=
               (datetime.utcnow() - timedelta(hours=1))):
            total_throughput += tp * active
            size += 1

        if size == 0:
            return 0
        else:
            return (total_throughput/size)

    def get_per_file_throughput(self, src, dst):
        """
        Returns the per file throughput info in the last hour for a given src
        dst pair
        """
        throughput = 0
        size = 0

        for per_file_throughput in self.session.query\
        (OptimizerEvolution.throughput)\
        .filter(OptimizerEvolution.source_se == src)\
        .filter(OptimizerEvolution.dest_se == dst)\
        .filter(OptimizerEvolution.datetime >=
               (datetime.utcnow() - timedelta(hours=1))):
            throughput += per_file_throughput[0]
            size += 1

        if size == 0:
            return 0
        else:
            return (throughput/size)

    def get_pending_data(self, src, dst, vo, user_activity):
        """
        Returns the pending data in the queue for a given src dst pair.
        Pending data is aggregated from all activities with priorities >=
        to the user_activity's priority. Only Atlas mentions the ActivityShare.
        """
        share = self.session.query(ActivityShare).get(vo)
        total_pending_data = 0
        if share is None:
            for data in self.session.query(File.user_filesize)\
                                    .filter(File.source_se == src)\
                                    .filter(File.dest_se == dst)\
                                    .filter(File.vo_name == vo)\
                                    .filter(File.file_state == 'SUBMITTED'):
                total_pending_data += data[0]
        else:
            activities = json.loads(share.activity_share)
            for key in activities.keys():
                if activities.get(key) >= activities.get(user_activity):
                    for data in self.session.query(File.user_filesize)\
                                     .filter(File.source_se == src)\
                                     .filter(File.dest_se == dst)\
                                     .filter(File.vo_name == vo)\
                                     .filter(File.activity == key)\
                                     .filter(File.file_state == 'SUBMITTED'):
                        total_pending_data += data[0]

        return total_pending_data

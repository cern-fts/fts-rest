import operator
import logging

log = logging.getLogger(__name__)


class Scheduler:
    """
    The scheduler class is used to rank the source sites based on a number 
    of factors e.g queued files, success rate etc. 

    If the throughput is 0 for a given src dst pair, we should select this 
    source site, in this way we can probe the network to get throughput info 
    for future transfers
    """

    def __init__(self, cls):
        """
        cls is the querying mechanism, it can either be a cache or a database
        impelmentation. 

        Using a caching implementation with scheduler:
        queue_provider = Database(Session)
        cache_provider = ThreadLocalCache(queue_provider)
        s = Scheduler (cache_provider)

        Using a direct database implementation with scheduler:
        queue_provider = Database(Session)
        s = Scheduler (queue_provider)
        """
        self.cls = cls

    @staticmethod
    def select_source(source, throughput):
        myList = []
        myList.append((source,throughput))
        return myList

    def rank_submitted(self, sources, dst, vo):
        """
        Ranks the source sites based on the number of pending files
        in the queue
        """
        ranks = []
        for src in sources:
            ranks.append((src, self.cls.get_submitted(src, dst, vo)))
        return sorted(ranks, key=operator.itemgetter(1))

    def rank_success_rate(self, sources, dst):
        """
        Ranks the source sites based on the success rate of the transfers
        in the last 1 hour
        """
        ranks = []
        for src in sources:
            ranks.append((src, self.cls.get_success_rate(src, dst)))
        return sorted(ranks, key=operator.itemgetter(1), reverse=True)

    def rank_throughput(self, sources, dst):
        """
        Ranks the source sites based on the total throughput rate between 
        a source destination pair in the last 1 hour
        """
        ranks = []
        for src in sources:
            throughput = self.cls.get_throughput(src, dst)
            if throughput == 0:
                return Scheduler.select_source(src, throughput)
            ranks.append((src, throughput))
        return sorted(ranks, key=operator.itemgetter(1), reverse=True)

    def rank_per_file_throughput(self, sources, dst):
        """
        Ranks the source sites based on the per file throughput rate between 
        a source destination pair in the last 1 hour
        """
        ranks = []
        for src in sources:
            per_file_throughput = self.cls.get_per_file_throughput(src, dst)
            if per_file_throughput == 0:
                return Scheduler.select_source(src, per_file_throughput)
            ranks.append((src, per_file_throughput))
        return sorted(ranks, key=operator.itemgetter(1), reverse=True)

    def rank_pending_data(self, sources, dst, vo, user_activity):
        """
        Ranks the source sites based on the total pending data in the queue 
        between a source destination pair. Pending data is the aggregated 
        amount of data from all activites with priorities >= to the 
        user_activities's priority
        """
        ranks = []
        for src in sources:
            ranks.append((src, self.cls.get_pending_data(src, dst, vo,
                                                         user_activity)))
        return sorted(ranks, key=operator.itemgetter(1))

    def rank_waiting_time(self, sources, dst, vo, user_activity):
        """
        Ranks the source sites based on the waiting time for the incoming 
        job in the queue
        """
        ranks = []
        for src in sources:
            pending_data = self.cls.get_pending_data(src, dst, vo,
                                                     user_activity)
            throughput = self.cls.get_throughput(src, dst)
            if throughput == 0:
                return Scheduler.select_source(src, throughput)
            waiting_time = pending_data / throughput
            ranks.append((src, waiting_time))
        return sorted(ranks, key=operator.itemgetter(1))

    def rank_waiting_time_with_error(self, sources, dst, vo, user_activity):
        """
        Using the failure rate info, calculate the amount of data that will 
        be resent. Rank based on the waiting time plus the time for resending 
        failed data
        """
        ranks = []
        for src in sources:
            pending_data = self.cls.get_pending_data(src, dst, vo,
                                                     user_activity)
            throughput = self.cls.get_throughput(src, dst)
            if throughput == 0:
                return Scheduler.select_source(src, throughput)
            waiting_time = pending_data / throughput
            failure_rate = 100 - self.cls.get_success_rate(src, dst)
            error = failure_rate * waiting_time / 100
            wait_time_with_error = waiting_time + error
            ranks.append((src, wait_time_with_error))
        return sorted(ranks, key=operator.itemgetter(1))

    def rank_finish_time(self, sources, dst, vo, user_activity,
                         user_file_size):
        """
        Ranks the source sites based on the waiting time with error plus the
        time required to transfer the file
        """
        ranks = []
        for src in sources:
            pending_data = self.cls.get_pending_data(src, dst, vo,
                                                     user_activity)
            throughput = self.cls.get_throughput(src, dst)
            if throughput == 0:
                return Scheduler.select_source(src, throughput)
            waiting_time = pending_data / throughput
            failure_rate = 100 - self.cls.get_success_rate(src, dst)
            error = failure_rate * waiting_time / 100
            wait_time_with_error = waiting_time + error
            file_throughput = self.cls.get_per_file_throughput(src, dst)
            file_transfer_time = (user_file_size/1024/1024) / file_throughput
            finish_time = wait_time_with_error + file_transfer_time
            ranks.append((src, finish_time))
        return sorted(ranks, key=operator.itemgetter(1))

import threading
import hashlib
import logging

from datetime import datetime

log = logging.getLogger(__name__)
threadLocal = threading.local()

class ThreadLocalCache:
    """
    ThreadLocalCache class provides an in memory cache for each thread
    """
    initialized = False
 
    # Run cache clean_cleanup after every 5 mins (1800 secs)
    cache_refresh_time = 1800

    # Expire cache entry after 5 mins (300 secs)
    cache_entry_life = 300
    
    def __init__(self, queue_provider):
        self.queue_provider = queue_provider
        if getattr(threadLocal, 'initialized', None) is None:
            ThreadLocalCache.init_cache()
            threadLocal.initialized = True

    @staticmethod
    def init_cache():
        """
        Maintain a separate cache for submitted, success, throughput etc 
        """
        threadLocal.creation_time = datetime.utcnow() 

        threadLocal.submitted_dict = {}
        threadLocal.success_dict = {}
        threadLocal.throughput_dict = {}
        threadLocal.per_file_throughput_dict = {}
        threadLocal.pending_data_dict = {}

    @staticmethod
    def get_seconds_elapsed(time_diff):
        seconds = (time_diff.days * 86400) + time_diff.seconds
        return seconds
 
    @staticmethod
    def check_expiry(t, entry_life):
        secs = ThreadLocalCache.get_seconds_elapsed(datetime.utcnow() - t)
        return True if secs > entry_life else False

    @staticmethod
    def get_key(*args):
        key = 0
        for x in args:
            key += hash(x)
        return key

    @staticmethod
    def cache_cleanup():
        threadLocal.creation_time = datetime.utcnow()
        
        # Get dictionaries from threadLocal
        dict_list = []
        for attr in dir(threadLocal):
            if attr.endswith("_dict"):
                dict_list.append(getattr(threadLocal, attr, None))

        # Remove expired entries from cache
        for _dict in dict_list:
            for key in _dict.keys():
                if ThreadLocalCache.check_expiry(_dict[key][1],
                                           ThreadLocalCache.cache_entry_life):
                    del _dict[key]
                 
    @staticmethod
    def cache_wrapper(dict_name, func, *args):
        """
        cache_wrapper gets info from cache, in case the cache entry is expired
        or not present in cache, FTS db is queried to update the cache.
        All expired entries from cache are eventually removed after the 
        cache_refresh_time expires 
        """
        val = []
        thread_dict = getattr(threadLocal, dict_name, None)
        key = ThreadLocalCache.get_key(*args)

        if ThreadLocalCache.check_expiry(threadLocal.creation_time,
                                         ThreadLocalCache.cache_refresh_time):
            ThreadLocalCache.cache_cleanup()

        if key not in thread_dict:
            val.append(func(*args))
            val.append(datetime.utcnow())
            thread_dict[key] = val
        else:
            val = thread_dict[key]
            if ThreadLocalCache.check_expiry(val[1],
                                             ThreadLocalCache.cache_entry_life):
                val = []
                val.append(func(*args))
                val.append(datetime.utcnow())
                thread_dict[key] = val
        return val[0]


    def get_submitted(self, src, dst, vo):
        return ThreadLocalCache.cache_wrapper('submitted_dict',
                                             self.queue_provider.get_submitted,
                                             src, dst, vo)

    def get_success_rate(self, src, dst):
        return ThreadLocalCache.cache_wrapper('success_dict',
                                          self.queue_provider.get_success_rate,
                                          src, dst)

    def get_throughput(self, src, dst):
        return ThreadLocalCache.cache_wrapper('throughput_dict',
                                          self.queue_provider.get_throughput,
                                          src, dst)

    def get_per_file_throughput(self, src, dst):
        return ThreadLocalCache.cache_wrapper('per_file_throughput_dict',
                                   self.queue_provider.get_per_file_throughput,
                                   src, dst)

    def get_pending_data(self, src, dst, vo, user_activity):
        return ThreadLocalCache.cache_wrapper('pending_data_dict',
                                        self.queue_provider.get_pending_data,
                                        src, dst, vo, user_activity)

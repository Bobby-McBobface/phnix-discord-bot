import collections
import time

CacheItem = collections.namedtuple("CacheItem", ["time", "data_other", "data_check_same", "data_check_different"])

class RepeatDataError(Exception):
    def __init__(self, data_others, data_check_same, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Save data of failed addition
        self.data_others = data_others
        self.data_check_same = data_check_same


class Cache:
    
    def __init__(self, timeout=60, max_count=3):
        self._cache = collections.deque() # Double-ended queue https://docs.python.org/3/library/collections.html#collections.deque
        self.timeout = timeout
        self.max_count = max_count
    
    def clean_expired(self):
        """Iteratively removes items from left of cache if they are expired"""
        while len(self._cache) != 0 \
          and (time.time() - self._cache[0].time) > self.timeout:
            self._cache.popleft()
    
    def add(self, data_other, data_check_same, data_check_different):
        
        # Clean timed-out entries
        self.clean_expired()
        
        # Check if it follows the rules
        repeat_count = 1
        repeat_checkdiffthings = {data_check_different} # Put current as default
        repeat_data_others = []
        for item in self._cache:
            if item.data_check_same == data_check_same:
                if item.data_check_different not in repeat_checkdiffthings:
                    repeat_checkdiffthings.add(item.data_check_different)
                    repeat_data_others.append(item.data_other)
                    repeat_count += 1
                    if repeat_count == self.max_count:
                        raise RepeatDataError(repeat_data_others, data_check_same)
        
        # Add to cache
        self._cache.append(CacheItem(
            time = time.time(),
            data_other = data_other,
            data_check_same = data_check_same,
            data_check_different = data_check_different
        ))
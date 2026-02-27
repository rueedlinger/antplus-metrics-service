from collections import deque
import time
import threading


from enum import Enum


class MetricsKey(str, Enum):
    POWER = "power"
    SPEED = "speed"
    CADENCE = "cadence"
    DISTANCE = "distance"
    HEART_RATE = "heart_rate"


class TimedMap:
    def __init__(self, ttl=15):
        self.ttl = ttl  # time-to-live in seconds
        self.store = {}
        self.lock = threading.Lock()  # lock for thread safety

    def set(self, key, value):
        if value is None or int(value) <= 0:
            return
        expire_time = time.time() + self.ttl
        with self.lock:
            self.store[key] = (value, expire_time)

    def get(self, key):
        with self.lock:
            if key in self.store:
                value, expire_time = self.store[key]
                if time.time() < expire_time:
                    return value
                else:
                    # Expired, remove entry
                    del self.store[key]
        return None

    def clear_expired(self):
        now = time.time()
        with self.lock:
            keys_to_delete = [k for k, (_, t) in self.store.items() if t <= now]
            for k in keys_to_delete:
                del self.store[k]

    def __repr__(self):
        with self.lock:
            return str({k: v[0] for k, v in self.store.items()})


class TimedMovingAverage:
    def __init__(self, ttl=45):
        self.ttl = ttl
        self.store = {}
        self.lock = threading.Lock()

    def add(self, key, value):
        if value is None or int(value) <= 0:
            return
        now = time.time()
        expire_time = now + self.ttl
        with self.lock:
            if key not in self.store:
                self.store[key] = deque()
            self.store[key].append((expire_time, value))
            self._cleanup_key(key, now)

    def _cleanup_key(self, key, current_time=None):
        if current_time is None:
            current_time = time.time()
        dq = self.store.get(key)
        if dq:
            while dq and dq[0][0] <= current_time:
                dq.popleft()
            if not dq:
                del self.store[key]

    def _cleanup(self):
        now = time.time()
        with self.lock:
            for key in list(self.store.keys()):
                self._cleanup_key(key, now)

    def average(self, key):
        self._cleanup_key(key)
        with self.lock:
            dq = self.store.get(key)
            if not dq:
                return None
            return sum(v for _, v in dq) / len(dq)

    def __repr__(self):
        self._cleanup()
        with self.lock:
            return {k: [v for _, v in dq] for k, dq in self.store.items()}


class CumulativeSumMap:
    def __init__(self, threshold: int = 100):
        self.store = {}
        self.offset = {}
        self.lock = threading.Lock()
        self.threshold = threshold

    def add(self, key, value):
        if value is None or int(value) <= 0:
            return

        with self.lock:
            if key not in self.store:
                self.store[key] = [value]
                # keep first value as offset to simulate a reste to zero
                if value <= self.threshold:
                    self.offset[key] = 0
                else:
                    self.offset[key] = value
                return

            last_value = self.store[key][-1]

            if value < last_value:
                # append if smaller sensor was reset
                self.store[key].append(value)
            elif value > last_value:
                # replace last value if greater
                self.store[key][-1] = value

    def sum(self, key, reset_with_offset=True):
        with self.lock:
            values = self.store.get(key)
            offset = self.offset.get(key)
            if not values:
                return None

            if reset_with_offset:
                return sum(values) - offset

            return sum(values)

    def get_values(self, key):
        with self.lock:
            return list(self.store.get(key, []))

    def clear(self, key=None):
        with self.lock:
            if key is None:
                self.store.clear()
                self.offset.clear()
            else:
                self.store.pop(key, None)
                self.offset.pop(key, None)

    def __repr__(self):
        with self.lock:
            return str(self.store)

import time


class QueueAnalytics:
    """Tracks queue metrics for a single zone in real time.

    Maintains per-ID entry timestamps and computes wait times,
    queue length, and throughput entirely in memory.
    One instance should be created per zone.
    """

    def __init__(self):
        self.active_ids    = set()   # IDs currently inside the zone
        self.entry_times   = {}      # ID -> timestamp when they entered
        self.waiting_times = []      # completed wait durations (seconds)
        self.current_waits = {}      # ID -> elapsed seconds so far

    def update(self, ids_inside_zone):
        """Update state based on the set of IDs present this frame.

        Should be called once per frame after zone membership is determined.
        """
        now = time.time()
        ids_inside_zone = set(ids_inside_zone)

        for id_ in ids_inside_zone - self.active_ids:
            self.entry_times[id_] = now

        for id_ in ids_inside_zone:
            if id_ in self.entry_times:
                self.current_waits[id_] = now - self.entry_times[id_]

        for id_ in self.active_ids - ids_inside_zone:
            enter_time = self.entry_times.pop(id_, None)
            if enter_time:
                self.waiting_times.append(now - enter_time)
            self.current_waits.pop(id_, None)

        self.active_ids = ids_inside_zone

    def queue_length(self):
        """Returns number of people currently in the zone."""
        return len(self.active_ids)

    def average_wait(self):
        """Returns mean wait time of all completed visits in seconds."""
        if not self.waiting_times:
            return 0.0
        return sum(self.waiting_times) / len(self.waiting_times)

    def longest_current_wait(self):
        """Returns the longest ongoing wait among people currently in zone."""
        return max(self.current_waits.values(), default=0.0)

    def total_served(self):
        """Returns total number of people who have exited the zone."""
        return len(self.waiting_times)

import time


# Timer class. A Timer object has 2 methods: start and stop. start - initializes the start time. stop - calculates
# the elapsed time since the start and return the delta
class GameTimer:
    def __init__(self):
        self.start = None

    def start_timer(self):
        self.start = time.perf_counter()

    def stop_timer(self):
        end = time.perf_counter() - self.start
        self.start = None
        return end

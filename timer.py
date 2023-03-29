from time import time


class Timer():
    def __init__(self):
        self.started = False
        self.elasped_time = 0
        self.start_time = 0

    def start(self):
        self.started = True
        self.start_time = time()

    def end(self):
        self.started = False
        return round(time()-self.start_time, 2)

    def is_started(self):
        return self.started

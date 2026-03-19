import pyray as pr
import math

import easings


class InterpolatedValue:
    def __init__(self, value: float, duration: float, func=easings.ease_in_out_quad):
        self.start = value
        self.end = value
        self.duration = duration
        self.func = func

        self.start_time = pr.get_time()

    def get(self):
        now = pr.get_time()
        t = (now - self.start_time) / self.duration
        t = min(max(t, 0), 1)

        return self.start + self.func(t)*(self.end - self.start)

    def set(self, value: float, instant=False, start_at_current=False):
        if instant: self.start = value
        elif start_at_current: self.start = self.get()
        else: self.start = self.end
        self.end = value
        self.start_time = pr.get_time()
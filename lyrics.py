from typing import Any
import pyray as pr
import math

import easings
from i_value import InterpolatedValue
from line import Line


class Lyrics:
    def __init__(self, path: str = None):
        self.font = pr.load_font("jetbrains_mono.ttf")

        self.lines: list[Line] = []
        self.current_line = 0
        self.start_time = pr.get_time() - 30

        self.num_shown_lines = 5
        self.scroll = InterpolatedValue(0, 0.5)

        # self.before_color = (220, 180, 160)
        # self.after_color = (64, 40, 30)
        self.before_color = (160, 100, 80)
        self.after_color = (255, 255, 255)

        if path:
            with open(path, "r") as file:
                self.load(file.read())

    def load_metadata(self, data_type: str, value: Any):
        print(data_type, value)

    def load_line(self, line: str):
        if line.count("[") == 0 or line.count("]") == 0:
            return

        data = line[1:line.index("]")]

        if data.startswith(("id", "ar", "al", "ti", "length")):
            self.load_metadata(
                data.split(":")[0],
                ":".join(data.split(":")[1:])[1:], # length contains ":"
            )
            return

        minute = int(data.split(":")[0])
        second = int(data.split(":")[1].split(".")[0])
        hundredth = int(data.split(":")[1].split(".")[1])

        final_time = (minute * 60) + second + (hundredth / 100)

        self.lines.append(Line(
            final_time,
            line.split("]")[1]
        ))

    def load(self, raw: str):
        for line in raw.split("\n"):
            try:
                self.load_line(line)
            except Exception:
                raise BaseException(f"Couldn't load line: \"{line}\"")

    def set_current_line(self, value: int):
        self.current_line = value
        self.scroll.set(value)

    def update(self):
        now = pr.get_time()

        if self.current_line+1 < len(self.lines):
            if (now - self.start_time) > self.lines[self.current_line+1].time:
                self.set_current_line(self.current_line+1)

    def render(self, screen_size: tuple[int, int]):
        now = pr.get_time()

        for i in range(self.current_line-self.num_shown_lines, self.current_line + self.num_shown_lines):
            if not (0 <= i < len(self.lines)):
                continue

            line = self.lines[i]
            y = int(300 + (i - self.scroll.get()) * 32)

            # current line
            if i == self.current_line:
                pr.draw_rectangle(
                    0, y,
                    screen_size[0], 32,
                    pr.ORANGE
                )

                passed_time = (now - self.start_time) - line.time
                total_duration = self.lines[min(i+1, len(self.lines)-1)].time - self.lines[i].time
                t = passed_time / (total_duration if total_duration else passed_time)
                x = t * len(line.text) * 16

                pr.draw_rectangle(
                    int(x - 5),
                    int(y),
                    10,
                    32,
                    pr.RED
                )

            alpha = 1 - (abs(i - self.scroll.get()) / self.num_shown_lines)
            alpha = easings.ease_out_quart(alpha)
            color = self.before_color if (i - self.scroll.get()) < 0 else self.after_color

            pr.draw_text_ex(
                self.font,
                line.text,
                (0, y),
                32,
                0,
                (
                    color[0],
                    color[1],
                    color[2],
                    int(alpha * 255)
                )
            )
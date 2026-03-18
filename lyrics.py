from typing import Any
import pyray as pr

from line import Line


class Lyrics:
    def __init__(self, path: str = None):
        self.font = pr.load_font("jetbrains_mono.ttf")

        self.lines: list[Line] = []
        self.current_line = 0
        self.start_time = pr.get_time()

        self.num_shown_lines = 5

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

    def update(self):
        now = pr.get_time()

        if self.current_line+1 < len(self.lines):
            if (now - self.start_time) > self.lines[self.current_line+1].time:
                self.current_line += 1

    def render(self, screen_size: tuple[int, int]):
        for i in range(-self.num_shown_lines, self.num_shown_lines):
            if not (0 <= self.current_line+i < len(self.lines)):
                continue

            line = self.lines[self.current_line+i]
            y = 300 + i * 32

            # current line
            if i == 0:
                pr.draw_rectangle(
                    0, y,
                    screen_size[0], 32,
                    pr.ORANGE
                )

            brightness = 1 - (abs(i) / self.num_shown_lines)

            pr.draw_text_ex(
                self.font,
                line.text,
                (0, y),
                32,
                0,
                (
                    int(brightness*255),
                    int(brightness*255),
                    int(brightness*255),
                    255
                )
            )
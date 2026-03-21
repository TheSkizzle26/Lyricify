from typing import Any
import pyray as pr
import math

import easings
from config import Config
from i_value import InterpolatedValue
from line import Line
from palette import Palette


class Lyrics:
    def __init__(self, config: Config, palette: Palette):
        self.config = config
        self.palette = palette

        self.config_num_lines = self.config["num_lines"]
        self.config_font_size = self.config["font_size"]
        self.config_active_scale = self.config["active_scale"]
        self.config_active_rotation = self.config["active_rotation"]
        self.config_max_offset = self.config["max_offset"]

        self.font = pr.load_font_ex(
            "fonts/jetbrains_mono.ttf",
            self.config_font_size,
            None,
            0
        )
        pr.set_texture_filter(
            self.font.texture,
            pr.TextureFilter.TEXTURE_FILTER_TRILINEAR
        )

        self.anchor_pos = (
            self.config["anchor_x"],
            self.config["anchor_y"]
        )

        self.lines: list[Line] = []
        self.current_line = 0
        self.start_time = pr.get_time()

        self.scroll = InterpolatedValue(0, 0.5)

    def reset(self, song_pos: float, instant=False):
        self.start_time = pr.get_time() - song_pos

        line_idx = 0
        for i, line in enumerate(self.lines):
            if line.time < song_pos:
                line_idx = i

        if line_idx < 0:
            line_idx = 0

        if line_idx != self.current_line:
            self.set_current_line(
                line_idx,
                instant=(abs(line_idx - self.current_line) > 3) or instant
            )

    def load_metadata(self, data_type: str, value: Any):
        ...

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
        self.lines = []

        for line in raw.split("\n"):
            try:
                self.load_line(line)
            except Exception:
                raise BaseException(f"Couldn't load line: \"{line}\"")

    def set_current_line(self, value: int, instant=False, start_at_current=True):
        self.current_line = value
        self.scroll.set(value, instant=instant, start_at_current=start_at_current)

    def update(self):
        now = pr.get_time()

        if self.current_line+1 < len(self.lines):
            if (now - self.start_time) > self.lines[self.current_line+1].time:
                self.set_current_line(self.current_line+1)

    def get_str_width(self, text: str, font_size=None):
        return int(pr.measure_text_ex(
            self.font,
            text,
            font_size if font_size else self.config_font_size,
            0
        ).x)

    def clamp(self, x: float, a: float, b: float):
        if x < a: return a
        if x > b: return b
        return x

    def color_lerp(self, color_a: tuple[int, int, int], color_b: tuple[int, int, int], t: float):
        return (
            int(color_a[0] + t*(color_b[0] - color_a[0])),
            int(color_a[1] + t*(color_b[1] - color_a[1])),
            int(color_a[2] + t*(color_b[2] - color_a[2])),
        )

    def color_clamp(self, color: tuple[int, int, int]):
        return (
            min(max(color[0], 0), 255),
            min(max(color[1], 0), 255),
            min(max(color[2], 0), 255),
        )

    def draw_text_centered(self, text: str, center_x: float, center_y: float, font_size: float, rotation: float, tint):
        text_width = self.get_str_width(text, font_size)
        pr.draw_text_pro(
            self.font,
            text,
            (center_x, center_y),
            (
                text_width / 2,
                font_size / 2
            ),
            rotation,
            font_size,
            0,
            tint
        )

    def draw_current_line(self, x: int, y: int, now: float):
        line = self.lines[self.current_line]
        passed_time = (now - self.start_time) - line.time

        next_line_idx = min(self.current_line + 1, len(self.lines) - 1)
        next_line = self.lines[next_line_idx]
        total_duration = next_line.time - line.time

        t = passed_time / (total_duration if total_duration else passed_time)
        t_idx = t * len(line.text)

        char_x = 0
        for char_idx in range(len(line.text)):
            char = line.text[char_idx]
            char_width = self.get_str_width(char)

            lerp = (t_idx - char_idx) * 0.5 + 0.5
            lerp = self.clamp(lerp, 0, 1)
            color = self.color_lerp(
                self.palette.get_text_color_dark(),
                self.palette.get_text_color_light(),
                lerp
            )
            color = self.color_clamp(color)

            effect_offset_t = self.clamp(
                1 - abs(t_idx - char_idx)/2 - 0.5,
                0,
                1
            )
            effect_offset_t = easings.ease_out_quart(effect_offset_t)
            final_size = self.config_font_size + effect_offset_t * self.config_active_scale

            rotation_target = math.sin(char_idx*2 + pr.get_time()*7) * self.config_active_rotation
            rotation = effect_offset_t * rotation_target

            self.draw_text_centered(
                char,
                x + char_x + char_width / 2,
                y + self.config_font_size / 2,
                final_size,
                rotation,
                (
                    int(color[0]),
                    int(color[1]),
                    int(color[2]),
                    255
                )
            )

            char_x += char_width

    def draw_other_line(self, x: int, y: int, i: int):
        line = self.lines[i]

        alpha = 1 - (abs(i - self.scroll.get()) / self.config_num_lines)
        alpha = easings.ease_out_quart(alpha)
        alpha = self.clamp(alpha, 0, 1)
        color = self.palette.get_text_color_light() if (i - self.scroll.get()) < 0 else self.palette.get_text_color_dark()

        pr.draw_text_ex(
            self.font,
            line.text,
            (x, y),
            self.config_font_size,
            0,
            (
                color[0],
                color[1],
                color[2],
                int(alpha * 255)
            )
        )

    def render(self):
        now = pr.get_time()

        for i in range(self.current_line-self.config_num_lines,
                       self.current_line+self.config_num_lines):
            if not (0 <= i < len(self.lines)):
                continue

            x = self.anchor_pos[0] + int(
                math.pow(
                    abs(i - self.scroll.get()) / self.config_num_lines,
                    4
                ) * self.config_max_offset
            )
            y = (self.anchor_pos[1] - self.config_font_size/2) + int(
                (i - self.scroll.get()) * self.config_font_size
            )

            x = max(x, 0)
            y = max(y, 0)

            if i == self.current_line:
                self.draw_current_line(x, y, now)
            else:
                self.draw_other_line(x, y, i)

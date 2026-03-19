import pyray as pr
import sys

import system
from lyrics import Lyrics


class Main:
    def __init__(self):
        self.width, self.height = 1920, 1080
        pr.set_config_flags(
            pr.ConfigFlags.FLAG_FULLSCREEN_MODE
        )
        pr.init_window(self.width, self.height, "Lyricify")
        pr.set_window_monitor(0)
        pr.set_target_fps(144)

        self.system = system.SystemLinux()
        self.lyrics = Lyrics("test_data")

        self.last_sync_time = -999

    def sync(self):
        pos = self.system.get_song_pos()
        self.lyrics.reset(pos)

    def update(self):
        if pr.is_key_pressed(pr.KeyboardKey.KEY_ESCAPE):
            pr.close_window()
            sys.exit()

        now = pr.get_time()

        if now - self.last_sync_time > 1:
            self.last_sync_time = now
            self.sync()

        if pr.is_key_pressed(pr.KeyboardKey.KEY_R):
            self.sync()

        self.lyrics.update()

    def render(self):
        pr.begin_drawing()
        pr.clear_background((
            255,
            90,
            70
        ))

        self.lyrics.render(
            (self.width, self.height)
        )

        pr.end_drawing()

    def run(self):
        while True:
            self.update()
            self.render()

            pr.set_window_title(f"FPS: {pr.get_fps()}")


if __name__ == '__main__':
    Main().run()
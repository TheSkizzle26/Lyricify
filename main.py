import pyray as pr
import sys

from lyrics import Lyrics


class Main:
    def __init__(self):
        self.width, self.height = 800, 600
        pr.init_window(self.width, self.height, "Lyricify")
        pr.set_window_monitor(0)

        self.lyrics = Lyrics("test_data")

    def update(self):
        if pr.is_key_pressed(pr.KeyboardKey.KEY_ESCAPE):
            pr.close_window()
            sys.exit()

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


if __name__ == '__main__':
    Main().run()
import pyray as pr
import sys

import data
import system
from cache import Cache
from gradient import Gradient
from hash import get_song_hash
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
        self.cache = Cache()
        self.data = data.Data()
        self.gradient = Gradient((self.width, self.height))
        self.lyrics = Lyrics()
        self.current_song_name = None

        self.load_data()
        self.sync(instant=True)
        self.last_sync_time = pr.get_time()

    def sync(self, instant=False):
        pos = self.system.get_song_pos()
        self.lyrics.reset(pos, instant=instant)

    def load_data(self):
        name = self.system.get_song_name()
        artists = self.system.get_song_artists()
        album = self.system.get_song_album()
        length = self.system.get_song_length()

        song_hash = get_song_hash(
            name,
            artists,
            album,
            length
        )

        if self.cache.is_cached(song_hash):
            print(f"Using cached: {name}")
            self.lyrics.load(self.cache.get(song_hash))
        else:
            print(f"Loading new: {name}")

            self.data.fetch(
                name,
                album,
                artists,
                length
            )

            self.lyrics.load(self.data.get_lyrics_raw())
            self.cache.store(song_hash, self.data.get_lyrics_raw())

    def update(self):
        if pr.is_key_pressed(pr.KeyboardKey.KEY_ESCAPE):
            pr.close_window()
            sys.exit()

        if pr.is_key_pressed(pr.KeyboardKey.KEY_R):
            self.load_data()
            self.sync()

        now = pr.get_time()

        if now - self.last_sync_time > 1:
            self.last_sync_time = now
            self.sync()

            song_name = self.system.get_song_name()

            if song_name != self.current_song_name:
                self.current_song_name = song_name
                self.load_data()

        self.lyrics.update()

    def render(self):
        pr.begin_drawing()
        # pr.clear_background((
        #     255,
        #     90,
        #     70
        # ))

        self.gradient.render((self.width, self.height))

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
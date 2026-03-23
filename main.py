import os
import pyray as pr
import sys
import platformdirs

import cover
import data
import system
from cache import Cache
from config import Config
from gradient import Gradient
from hash import get_song_hash
from lyrics import Lyrics
from palette import Palette


class Main:
    def __init__(self):
        self.width, self.height = 1920, 1080
        pr.set_config_flags(
            pr.ConfigFlags.FLAG_FULLSCREEN_MODE
        )
        pr.init_window(self.width, self.height, "Lyricify")
        pr.set_window_monitor(0)
        pr.set_target_fps(60)

        self.system = system.SystemLinux()
        self.cache = Cache()
        self.config = Config()
        self.data = data.Data()
        self.palette = Palette(self.config)
        self.gradient = Gradient(self.config, self.palette, (self.width, self.height))
        self.lyrics = Lyrics(self.config, self.palette)
        self.current_song_name = None

        self.gradient_texture = pr.load_render_texture(self.width, self.height)
        self.calculate_palette()

        self.load_data()
        self.sync(instant=True)
        self.last_sync_time = -999

    def find_song_path(self, path: str, name: str):
        for sub_dir in os.listdir(path):
            full_path = f"{path}/{sub_dir}"

            if os.path.isdir(full_path):
                ret = self.find_song_path(full_path, name)
                if len(ret): return ret
            elif sub_dir.endswith((".mp3", ".wav", ".ogg", ".flac")):
                if sub_dir.startswith(name):
                    return full_path

        return ""

    def sync(self, instant=False):
        pos = self.system.get_song_pos()
        self.lyrics.reset(pos, instant=instant)

    def load_data(self):
        name = self.system.get_song_name()
        artists = self.system.get_song_artists()
        album = self.system.get_song_album()
        length = self.system.get_song_length()

        if not name or name == "":
            return

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

        self.sync(instant=True)

    def sync_interval(self, now: float):
        self.system.fetch()

        self.last_sync_time = now
        self.sync()

        song_name = self.system.get_song_name()

        if song_name != self.current_song_name:
            self.current_song_name = song_name
            self.load_data()

            if not self.config["use_local_cover_palette"]:
                return

            if self.system.get_song_path():
                # path provided by player
                song_path = self.system.get_song_path()
            else:
                # find the path
                if self.config["music_file_path"]:
                    search_path = self.config["music_file_path"].removesuffix("/").removesuffix("\\")
                else:
                    search_path = platformdirs.user_music_dir()
                song_path = self.find_song_path(search_path, song_name)

            if song_path:
                print(f"Loading cover image of {song_name} ({song_path})...")
            else:
                print(f"Couldn't locate file for {song_name}")

            image_data = cover.extract_file_cover(song_path)

            if image_data:
                self.calculate_palette(image_data)
            else:
                print(f"Couldn't load cover for {song_name}")

    def update(self):
        if pr.is_key_pressed(pr.KeyboardKey.KEY_ESCAPE):
            pr.close_window()
            sys.exit()

        if pr.is_key_pressed(pr.KeyboardKey.KEY_R):
            self.load_data()
            self.sync()

        now = pr.get_time()

        if now - self.last_sync_time > 1:
            self.sync_interval(now)

        self.lyrics.update()

    def calculate_palette(self, image_data=None):
        if image_data:
            self.palette.from_image_data(image_data)

        pr.begin_texture_mode(self.gradient_texture)
        self.gradient.render((self.width, self.height))
        pr.end_texture_mode()

    def draw_palette(self):
        pr.draw_rectangle(
            0, 0,
            100, 100,
            self.palette.get_color(0)
        )
        pr.draw_rectangle(
            100, 0,
            100, 100,
            self.palette.get_color(1)
        )
        pr.draw_rectangle(
            200, 0,
            100, 100,
            self.palette.get_color(2)
        )
        pr.draw_rectangle(
            0, 100,
            100, 100,
            self.palette.get_text_color_light()
        )
        pr.draw_rectangle(
            100, 100,
            100, 100,
            self.palette.get_text_color_dark()
        )

    def render(self):
        pr.begin_drawing()

        pr.draw_texture(
            self.gradient_texture.texture,
            0, 0,
            pr.WHITE
        )

        self.lyrics.render()

        pr.end_drawing()

    def run(self):
        while True:
            self.update()
            self.render()

            pr.set_window_title(f"FPS: {pr.get_fps()}")


if __name__ == '__main__':
    Main().run()
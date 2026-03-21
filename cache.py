import platformdirs
import os

from defaults import *


class Cache:
    def __init__(self):
        self.cache_path = platformdirs.user_cache_dir(
            APP_NAME,
            APP_AUTHOR
        )

        if not os.path.exists(self.cache_path):
            os.mkdir(self.cache_path)
            print("created cache directory")

        print("using", self.cache_path, "as cache directory")

    def file_path(self, song_hash: str):
        return self.cache_path + "/" + song_hash

    def is_cached(self, song_hash: str) -> bool:
        path = self.file_path(song_hash)

        if os.path.exists(path):
            with open(path, "r") as file:
                raw = file.read()

            return len(raw) > 0

        return False

    def get(self, song_hash: str) -> str:
        path = self.file_path(song_hash)

        with open(path, "r") as file:
            return file.read()

    def store(self, song_hash: str, raw: str):
        path = self.file_path(song_hash)

        with open(path, "w") as file:
            file.write(raw)
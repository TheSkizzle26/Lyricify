import requests

from .data_module import DataModule


class DataLrcLib(DataModule):
    """
    Pretty weird code but works
    surprisingly well.
    """

    def load(self, data) -> bool:
        if not data:
            return False
        if "syncedLyrics" not in data:
            return False
        if data["syncedLyrics"] is None:
            return False

        self.lyrics_raw = data["syncedLyrics"]

        return True

    def fetch_try(self, name: str, album: str, artists: list[str], length: float, params_to_pass: list[str]):
        self.fetch_successful = False
        url = "https://lrclib.net/api/search"
        params = {}

        if name and "name" in params_to_pass: params["track_name"] = name
        if artists and "artists" in params_to_pass: params["artist_name"] = artists
        if album and "album" in params_to_pass: params["album_name"] = album
        if length and "length" in params_to_pass: params["duration"] = length

        print(name, album, artists, length)

        result = requests.get(url, params=params)
        if result.status_code == 404:
            print("lrclib returned code", result.status_code)
            return

        data = result.json()
        print(len(data))

        found = False
        for json in data:
            print(json)
            if self.load(json):
                found = True
                break

        if not found:
            print(f"lrclib doesn't provide synced lyrics: {name}")
            return

        self.fetch_successful = True

    def fetch(self, name: str, album: str, artists: list[str], length: float):
        print("lrclib: trying with all parameters...")
        self.fetch_try(name, album, artists, length, params_to_pass=["name", "artists", "album", "length"])

        if self.fetch_successful:
            return

        print("lrclib: trying without album...")
        self.fetch_try(name, album, artists, length, params_to_pass=["name", "artists", "length"]) # try without album data

        if self.fetch_successful:
            return

        print("lrclib: trying without artists...")
        self.fetch_try(name, album, artists, length, params_to_pass=["name", "album", "length"]) # try without artists data

        if self.fetch_successful:
            return

        print("lrclib: trying without album & artists...")
        self.fetch_try(name, album, artists, length, params_to_pass=["name", "length"]) # try without album & artists data
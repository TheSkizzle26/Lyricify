import requests

from .data_module import DataModule


class DataLrcLib(DataModule):
    def load(self, data) -> bool:
        if not data:
            return False
        if "syncedLyrics" not in data:
            return False
        if data["syncedLyrics"] is None:
            return False

        self.lyrics_raw = data["syncedLyrics"]

        return True

    def fetch(self, name: str, album: str, artists: list[str], length: float):
        self.fetch_successful = False
        url = "https://lrclib.net/api/search"
        params = {}

        if name: params["track_name"] = name
        if artists: params["artist_name"] = artists
        if album: params["album_name"] = album
        # if length: params["duration"] = length

        result = requests.get(url, params=params)
        if result.status_code == 404:
            print("lrclib returned code", result.status_code)
            return

        data = result.json()

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
class DataModule:
    def __init__(self):
        self.fetch_successful = False
        self.lyrics_raw = ""

    def fetch(self, name: str, album: str, artists: list[str], length: float):
        ...

    def was_successful(self) -> bool:
        return self.fetch_successful

    def get_lyrics_raw(self) -> str:
        return self.lyrics_raw
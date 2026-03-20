from data.data_module import DataModule
from data.lrclib import DataLrcLib


class Data(DataModule):
    def __init__(self):
        super().__init__()

        # maybe I'll add more later, but for now this'll do
        self.lrclib = DataLrcLib()

    def fetch(self, name: str, album: str, artists: list[str], length: float):
        self.lrclib.fetch(name, album, artists, length)
        self.fetch_successful = True

        if self.lrclib.was_successful():
            self.lyrics_raw = self.lrclib.get_lyrics_raw()
            print(f"Successfully fetched song info: {name}")
            return

        print(f"Couldn't fetch song info: {name}")
        self.fetch_successful = False
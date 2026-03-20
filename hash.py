import hashlib


def get_song_hash(name: str, artists: list[str], album: str, length: float):
    buf = bytes(name.encode())

    for artist in artists:
        buf += bytes(artist.encode())

    buf += bytes(album.encode())
    buf += int(length).to_bytes(4, signed=False)

    hash = hashlib.sha256(buf)
    return hash.hexdigest()


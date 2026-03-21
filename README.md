## Lyricify
A simple program to display the currently playing lyrics!

![preview](./preview.gif)

## Requirements
- Linux (Windows currently isn't supported)
- uv

## How to run
1. Clone the GitHub repo
2. Open your terminal in the downloaded folder
3. Run **uv run main.py**

## How to configure
- Edit the config file (~/.config/Lyricify/lyricify.conf on Linux)
- Just change whatever you want and rerun the program
- To reset the config file, just delete it

## FAQ
- **There's a black screen?**

    Just wait a few seconds, it probably can't find the lyrics online.
- **The background is black?**
    
    Lyricify searches your music directory for a file containing the currently playing song.
If it can't find it, it can't use the contained cover art. I will add fetching this information online later.
- **The lyrics aren't synced up correctly?**

    Sometimes the lyrics this program fetches online are just poorly synced.
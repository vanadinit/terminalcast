# Terminalcast

Command line tool to cast local video files to your chromecast.

Inspired by https://github.com/keredson/gnomecast

## Supported media types
Checkout https://developers.google.com/cast/docs/media for your Chromecast model.

Use ffmpeg to convert unsupported files to a supported format:
```commandline
ffmpeg -i '{input_file}' -metadata title="{title}" -map 0 -c:v {video_codec} -c:a {audio_codec} -c:s copy '{output_file}'
```

## Supported Chromecast versions
In principle this should work with any Chromecast which is supported by https://github.com/home-assistant-libs/pychromecast.

In practice, I discovered that a Chromecast with Google TV enables you to control the player via the remote control, which is very nice.

## Installation
```commandline
pip install terminalcast
```

## Usage

### Basic Usage
```commandline
terminalcast my_video.mp4
```

### Port Configuration
By default, a random free port is chosen. You can specify a fixed port if needed (e.g. for firewall rules):
```commandline
terminalcast my_video.mp4 --port 8080
```
Alternatively, set the environment variable `TERMINALCAST_PORT`:
```bash
export TERMINALCAST_PORT=8080
terminalcast my_video.mp4
```

### Reverse Proxy / Custom URL
If you are running terminalcast behind a reverse proxy (e.g. Nginx, Traefik) and want to expose the video via a specific full URL:
```commandline
terminalcast my_video.mp4 --video-url https://my-server.com/cast/video
```
Alternatively, set the environment variable `TERMINALCAST_VIDEO_URL`:
```bash
export TERMINALCAST_VIDEO_URL="https://my-server.com/cast/video"
terminalcast my_video.mp4
```
**Note:** You must ensure that your proxy forwards requests from this URL to the local terminalcast server (default path is `/video`).

### Known Hosts
If network discovery fails (e.g. due to network restrictions), you can specify known Chromecast IPs:
```commandline
terminalcast my_video.mp4 --known-hosts 192.168.1.50,192.168.1.51
```
Alternatively, set the environment variable `TERMINALCAST_KNOWN_HOSTS`:
```bash
export TERMINALCAST_KNOWN_HOSTS="192.168.1.50,192.168.1.51"
terminalcast my_video.mp4
```

### Temporary File Location
When selecting a different audio track, a temporary file is created. To speed this up, you can specify a directory for these files, ideally a RAM disk. A progress bar will be shown during this process.

The default priority is:
1. `TERMINALCAST_TMP_DIR` environment variable
2. `/dev/shm` (RAM disk on Linux)
3. `/var/tmp`
4. System default

Example:
```bash
export TERMINALCAST_TMP_DIR="/my/fast/disk"
terminalcast my_video.mp4 --audio-title "English"
```

## Using as a Library
You can also use `terminalcast` as a library in your own projects.

```python
from terminalcast import FileMetadata, TerminalCast, create_tmp_video_file

# 1. Get file metadata
filepath = "my_video.mp4"
media_file = FileMetadata(filepath=filepath)
print(media_file.details())

# 2. Select an audio stream (e.g., the first one)
audio_stream = media_file.audio_streams[0]

# 3. (Optional) Create a temporary file if a different audio track is needed
# This shows a progress bar and can take a callback for progress updates
def my_progress_callback(progress: float):
    print(f"Conversion progress: {progress:.2f}%")

tmp_filepath = create_tmp_video_file(
    filepath=filepath,
    audio_index=audio_stream.index[-1:],
    duration=media_file.duration,
    progress_callback=my_progress_callback
)

# 4. Initialize TerminalCast
# You can pass known_hosts as a list of IPs and a specific port
tcast = TerminalCast(
    filepath=tmp_filepath or filepath,
    select_ip=False,  # or True for interactive selection, or a specific IP string
    known_hosts=["192.168.1.50"],
    port=8080,
    video_url="https://my-server.com/cast/video"
)

# 5. Start the server and play
print(f"Casting to: {tcast.cast.cast_info.friendly_name}")
tcast.start_server()
tcast.play_video()

# The video is now playing. The script will block here until playback is active.
# You might want to add logic to handle server shutdown, etc.
```

## Contributing
Contributions are welcome! To set up your development environment:

1.  **Clone the repository**
2.  **Install dependencies:** This will install the project in editable mode with all development tools.
    ```bash
    make install
    ```
3.  **Install the pre-commit hook:** This will run quick checks before each commit.
    ```bash
    pre-commit install
    ```
4.  **Run all checks:** You can run all linters, type checks, and tests manually at any time.
    ```bash
    make check
    ```

## How is it working?
**Terminalcast** creates a little HTTP Server at your current machine and serves your media file there. Then it tells the
Chromecast the play the stream served at your IP with the corresponding path. That's it! (The devil is in the details.)

**Terminalcast** uses [Bottle](https://bottlepy.org/docs/dev/) to create a small app providing the media file. This app is
served by [Waitress](https://docs.pylonsproject.org/projects/waitress/en/stable/).

On the other hand **Terminalcast** detects and plays the media via [PyChromecast](https://pypi.org/project/PyChromecast/).

For file information and conversion [ffmpeg-python](https://pypi.org/project/ffmpeg-python/) is used.

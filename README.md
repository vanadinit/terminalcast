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

## How is it working?
**Terminalcast** creates a little HTTP Server at your current machine and serves your media file there. Then it tells the
Chromecast the play the stream served at your IP with the corresponding path. That's it! (The devil is in the details.)

**Terminalcast** uses [Bottle](https://bottlepy.org/docs/dev/) to create a small app providing the media file. This app is
served by [Paste](https://pypi.org/project/Paste/).

On the other hand **Terminalcast** detects and plays the media via [PyChromecast](https://pypi.org/project/PyChromecast/).

For file information and conversion [ffmpeg-python](https://pypi.org/project/ffmpeg-python/) is used.

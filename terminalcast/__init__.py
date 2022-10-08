import socket
from argparse import ArgumentParser
from contextlib import closing
from threading import Thread
from time import sleep

import ffmpeg_streaming
from bottle import Bottle, static_file

PORT = 12345

RECEIVER_APP = '''<html>
<head>
  <script type="text/javascript"
      src="//www.gstatic.com/cast/sdk/libs/caf_receiver/v3/cast_receiver_framework.js">
  </script>
</head>
<body>
  <cast-media-player></cast-media-player>
  <script>
    cast.framework.CastReceiverContext.getInstance().start();
  </script>
</body>
</html>
'''


def get_my_ip() -> str:
    for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
        if not ip.startswith("127."):
            return ip

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.connect(("8.8.8.8", 53))
        return s.getsockname()[0]


def get_port() -> int:
    # with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
    #    s.bind(('0.0.0.0', 0))
    #    return s.getsockname()[1]

    return PORT


def run_server(filepath: str):
    app = Bottle()

    @app.get('/video.<ext>')
    def video():
        response = static_file(filepath, root='/')
        if 'Last-Modified' in response.headers:
            del response.headers['Last-Modified']
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Connection'] = 'keep-alive'
        return response

    @app.route('/home')
    def home():
        return RECEIVER_APP

    app.run(host=get_my_ip(), port=get_port(), debug=True)


def main():
    parser = ArgumentParser(prog='terminalcast', description='Cast local videos to your chromecast')
    parser.add_argument(
        'filepath', help='file path'
    )
    args = parser.parse_args()

    # TODO Use DASH
    video = ffmpeg_streaming.input(args.filepath)
    dash = video.dash(ffmpeg_streaming.Formats.h264())
    dash.auto_generate_representations()
    # dash.output()

    Thread(target=run_server, kwargs={'filepath': args.filepath}, daemon=True).start()
    sleep(1)


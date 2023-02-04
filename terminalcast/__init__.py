import socket
from argparse import ArgumentParser
from contextlib import closing
from functools import cached_property
from threading import Thread
from time import sleep
from typing import List

from bottle import Bottle, static_file
from paste import httpserver
from paste.translogger import TransLogger
from pychromecast import get_chromecasts, Chromecast
from pychromecast.controllers.media import MediaController


def get_my_ip() -> str:
    for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
        if not ip.startswith("127."):
            return ip

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.connect(("8.8.8.8", 53))
        return s.getsockname()[0]


def get_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('0.0.0.0', 0))
        return s.getsockname()[1]


def selector(entries: List[tuple]):
    """Provides a command line interface for selecting from multiple entries
    :param entries: List of Tuples(entry: Any, label: str)
    """
    match len(entries):
        case 0:
            return None
        case 1:
            return entries[0][0]
        case _:
            entry_labels = '\n'.join([
                f'{index}: {entry[1]}'
                for index, entry in enumerate(entries)
            ])
            return entries[int(input(f'Found multiple entries, please choose: \n{entry_labels}\n'))][0]


class TerminalCast:
    def __init__(self, filepath: str):
        self.filepath = filepath

    @cached_property
    def ip(self) -> str:
        return get_my_ip()

    @cached_property
    def port(self) -> int:
        return get_port()

    @cached_property
    def cast(self) -> Chromecast:
        print('Searching Chromecasts ...')
        chromecasts, browser = get_chromecasts()

        chromecast = selector(entries=[
            (cast, f'{cast.cast_info.friendly_name} ({cast.cast_info.host})')
            for cast in chromecasts
        ])

        if chromecast:
            chromecast.wait()
            return chromecast

        raise Exception('No Chromecast available')

    def start_server(self):
        Thread(target=self.run_server).start()
        sleep(5)

    def run_server(self):
        app = Bottle()

        @app.get('/video')
        def video():
            response = static_file(self.filepath, root='/')
            if 'Last-Modified' in response.headers:
                del response.headers['Last-Modified']
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            response.headers['Connection'] = 'keep-alive'
            return response

        print('Starting server')
        print(f'IP: {self.ip}, Port: {self.port}')
        handler = TransLogger(app, setup_console_handler=True)
        httpserver.serve(handler, host=self.ip, port=str(self.port), daemon_threads=True)

    def play_video(self):
        mc: MediaController = self.cast.media_controller
        mc.play_media(url=f'http://{self.ip}:{self.port}/video', content_type='video/mp4')
        mc.block_until_active()
        print(mc.status)


def main():
    parser = ArgumentParser(prog='terminalcast', description='Cast local videos to your chromecast')
    parser.add_argument('filepath', help='file path')
    # TODO audio stream selection
    #  * check with ffmpeg, it there are multiple streams
    #  * provide selection possibiliy
    #  * reencode with ffmpeg if not the first stream, delete all others -> temp file
    args = parser.parse_args()

    tc = TerminalCast(filepath=args.filepath)
    print(f'Chromecast: {tc.cast.cast_info.friendly_name}')
    print(f'Status: {tc.cast.status}')
    tc.start_server()
    tc.play_video()

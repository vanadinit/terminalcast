import socket
from argparse import ArgumentParser
from contextlib import closing
from threading import Thread
from time import sleep

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


class TerminalCast:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.cast = None

        self._ip = None
        self._port = None

    @property
    def ip(self):
        if self._ip is None:
            self._ip = get_my_ip()
            print(f'IP: {self._ip}')
        return self._ip

    @property
    def port(self):
        if self._port is None:
            self._port = get_port()
            print(f'Port: {self._ip}')
        return self._port

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
        handler = TransLogger(app, setup_console_handler=True)
        httpserver.serve(handler, host=self.ip, port=str(self.port), daemon_threads=True)

    def select_cast(self):
        self.cast: Chromecast
        print('Searching Chromecasts ...')
        chromecasts, browser = get_chromecasts()
        match len(chromecasts):
            case 0:
                raise Exception('No Chromecast available')
            case 1:
                self.cast = chromecasts[0]
            case _:
                casts = '\n'.join([
                    f'{index}: {cast.cast_info.friendly_name} ({cast.cast_info.host})'
                    for index, cast in enumerate(chromecasts)
                ])
                self.cast = chromecasts[int(input(f'Found multiple Chromecasts, please choose: \n{casts}\n'))]
        self.cast.wait()
        print(f'Chromecast: {self.cast.cast_info.friendly_name}')
        print(f'Status: {self.cast.status}')

    def play_video(self):
        if self.cast is None:
            self.select_cast()

        mc: MediaController = self.cast.media_controller
        mc.play_media(url=f'http://{self.ip}:{self.port}/video', content_type='video/mp4')
        mc.block_until_active()
        print(mc.status)


def main():
    parser = ArgumentParser(prog='terminalcast', description='Cast local videos to your chromecast')
    parser.add_argument('filepath', help='file path')
    args = parser.parse_args()

    tc = TerminalCast(filepath=args.filepath)
    tc.select_cast()
    tc.start_server()
    tc.play_video()

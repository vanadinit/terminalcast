import os
import socket
from contextlib import closing
from functools import cached_property
from tempfile import mkstemp
from threading import Thread
from time import sleep

import ffmpeg
from bottle import Bottle, static_file
from paste import httpserver
from paste.translogger import TransLogger
from pychromecast import Chromecast, get_chromecasts
from pychromecast.controllers.media import MediaController

from . import selector


class TerminalCast:
    def __init__(self, filepath: str, select_ip: str | bool):
        self.filepath = filepath
        self.select_ip = select_ip
        self.server_thread = None

    @cached_property
    def ip(self) -> str:
        if isinstance(self.select_ip, str):
            return self.select_ip

        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.connect(("8.8.8.8", 53))
            ip_rec = s.getsockname()[0]

        if not self.select_ip:
            return ip_rec

        ip_list = []
        for _ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            if _ip.startswith('127.'):
                continue
            label = f'{_ip} (recommended)' if _ip == ip_rec else _ip
            ip_list.append((_ip, label))

        if ip_list:
            return selector(ip_list)
        else:
            return ip_rec

    @cached_property
    def port(self) -> int:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('0.0.0.0', 0))
            return s.getsockname()[1]

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
        self.server_thread = Thread(target=self.run_server).start()
        sleep(5)

    def stop_server(self):
        if isinstance(self.server_thread, Thread):
            self.server_thread.join()

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


def create_tmp_video_file(filepath: str, audio_index: int) -> str:
    """
    Create temporary video file with specified audio track only
    :param filepath: file path of original video file
    :param audio_index: stream index of requested audio track
    :return: filename (including path)
    """
    tmp_file_path = mkstemp(
        suffix='.mp4',
        prefix=f'terminalcast_pid{os.getpid()}_',
        dir='/var/tmp' if os.path.isdir('/var/tmp') else None)[1]
    os.remove(tmp_file_path)

    print(f'Create temporary video file at {tmp_file_path}')

    input_stream = ffmpeg.input(filepath, loglevel='error')
    video = input_stream['v']
    audio = input_stream[audio_index]
    ffmpeg.output(
        video, audio, tmp_file_path,
        codec='copy',
    ).run()

    print(f'Video created')
    return tmp_file_path

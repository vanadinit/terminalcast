import os
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

from .helper import selector
from .network import get_my_ip, get_port


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

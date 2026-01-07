import os
import socket
import time
from contextlib import closing
from datetime import datetime
from functools import cached_property
from tempfile import mkstemp
from threading import Thread
from typing import Callable

import ffmpeg
from bottle import Bottle, static_file, request, response
from pychromecast import Chromecast, get_chromecasts
from pychromecast.controllers.media import MediaController
from tqdm import tqdm
from waitress import serve

from .helper import format_bytes, selector, simplify_user_agent


class TerminalCast:
    def __init__(self, filepath: str, select_ip: str | bool, known_hosts: list[str] | None = None, port: int | None = None):
        self.filepath = os.path.abspath(filepath)
        self.select_ip = select_ip
        self.known_hosts = known_hosts
        self.requested_port = port
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
        if self.requested_port:
            return self.requested_port

        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('0.0.0.0', 0))
            return s.getsockname()[1]

    @cached_property
    def cast(self) -> Chromecast:
        print('Searching Chromecasts ...')
        chromecasts, browser = get_chromecasts(known_hosts=self.known_hosts)

        chromecast = selector(entries=[
            (cast, f'{cast.cast_info.friendly_name} ({cast.cast_info.host})')
            for cast in chromecasts
        ])

        if chromecast:
            chromecast.wait()
            return chromecast

        raise NoChromecastAvailable('No Chromecast available')

    def start_server(self):
        self.server_thread = Thread(target=self.run_server)
        self.server_thread.start()
        time.sleep(5)

    def get_video_url(self) -> str:
        return f'http://{self.ip}:{self.port}/video'

    def run_server(self):
        print(self.get_video_url())
        run_http_server(filepath=self.filepath, ip=self.ip, port=self.port)

    def play_video(self):
        mc: MediaController = self.cast.media_controller
        mc.play_media(url=self.get_video_url(), content_type='video/mp4')
        mc.block_until_active()
        print(mc.status)


def run_http_server(filepath: str, ip: str, port: int):
    app = Bottle()

    @app.hook('after_request')
    def log_request():
        ts = datetime.now().astimezone().strftime('%d/%b/%Y %H:%M:%S %z')
        length = format_bytes(response.headers.get('Content-Length'))
        addr = request.remote_addr or '-'
        ua = simplify_user_agent(request.headers.get('User-Agent', '-'))

        print(f'[{ts}] {request.method} {request.path} {response.status_code} ({length}) from {addr} ({ua})')

    @app.get('/video')
    def video():
        resp = static_file(filepath, root='/')
        if 'Last-Modified' in resp.headers:
            del resp.headers['Last-Modified']
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, HEAD'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return resp

    print('Starting server')
    serve(app, host=ip, port=port, _quiet=True)


def create_tmp_video_file(
    filepath: str,
    audio_index: str | int,
    duration: float,
    progress_callback: Callable[[float], None] | None = None
) -> str:
    """
    Create temporary video file with specified audio track only
    :param filepath: file path of original video file
    :param audio_index: stream index of requested audio track
    :param duration: total duration of the video in seconds
    :param progress_callback: function to call with progress percentage
    :return: filename (including path)
    """
    # Prioritize env var, then fall back to smart detection
    temp_dir = os.getenv('TERMINALCAST_TMP_DIR')
    if not temp_dir or not os.path.isdir(temp_dir):
        if os.path.isdir('/dev/shm'):
            temp_dir = '/dev/shm'
        elif os.path.isdir('/var/tmp'):
            temp_dir = '/var/tmp'
        else:
            temp_dir = None  # Use system default

    tmp_file_path = mkstemp(
        suffix='.mp4',
        prefix=f'terminalcast_pid{os.getpid()}_',
        dir=temp_dir
    )[1]
    os.remove(tmp_file_path)

    print(f'Create temporary video file at {tmp_file_path}')

    input_stream = ffmpeg.input(filepath)
    video = input_stream['v']
    audio = input_stream[str(audio_index)]
    
    process = (
        ffmpeg.output(video, audio, tmp_file_path, codec='copy', progress='pipe:1')
        .run_async(pipe_stdout=True, pipe_stderr=True)
    )

    with tqdm(total=100, desc="Converting") as pbar:
        for line in process.stdout:
            line = line.decode('utf-8')
            if 'out_time_ms' in line:
                time_ms = int(line.split('=')[1])
                progress = (time_ms / (duration * 1000000)) * 100
                pbar.n = int(progress)
                pbar.refresh()
                if progress_callback is not None:
                    progress_callback(progress)

    process.wait()
    print('Video created')
    return tmp_file_path


class NoChromecastAvailable(Exception):
    pass

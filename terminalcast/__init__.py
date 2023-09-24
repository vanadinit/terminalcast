import os
from argparse import ArgumentParser
from importlib import metadata
from tempfile import mkstemp

import ffmpeg

from .filedata import FileMetadata
from .helper import selector
from .tc import TerminalCast

VERSION = metadata.version('terminalcast')


def main():
    print(f'Terminalcast Version {VERSION}')

    parser = ArgumentParser(prog='terminalcast', description='Cast local videos to your chromecast')
    parser.add_argument('filepath', help='file path')
    args = parser.parse_args()

    print('----- File information -----')
    media_file_data = FileMetadata(filepath=args.filepath)
    print(media_file_data.details())

    audio_stream = selector(entries=[
        (stream, f'Audio: {stream.title}')
        for stream in media_file_data.audio_streams
    ])

    tmp_file_path = ''
    if audio_stream and audio_stream != media_file_data.audio_streams[0]:
        tmp_file_path = mkstemp(
            suffix='.mp4',
            prefix=f'terminalcast_pid{os.getpid()}_',
            dir='/var/tmp' if os.path.isdir('/var/tmp') else None)[1]
        os.remove(tmp_file_path)

        print(f'Create temporary video file at {tmp_file_path}')
        input = ffmpeg.input(args.filepath, loglevel='error')
        video = input['v']
        audio = input[audio_stream.index[-1:]]
        ffmpeg.output(
            video, audio, tmp_file_path,
            codec='copy',
        ).run()
        print(f'Video created')

    print('----- Initializing Chromecast -----')
    tc = TerminalCast(filepath=tmp_file_path or args.filepath)
    print(f'Chromecast: {tc.cast.cast_info.friendly_name}')
    print(f'Status: {tc.cast.status}')

    print('----- Starting HTTP Server -----')
    tc.start_server()

    print('----- Start playing video -----\n')
    tc.play_video()

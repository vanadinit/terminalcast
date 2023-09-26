from argparse import ArgumentParser
from importlib import metadata

from .filedata import FileMetadata, AudioMetadata
from .helper import selector
from .tc import TerminalCast, create_tmp_video_file

VERSION = metadata.version('terminalcast')


def main():
    print(f'Terminalcast Version {VERSION}')

    parser = ArgumentParser(prog='terminalcast', description='Cast local videos to your chromecast')
    parser.add_argument('filepath', help='file path')
    args = parser.parse_args()

    print('----- File information -----')
    media_file_data = FileMetadata(filepath=args.filepath)
    print(media_file_data.details())

    audio_stream: AudioMetadata = selector(entries=[
        (stream, f'Audio: {stream.title}')
        for stream in media_file_data.audio_streams
    ])

    print(f'Select audio stream "{audio_stream.title}"')

    tmp_file_path = ''
    if audio_stream and audio_stream != media_file_data.audio_streams[0]:
        print('Need to create temp file with selected audio track only')
        tmp_file_path = create_tmp_video_file(filepath=args.filepath, audio_index=audio_stream.index[-1:])

    print('----- Initializing Chromecast -----')
    tc = TerminalCast(filepath=tmp_file_path or args.filepath)
    print(f'Chromecast: {tc.cast.cast_info.friendly_name}')
    print(f'Status: {tc.cast.status}')

    print('----- Starting HTTP Server -----')
    tc.start_server()

    print('----- Start playing video -----\n')
    tc.play_video()

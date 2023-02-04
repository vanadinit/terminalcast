from argparse import ArgumentParser
from importlib import metadata

from .filedata import FileMetadata
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
    # TODO audio stream selection
    #  * check with ffmpeg, it there are multiple streams
    #  * provide selection possibiliy
    #  * reencode with ffmpeg if not the first stream, delete all others -> temp file

    print('----- Initializing Chromecast -----')
    tc = TerminalCast(filepath=args.filepath)
    print(f'Chromecast: {tc.cast.cast_info.friendly_name}')
    print(f'Status: {tc.cast.status}')

    print('----- Starting HTTP Server -----')
    tc.start_server()

    print('----- Start playing video -----\n')
    tc.play_video()

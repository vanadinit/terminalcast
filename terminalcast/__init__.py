from argparse import ArgumentParser, Namespace
from importlib import metadata

from .filedata import FileMetadata, AudioMetadata
from .helper import selector
from .tc import TerminalCast, create_tmp_video_file

VERSION = metadata.version('terminalcast')


def select_audio(media_file_data: FileMetadata, args: Namespace) -> AudioMetadata:
    if args.audio_title:
        return [
            stream
            for stream in media_file_data.audio_streams
            if stream.title == args.audio_title
        ][0]
    elif args.non_interactive:
        return media_file_data.audio_streams[0]
    else:
        return selector(entries=[
            (stream, f'Audio: {stream.title}')
            for stream in media_file_data.audio_streams
        ])


def main():
    print(f'Terminalcast Version {VERSION}')

    parser = ArgumentParser(prog='terminalcast', description='Cast local videos to your chromecast')
    parser.add_argument('filepath', help='file path')
    parser.add_argument(
        '--select-ip',
        action='store_true',
        help='Flag to manually select the correct ip where the hosted file should be provided',
    )
    parser.add_argument(
        '--ip',
        help='IP address where hosted file should be provided',
    )
    parser.add_argument(
        '--audio-title',
        help='Title of desired audio stream',
    )
    parser.add_argument(
        '--non-interactive',
        action='store_true',
        help='For scripts and non interactive environments. Disables "select-ip" and auto-select all values not given',
    )
    args = parser.parse_args()

    print('----- File information -----')
    media_file_data = FileMetadata(filepath=args.filepath)
    print(media_file_data.details())

    audio_stream = select_audio(media_file_data=media_file_data, args=args)
    print(f'Selecting audio stream "{audio_stream.title}"')

    tmp_file_path = ''
    if audio_stream and audio_stream != media_file_data.audio_streams[0]:
        print('Need to create temp file with selected audio track only')
        tmp_file_path = create_tmp_video_file(filepath=args.filepath, audio_index=audio_stream.index[-1:])

    print('----- Create Terminalcast and select IP -----')
    tcast = TerminalCast(
        filepath=tmp_file_path or args.filepath,
        select_ip=args.ip or (args.select_ip and not args.non_interactive),
    )
    print(f'IP: {tcast.ip}')

    print('----- Initializing Chromecast -----')
    print(f'Chromecast: {tcast.cast.cast_info.friendly_name}')
    print(f'Status: {tcast.cast.status}')

    print('----- Starting HTTP Server -----')
    tcast.start_server()

    print('----- Start playing video -----\n')
    tcast.play_video()

import os
from functools import cached_property
from typing import List

import ffmpeg


class Metadata:
    def __repr__(self):
        fields = [f'{k}:{v}' for k, v in self.__dict__.items() if v is not None and not k.startswith('_')]
        return '{class_name}({fields})'.format(
            class_name=self.__class__.__name__,
            fields=', '.join(fields)
        )


class StreamMetadata(Metadata):
    def __init__(self, index, codec, title=None):
        self.index = index
        self.codec = codec
        self.title = title

    def details(self):
        return f'{self.title} ({self.codec})'


class AudioMetadata(StreamMetadata):
    def __init__(self, channels: int = 2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channels = channels

    def details(self):
        match self.channels:
            case 1:
                channels = 'mono'
            case 2:
                channels = 'stereo'
            case 6:
                channels = '5.1'
            case 8:
                channels = '7.1'
            case _:
                channels = str(self.channels)
        return f'{self.title} ({self.codec}/{channels})'


class FileMetadata(Metadata):
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.ext = filepath.lower().split(".")[-1]

    @cached_property
    def ffoutput(self) -> dict:
        return ffmpeg.probe(self.filepath)

    @cached_property
    def duration(self) -> float:
        return float(self.ffoutput['format']['duration'])

    @cached_property
    def audio_streams(self) -> List[AudioMetadata]:
        return [
            AudioMetadata(
                index=f'0:{stream["index"]}',
                codec=stream['codec_name'],
                title=stream.get('tags', {}).get('language', 'Audio (unknown)'),
                channels=stream['channels'],
            )
            for stream in self.ffoutput['streams']
            if stream.get('codec_type') == 'audio'
        ]

    @cached_property
    def video_streams(self) -> List[StreamMetadata]:
        return [
            StreamMetadata(
                index=f'0:{stream["index"]}',
                codec=stream['codec_name'],
                title=stream.get('tags', {}).get('language', 'Video (unknown)'),
            )
            for stream in self.ffoutput['streams']
            if stream.get('codec_type') == 'video'
        ]

    def details(self):
        return '''
        File: {file}
        Video: {video}
        Audio: {audio}
        '''.format(
            file=os.path.basename(self.filepath),
            video=', '.join([vis.details() for vis in self.video_streams]),
            audio=', '.join([aus.details() for aus in self.audio_streams]),
        )

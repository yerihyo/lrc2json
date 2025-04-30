import operator
import re
from functools import reduce
from itertools import chain
from typing import TextIO, Iterable

from future.utils import lmap


class LRC:

    def __init__(self, file: TextIO):
        self.file = file
    
    def write_synced_lyrics(self, lyrics: dict, f: TextIO) -> None:
        
        for millis in sorted(lyrics.keys()):

            minutes   = millis // 1000 // 60 
            seconds   = (millis // 1000) % 60
            remainder = millis % 1000

            line = '[{:02d}:{:02d}.{:02d}]{}'.format(minutes, seconds, remainder, lyrics[millis])
            if line[-1] != '\n': line += '\n'
            f.write(line)

    @classmethod
    def timestamp_str2msoffset(cls, s):
        has_millis = '.' in s
        pattern = '[\.:]' if has_millis else ':'
        parts = re.split(pattern, s)

        minutes = int(parts[0])
        seconds = int(parts[1])
        millis = int(parts[2]) if has_millis else 0

        return minutes * 60 * 1000 + seconds * 1000 + millis

    @classmethod
    def dicts2merged(cls, dicts:Iterable[dict]):
        return reduce(lambda a, b: {**a, **b}, dicts)



    @classmethod
    def lines2infos(cls, lines: Iterable[str]):
        def line2infos(line: str) -> Iterable[dict]:

            # lines = file.readlines()
            if not line:
                return None

            results = re.finditer('(\[\d\d\:\d\d\.\d+?(?=\])\]+)|(\[\d\d\:\d+?(?=\])\]+)', line)
            matches = [t for t in results]

            if len(matches) == 0:
                return None

            end_index = max([t.end(0) for t in matches])
            lyric = line[end_index:].strip()
            # if not lyrics:
            #     return None

            s_timestamps = [t.group(0)[1:-1] for t in matches]

            for x in s_timestamps:
                yield {
                    "msoffset": cls.timestamp_str2msoffset(x),
                    "lyric": lyric
                }

        infos = sorted(
            chain.from_iterable(map(line2infos, lines)),
            key=lambda x: x['msoffset']
        )
        return infos

    @classmethod
    def msoffset2str_srt(cls, msoffset):
        hours = int(msoffset) // (1000*60*60)
        minutes = (int(msoffset) % (1000*60*60)) // (1000*60)
        seconds = (int(msoffset) % (1000*60)) // 1000
        millisecs = msoffset % 1000
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millisecs:03d}"

    @classmethod
    def infos2srtlines(cls, infos:Iterable[dict]):
        # strs_msoffset = lmap(lambda info_: cls.msoffset2str_srt(info_['msoffset']), infos)

        for i, info in enumerate(infos):
            if not info['lyric']:
                continue

            msoffset_start = infos[i]['msoffset']
            msoffset_end = infos[i+1]['msoffset'] if i+1 < len(infos) else msoffset_start + 1000
            yield "\n".join([
                str(i+1),
                f"{cls.msoffset2str_srt(msoffset_start)} --> {cls.msoffset2str_srt(msoffset_end)}",
                info['lyric']
            ])

    @classmethod
    def info2hdoc(cls, info: dict) -> dict:
        return {info['msoffset']: info['lyric']}
    # @classmethod
    # def lines_lrc2dict(cls, lines: Iterable[str]) -> dict:
    #     return {
    #         info['msoffset']: info['lyric']
    #         for line in lines
    #         for info in cls.line2infos(line)
    #     }

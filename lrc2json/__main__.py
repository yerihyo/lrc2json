import argparse
import json
from lrc_parser import *

def main():

    parser = argparse.ArgumentParser(
                    prog='lrc2json',
                    description='Convert LRC format into json with timestamps',
                    usage="lrc2json: <lrc_file> <json_file> <srt_file>")
    
    parser.add_argument("lrc_file")
    parser.add_argument("json_file")
    parser.add_argument("srt_file")
    args = parser.parse_args()

    with open(args.lrc_file, "r", encoding="UTF-8") as infile:
        lines = [s.rstrip('\r\n') for s in infile if s]


    infos = LRC.lines2infos(lines)
    # infos = [info for str_line in lines for info in LRC.line2infos(str_line)]
    hdocs = lmap(LRC.info2hdoc, infos)
    with open(args.json_file, "w", encoding="UTF-8") as ofile:
        ofile.write(json.dumps(hdocs, ensure_ascii=False))

    srtlines = LRC.infos2srtlines(infos)
    with open(args.srt_file, "w", encoding="UTF-8") as ofile:
        print("\n\n".join(srtlines), file=ofile)

if __name__ == "__main__":
    main()



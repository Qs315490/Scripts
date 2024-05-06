"""
剔除mkv文件字幕，参数1为 文件 或 文件夹
"""

from sys import argv
from os import chdir, listdir, path
from pymkv import MKVFile, MKVTrack


def file_del(work_file: str):
    mkv = MKVFile(work_file)
    removed_track = False
    tracks: list[MKVTrack] = mkv.tracks
    if type(tracks[0]) is not MKVTrack:
        return
    for track in tracks[:]:
        if track.track_type == "subtitles":
            mkv.tracks.remove(track)
            removed_track = True
    if removed_track:
        mkv.no_attachments()
        # 在文件目录新建output文件夹
        mkv.mux(f"./output/{path.basename(work_file)}")


def dir_del(dir_path: str):
    for file in listdir(dir_path):
        if file.endswith(".mkv"):
            file_del(file)


def main():
    argc = len(argv)
    if argc < 2:
        print(f"Usage: python {argv[0]} <input.mkv>|<mkv_dir>")
        return

    if path.isfile(argv[1]):
        work_path = path.dirname(argv[1])
        chdir(work_path)
        file_del(path.basename(argv[1]))
    else:
        work_path = argv[1]
        chdir(work_path)
        dir_del(work_path)


if __name__ == "__main__":
    main()

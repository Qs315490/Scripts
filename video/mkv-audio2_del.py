"""
剔除mkv文件轨道id为2的音频，参数1为 文件 或 文件夹
"""

from os import chdir, listdir, path
from sys import argv

from pymkv import MKVFile, MKVTrack
from rich.progress import track as rich_track


def file_del(work_file: str):
    mkv = MKVFile(work_file)
    removed_track = False
    tracks: list[MKVTrack] = mkv.tracks
    if type(tracks[0]) is not MKVTrack:
        return
    for track in tracks[:]:
        if track.track_id == 2 and track.track_type == "audio":
            mkv.tracks.remove(track)
            removed_track = True
    if removed_track:
        # 在文件目录新建output文件夹
        mkv.mux(f"./output/{path.basename(work_file)}")


def dir_del(dir_path: str):
    mkv_list = [file for file in listdir(dir_path) if file.endswith(".mkv")]

    for file in rich_track(mkv_list):
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

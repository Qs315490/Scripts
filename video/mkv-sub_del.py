"""
剔除mkv文件字幕，参数1为 文件 或 文件夹
"""

from sys import argv
from os import listdir, path
from pymkv import MKVFile, MKVTrack


def file_del_sub(work_file: str):
    mkv = MKVFile(work_file)
    removed_track = False
    tracks: list[MKVTrack] = mkv.get_track()
    if type(tracks) is not list:
        return
    if type(tracks[0]) is not MKVTrack:
        return
    for track in tracks:
        if track.track_type == "subtitles":
            mkv.remove_track(track.track_id)
            removed_track = True
    if removed_track:
        # 在文件目录新建output文件夹
        output_path = path.dirname(work_file)
        mkv.mux(output_path + '/output/' + path.basename(work_file))


def dir_del_sub(dir_path: str):
    for file in listdir(dir_path):
        if file.endswith(".mkv"):
            file_del_sub(path.join(dir_path, file))


def main():
    argc = len(argv)
    if argc < 2:
        print(f"Usage: python {argv[0]} <input.mkv>")
        return
    work_path = argv[1]
    if path.isfile(work_path):
        file_del_sub(work_path)
    else:
        dir_del_sub(work_path)


if __name__ == "__main__":
    main()

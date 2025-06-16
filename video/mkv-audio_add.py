"""
合并mkv mka，参数1为 文件夹
"""

from sys import argv
from os import chdir, listdir, path
from rich.progress import track
from pymkv import MKVFile, MKVTrack

mkvs: list[str] = []
mkas: list[str] = []

def file_add(work_file: str):
    mkv = MKVFile(work_file)
    add_track = False
    name = path.splitext(work_file)[0]  # 获取文件名，无扩展名
    mka_list: list[str] = []  # 匹配文件
    for mka in mkas[:]:
        if name.lower() in mka.lower():
            mka_list.append(mka)
            mkas.remove(mka)
    # 开始添加文件
    for mka in mka_list:
        mkvtrack = MKVTrack(mka)
        mkv.add_track(mkvtrack)
        add_track = True

    if add_track:
        # 在文件目录新建output文件夹
        mkv.mux(f"./output/{work_file}")


def dir_add(dir_path: str):
    for file in listdir(dir_path):
        if file.endswith(".mkv"):
            mkvs.append(file)
        if file.endswith(".mka"):
            mkas.append(file)

    for mkv in track(mkvs, description="正在添加音频"):
        file_add(mkv)


def main():
    argc = len(argv)
    if argc < 2:
        print(f"Usage: python {argv[0]} <mkv and mka dir>")
        return
    work_path = argv[1]
    if path.isdir(work_path):
        chdir(work_path)
        dir_add(work_path)


if __name__ == "__main__":
    main()

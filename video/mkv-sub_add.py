"""
添加mkv文件字幕，参数1为 文件夹
"""

from sys import argv
from os import chdir, listdir, path
from pymkv import MKVFile, MKVTrack

mkvs: list[str] = []
subs: list[str] = []


def file_add(work_file: str):
    mkv = MKVFile(work_file)
    add_track = False
    name = path.splitext(work_file)[0]  # 获取文件名，无扩展名
    subs_list: list[str] = []  # 匹配的字幕文件
    for sub in subs[:]:
        if name in sub:
            subs_list.append(sub)
            subs.remove(sub)
    # 开始添加字幕文件
    for sub in subs_list:
        mkvtrack = MKVTrack(sub)
        info = sub.replace(name, "", 1).split(".")[
            1:-1
        ]  # 获取文件尾部名称
        count = len(info)
        if count == 2: # 符合jellyfin标注的格式 “语言名称.ISO639名称”
            mkvtrack.track_name = info[0]
            if "简" in info[0]:  # 如果是简体就设置为默认
                mkvtrack.default_track = True
            mkvtrack.language = info[1]
        elif count == 1: # 常见格式
            lang_zh_cn = ['chs', 'sc', 'zh', 'zh-cn', 'zh-Hans']
            lang_zh_tw = ['cht', 'tc', 'zh-tw', 'zh-Hant']
            if info[0] in lang_zh_cn:
                mkvtrack.track_name = '简体中文'
                mkvtrack.default_track = True
                info[0] = 'chi'
            if info[0] in lang_zh_tw:
                mkvtrack.track_name = '繁体中文'
                info[0] = 'chi'
            mkvtrack.language = info[0]
        mkv.add_track(mkvtrack)
        add_track = True

    if add_track:
        # 在文件目录新建output文件夹
        mkv.mux(f"./output/{work_file}")


def dir_add(dir_path: str):
    for file in listdir(dir_path):
        if file.endswith(".mkv"):
            mkvs.append(file)
        if file.endswith(".ass") or file.endswith(".srt"):
            subs.append(file)

    for mkv in mkvs:
        file_add(mkv)


def main():
    argc = len(argv)
    if argc < 2:
        print(f"Usage: python {argv[0]} <mkv and ass dir>")
        return
    work_path = argv[1]
    if path.isdir(work_path):
        chdir(work_path)
        dir_add(work_path)


if __name__ == "__main__":
    main()

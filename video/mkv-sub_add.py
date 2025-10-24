"""
添加mkv文件字幕，参数1为 文件夹
"""

from os import chdir, listdir, path
from sys import argv

from pymkv import MKVFile, MKVTrack
from rich.progress import track

mkvs: list[str] = []
subs: list[str] = []


def lang_code_convert(code: str, name: str = '') -> tuple[str, str]:
    """
    @param code: 语言代码
    @param name: 语言名称
    @return: (语言名称, ISO639名称)
    """
    if code == "":
        return name, "und"
    lang_zh_cn = ['chs', 'sc', 'zh', 'zh-cn', 'zh-hans', 'jpsc', 'gb']
    lang_zh_tw = ['cht', 'tc', 'zh-tw', 'zh-hant', 'jptc', 'big5']
    lang_jp = ['ja', 'jp']
    if code.lower() in lang_zh_cn:
        return '简体中文', 'chi'
    if code.lower() in lang_zh_tw:
        return '繁体中文', 'chi'
    if code.lower() in lang_jp:
        return "日语", "jpn"
    return name, code


def file_add(work_file: str):
    mkv = MKVFile(work_file)
    add_track = False
    name = path.splitext(work_file)[0]  # 获取文件名，无扩展名
    subs_list: list[str] = []  # 匹配的字幕文件
    for sub in subs[:]:
        if name.lower() in sub.lower():
            subs_list.append(sub)
            subs.remove(sub)
    # 开始添加字幕文件
    for sub in subs_list:
        mkvtrack = MKVTrack(sub)
        info = sub.replace(name, "", 1).split(".")[1:-1]  # 获取文件尾部名称
        count = len(info)
        if count == 2:  # 符合jellyfin标注的格式 “语言名称.ISO639名称”
            tmp = lang_code_convert(info[1], info[0])
        elif count == 1:  # 常见格式
            tmp = lang_code_convert(info[0])
        elif count == 0:
            # 无语言代码，默认为简体中文
            tmp = lang_code_convert("chs")
        else:  # 不符合格式
            print(f"文件 {sub} 无匹配格式，跳过")
            continue
        mkvtrack.track_name = tmp[0]
        mkvtrack.language = tmp[1]
        if "简" in tmp[0]:  # 如果是简体就设置为默认
            mkvtrack.default_track = True
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

    for mkv in track(mkvs, description="正在添加字幕"):
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

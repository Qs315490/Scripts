"""
转换mkv文件字幕，参数1为 文件 或 文件夹
"""

from sys import argv
from os import chdir, listdir, path, mkdir
from opencc import OpenCC

OUTPUT_PATH='./output'

def file_convert(work_file: str):
    with open(work_file, "r", encoding="utf-8") as f:
        content = f.read()
    content = OpenCC("t2s.json").convert(content)
    if not path.isdir(OUTPUT_PATH):
        mkdir(OUTPUT_PATH)
    with open(f"{OUTPUT_PATH}/{work_file}", "x", encoding="utf-8") as f:
        f.write(content)
    print(f"{work_file} 转换完成")


def dir_convert(dir_path: str):
    for file in listdir(dir_path):
        if file.endswith(".ass"):
            file_convert(file)


def main():
    argc = len(argv)
    if argc < 2:
        print(f"Usage: python {argv[0]} <input.ass>|<mkv_dir>")
        return

    if path.isfile(argv[1]):
        work_path = path.dirname(argv[1])
        chdir(work_path)
        file_convert(path.basename(argv[1]))
    else:
        work_path = argv[1]
        chdir(work_path)
        dir_convert(work_path)


if __name__ == "__main__":
    main()

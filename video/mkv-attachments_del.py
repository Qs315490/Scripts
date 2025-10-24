"""
剔除mkv附加文件，参数1为 文件 或 文件夹
"""

from os import chdir, listdir, path
from sys import argv

from pymkv import MKVFile
from rich.progress import track


def file_del(work_file: str):
    mkv = MKVFile(work_file)
    mkv.no_attachments()
    # 在文件目录新建output文件夹
    mkv.mux(f"./output/{work_file}")


def dir_del(dir_path: str):
    mkv_file = [file for file in listdir(dir_path) if file.endswith(".mkv")]

    for file in track(mkv_file, description="附件文件删除"):
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

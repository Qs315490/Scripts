import shutil
from os import PathLike, chdir, listdir, mkdir
from os.path import isdir
from pathlib import Path
from pprint import pprint
from xml.etree import ElementTree

from rich.progress import track

PATH:str = r""
if PATH == "":
    PATH = input("请输入路径：")


def find_nfo_file(path: PathLike[str]) -> Path:
    for file in listdir(path):
        if file.endswith(".nfo"):
            return path / Path(file)
    raise Exception("No nfo file found")


def get_media_nfo_year(path: PathLike[str]) -> str:
    result = find_nfo_file(path)
    with open(result, encoding="utf-8") as f:
        xml = ElementTree.parse(f)
    root = xml.getroot()
    result = root.find("year")
    if result is None:
        raise Exception("No year found")
    year = result.text
    if year is None:
        raise Exception("year found, but no text")
    return year


def mv_media(path: PathLike[str], year: str):
    if not isdir(year):
        mkdir(year)
    shutil.move(path, year)


FAIL_LIST = []


def main(path: PathLike[str]):
    chdir(path)
    # 遍历文件夹
    for file in track(listdir(path)):
        if not isdir(file):
            continue
        file_path = Path(file)
        try:
            result = get_media_nfo_year(file_path)
        except Exception as e:
            print(file, e)
            FAIL_LIST.append(f"{file}: {e}")
            continue
        print(file, result)
        mv_media(file_path, result)

    pprint(FAIL_LIST)


if __name__ == "__main__":
    main(Path(PATH))

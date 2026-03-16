import os
from functools import partial
from multiprocessing import Manager, Pool
from multiprocessing.managers import ListProxy
from typing import BinaryIO

from fontTools.ttLib import TTFont
from otf2ttf.cli import MAX_ERR, REVERSE_DIRECTION, otf_to_ttf
from psutil import cpu_count
from ttc2ttf import ttc2ttf
from ttf_rename import font_get_name

otf_to_ttf = partial(
    otf_to_ttf,
    max_err=MAX_ERR,
    reverse_direction=REVERSE_DIRECTION,
)

os.chdir(os.path.dirname(__file__))

INPUT_DIR = "./input"
OUTPUT_DIR = "./output"

os.mkdir(INPUT_DIR) if not os.path.exists(INPUT_DIR) else None
os.mkdir(OUTPUT_DIR) if not os.path.exists(OUTPUT_DIR) else None


def ttf2woff2(file_io: BinaryIO):
    try:
        font = TTFont(file_io)
        if font.sfntVersion == "OTTO":
            # 虽然 fonttools 可以处理 otf，但转换后的 woff2 字体会损坏，因此使用 otf2ttf
            otf_to_ttf(font)
    except Exception as e:
        print(e)
        return
    font.flavor = "woff2"

    return font


def font2woff2(file_path: str, fail_list: ListProxy):
    file_ext = os.path.splitext(file_path)[1].lower()
    match file_ext:
        case ".ttc":
            font_io_gen = ttc2ttf(file_path)
        case ".otf" | ".ttf":
            font_io_gen = [open(file_path, "rb")]
        case _:
            print(f"不支持的文件格式: {file_path}")
            return

    for i, file_io in enumerate(font_io_gen):
        font = ttf2woff2(file_io)
        if not font:
            fail_list.append(file_path)
            continue

        font_name = font_get_name(font)
        if font_name:
            file_name = f"{font_name}.woff2"
        else:
            file_name = os.path.basename(file_path)
            if i > 0:  # ttc 文件
                file_name = os.path.splitext(file_name)[0] + f"_{i}.woff2"
            else:  # otf/ttf 文件
                file_name = os.path.splitext(file_name)[0] + ".woff2"

        font.save(os.path.join(OUTPUT_DIR, file_name))
        font.close()
        # file_io.close()


def main():
    cpu_physical = cpu_count(logical=False)
    pool = Pool(processes=cpu_physical if cpu_physical else 1)
    fail_list: ListProxy[str] = Manager().list()
    for file in os.listdir(INPUT_DIR):
        pool.apply_async(font2woff2, (os.path.join(INPUT_DIR, file), fail_list))

    pool.close()
    pool.join()
    print(f"{len(fail_list)} 个文件转换失败")
    print(fail_list)


if __name__ == "__main__":
    main()

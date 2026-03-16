import os
from functools import partial
from multiprocessing import Manager, Pool

from fontTools.ttLib import TTFont
from otf2ttf.cli import MAX_ERR, REVERSE_DIRECTION, otf_to_ttf
from psutil import cpu_count

otf_to_ttf = partial(
    otf_to_ttf,
    max_err=MAX_ERR,
    reverse_direction=REVERSE_DIRECTION,
)

os.chdir(os.path.dirname(__file__))

input_dir = "./input"
output_dir = "./output"

os.mkdir(input_dir) if not os.path.exists(input_dir) else None
os.mkdir(output_dir) if not os.path.exists(output_dir) else None

def ttf2woff2(file: str, fail_list: list[str]):
    try:
        font = TTFont(os.path.join(input_dir, file))
        if font.sfntVersion == "OTTO":
            otf_to_ttf(font)
    except Exception as e:
        print(e)
        fail_list.append(file)
        print(f"转换失败: {file}")
        return
    font.flavor = "woff2"
    file = os.path.splitext(file)[0] + ".woff2"
    file = file.replace(" ", "_")
    font.save(os.path.join(output_dir, file))
    print(f"转换完成: {file} ")


def main():
    pool = Pool(processes=cpu_count(logical=False))
    fail_list = Manager().list()
    for file in os.listdir(input_dir):
        ext = os.path.splitext(file)[1].lower()
        match ext:
            case ".ttf" | ".otf":
                pool.apply_async(ttf2woff2, args=(file, fail_list))

    pool.close()
    pool.join()
    print(f"{len(fail_list)} 个文件转换失败")
    print(fail_list)


if __name__ == "__main__":
    main()

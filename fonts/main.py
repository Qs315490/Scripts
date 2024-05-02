import os
from multiprocessing import Pool, Manager
from fontTools.ttLib import TTFont

os.chdir(os.path.dirname(__file__))

input_dir = "./input"
output_dir = "./output"

os.mkdir(input_dir) if not os.path.exists(input_dir) else None
os.mkdir(output_dir) if not os.path.exists(output_dir) else None

def ttf2woff2(file, fail_list):
    try:
        font = TTFont(os.path.join(input_dir, file))
    except Exception as e:
        print(e)
        fail_list.append(file)
        print(f"转换失败: {file}")
        return
    font.flavor = "woff2"
    file = os.path.splitext(file)[0] + ".woff2"
    font.save(os.path.join(output_dir, file))
    print(f"转换完成: {file} ")


def main():
    pool = Pool(processes=4)
    fail_list = Manager().list([])
    for file in os.listdir(input_dir):
        pool.apply_async(ttf2woff2, args=(file, fail_list))
    pool.close()
    pool.join()
    print(f"{len(fail_list)} 个文件转换失败")
    print(fail_list)


if __name__ == "__main__":
    main()

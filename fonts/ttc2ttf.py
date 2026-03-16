#!/usr/bin/env python3

# First released as C++ program by Hiroyuki Tsutsumi
# as part of the free software suite “Beer”
# I thought porting it to Python could be both a challenge and useful

import os
from io import BytesIO
from struct import pack_into, unpack_from
from sys import argv, exit

from fontTools.ttLib import TTFont
from ttf_rename import font_get_name


def ceil4(n):
    """返回下一个 4 的倍数的整数"""
    return (n + 3) & ~3


def ttc_offset2ttf(buf: bytes, table_header_offset: int):
    """将 TTC 文件中的 TTF 文件偏移量转换为 TTF 文件"""

    table_count = unpack_from("!H", buf, table_header_offset + 0x04)[0]
    header_length = 0x0C + table_count * 0x10
    # print(f"\t标头长度: {header_length} Byte")

    table_length = 0
    for j in range(table_count):
        length = unpack_from("!L", buf, table_header_offset + 0x0C + 0x0C + j * 0x10)[0]
        table_length += ceil4(length)

    total_length = header_length + table_length
    new_buf = bytearray(total_length)
    header = unpack_from(header_length * "c", buf, table_header_offset)
    pack_into(header_length * "c", new_buf, 0, *header)
    current_offset = header_length

    for j in range(table_count):
        offset = unpack_from("!L", buf, table_header_offset + 0x0C + 0x08 + j * 0x10)[0]
        length = unpack_from("!L", buf, table_header_offset + 0x0C + 0x0C + j * 0x10)[0]
        pack_into("!L", new_buf, 0x0C + 0x08 + j * 0x10, current_offset)
        current_table = unpack_from(length * "c", buf, offset)
        pack_into(length * "c", new_buf, current_offset, *current_table)

        # table_checksum = sum(unpack_from("!"+("L"*length), new_buf, current_offset))
        # pack_into("!L", new_buf, 0x0C+0x04+j*0x10, table_checksum)

        current_offset += ceil4(length)
    return new_buf


def ttc2ttf(file_path: str):
    """将 TTC 文件拆分为多个 TTF"""

    in_file = open(file_path, "rb")
    buf = in_file.read()
    in_file.close()
    file_name = os.path.basename(file_path)

    if buf[:4] != b"ttcf":
        # end, so we don’t have to close the files or call exit() here
        print(f"文件 {file_name}.ttc 不是 TrueType 集合，原样输出")
        yield BytesIO(bytearray(buf))
        return

    ttf_count = unpack_from("!L", buf, 0x08)[0]
    # print(f"{file_name} 包含的 TTF 文件数量： {ttf_count}")

    ttf_offset_array = unpack_from("!" + ttf_count * "L", buf, 0x0C)
    for i in range(ttf_count):
        print(f"{file_name} 提取 TTF #{i + 1}:")
        table_header_offset = ttf_offset_array[i]
        # print(f"\t标头开始字节 {table_header_offset}")
        yield BytesIO(ttc_offset2ttf(buf, table_header_offset))


def main():
    os.chdir(os.path.dirname(__file__))
    input_dir = "./input"
    output_dir = "./output"
    os.mkdir(input_dir) if not os.path.exists(input_dir) else None
    os.mkdir(output_dir) if not os.path.exists(output_dir) else None
    if len(argv) == 2:
        file_name = argv[1]
        if not os.path.exists(file_name):
            exit("文件不存在")
        file_list = [file_name]
    else:
        file_list = os.listdir(input_dir)

    for i, file_name in enumerate(file_list):
        if not file_name.lower().endswith(".ttc"):
            continue

        print(f"处理文件 {file_name}...")
        ttf_buf_list = ttc2ttf(os.path.join(input_dir, file_name))
        base_name = os.path.splitext(os.path.basename(file_name))[0]
        for ttf_buf in ttf_buf_list:
            font = TTFont(ttf_buf)
            font_name = font_get_name(font)

            # 生成文件名
            if font_name:
                # 清理文件名中的非法字符
                safe_name = font_name.replace(" ", "_")
                file_new_name = f"{safe_name}.ttf"
            else:
                file_new_name = f"{base_name}_{i + 1}.ttf"

            output_path = os.path.join(output_dir, file_new_name)
            font.save(output_path)
            print(f"\n\t保存为: {file_new_name}")
            font.close()


if __name__ == "__main__":
    main()

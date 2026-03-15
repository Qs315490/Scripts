#!/usr/bin/env python3
import contextlib
import struct
import sys
import uuid
from argparse import ArgumentParser
from pathlib import Path

# 反向映射 GUID 到类型名称
guid_2_type = {
    # 官方 GPT 分区类型 GUID
    "EBD0A0A2-B9E5-4433-87C0-68B6B72699C7": "fat",
    "C12A7328-F81F-11D2-BA4B-00A0C93EC93B": "esp",
    "0FC63DAF-8483-4772-8E79-3D69D8477DE4": "linux",
    "0657FD6D-A4AB-43C4-84E5-0933C84B4F4F": "linux-swap",
    # Android 分区类型 GUID
    "2568845D-2332-4675-BC39-8FA5A4748D15": "bootloader",
    "49A4D17F-93A3-45C1-A0DE-F50B2EBE2599": "boot",
    "4177C722-9E92-4AAB-8644-43502BFD5506": "recovery",
    "EF32A33B-A409-486C-9141-9FFB711F6266": "misc",
    "20AC26BE-20B7-11E3-84C5-6CFDB94711E9": "metadata",
    "767941D0-2085-11E3-AD3B-6CFDB94711E9": "tertiary",
    "8F68CC74-C5E5-48DA-BE91-A0C8C15E9C80": "factory",
    "9FDAA6EF-4B3F-40D2-BA8D-BFF16BFB887B": "factory(alt)",
    "38F428E6-D326-425D-9140-6E0EA133647C": "system",
    "DC76DDA9-5AC1-491C-AF42-A82591580C0D": "data",
}


def parse_gpt_bin(filename):
    """
    解析 gpt.bin 文件并打印分区信息
    文件格式:
    - 魔数 (4字节): 0x6A8B0DA1
    - 起始 LBA (4字节)
    - 分区数量 (4字节)
    - 对每个分区:
        - 分区长度 (4字节, 有符号整数)
        - 分区标签 (72字节, UTF-16LE, 36个字符)
        - 分区类型 GUID (16字节, 小端)
        - 分区 GUID (16字节, 小端)
    """
    with open(filename, "rb") as f:
        # 读取文件头
        magic = struct.unpack("<I", f.read(4))[0]
        if magic != 0x6A8B0DA1:
            print(f"错误: 无效的魔数 0x{magic:08X}, 期望 0x6A8B0DA1")
            return False

        start_lba = struct.unpack("<I", f.read(4))[0]
        npart = struct.unpack("<I", f.read(4))[0]

        print("GPT 信息:")
        print(f"  魔数: 0x{magic:08X}")
        print(f"  起始 LBA: {start_lba}")
        print(f"  分区数量: {npart}")
        print()

        # 读取每个分区
        partitions = []
        for i in range(npart):
            # 读取分区长度
            length = struct.unpack("<i", f.read(4))[0]

            # 读取分区标签 (36个UTF-16LE字符 = 72字节)
            label_data = f.read(72)
            # 解码UTF-16LE并去除末尾的空字符
            label = label_data.decode("utf-16le").rstrip("\x00")

            # 读取分区类型 GUID (小端)
            type_guid_bytes = f.read(16)
            type_guid = uuid.UUID(bytes_le=type_guid_bytes)
            type_guid_str = str(type_guid).upper()

            # 读取分区 GUID (小端)
            part_guid_bytes = f.read(16)
            part_guid = uuid.UUID(bytes_le=part_guid_bytes)
            part_guid_str = str(part_guid).upper()

            # 查找分区类型名称
            type_name = guid_2_type.get(type_guid_str, "unknown")

            partitions.append(
                {
                    "index": i,
                    "length": length,
                    "label": label,
                    "type_guid": type_guid_str,
                    "type_name": type_name,
                    "part_guid": part_guid_str,
                }
            )

        # 打印分区信息
        print("分区列表:")
        print("-" * 100)
        print(
            f"{'索引':<4} {'长度':<12} {'标签':<20} {'类型':<15} {'分区GUID':<36} {'类型GUID':<36}"
        )
        print("-" * 100)

        for p in partitions:
            print(
                f"{p['index']:<4} {p['length']:<12} {p['label']:<20} "
                f"{p['type_name']:<15} {p['part_guid']:<36} {p['type_guid']}"
            )

        # 检查文件是否还有剩余数据
        remaining = f.read()
        if remaining:
            print(f"\n警告: 文件末尾还有 {len(remaining)} 字节未读取")

        return True


def main():
    parser = ArgumentParser(description="解析 gpt.bin 文件")
    parser.add_argument(
        "input",
        nargs="?",
        default="gpt.bin",
        help="输入的 gpt.bin 文件 (默认: gpt.bin)",
    )
    parser.add_argument("-o", "--output", help="输出到文件 (可选)")
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"错误: 文件 {args.input} 不存在")
        sys.exit(1)

    if args.output:
        # 如果指定了输出文件，将输出重定向到文件
        with open(args.output, "w", encoding="utf-8") as f:
            with contextlib.redirect_stdout(f):
                parse_gpt_bin(args.input)
        print(f"解析结果已保存到: {args.output}")
    else:
        parse_gpt_bin(args.input)


if __name__ == "__main__":
    main()

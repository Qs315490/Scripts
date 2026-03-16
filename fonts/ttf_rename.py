import os

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import NameRecord
from opencc import OpenCC


def filter_font_name(
    name_records: list[NameRecord],
) -> tuple[
    dict[int, list[NameRecord]],
    dict[int, list[NameRecord]],
    dict[int, list[NameRecord]],
]:
    """过滤字体名称"""
    chs_list: dict[int, list[NameRecord]] = {4: [], 1: [], 6: []}
    cht_list: dict[int, list[NameRecord]] = {4: [], 1: [], 6: []}
    english_list: dict[int, list[NameRecord]] = {4: [], 1: [], 6: []}
    allow_name_id = [1, 4, 6]

    for record in name_records:
        if record.nameID not in allow_name_id:
            continue
        match record.platformID:
            case 0:  # Unicode
                english_list[record.nameID].append(record)

            # Macintosh平台字体名称编码格式未知，暂不处理。会导致部分字体名称乱码
            # 一般情况下，乱码的字体都不支持Unicode编码，所以可以忽略
            # 字体名称乱码也方便于查找出不支持Unicode编码的字体
            # 适用于字体名称带 英文 的文件，毕竟不同编码相同的部分只有 ASCII 部分
            case 1:  # Macintosh
                match record.langID:
                    case 0:
                        english_list[record.nameID].append(record)
                    case 19:
                        cht_list[record.nameID].append(record)
                    case 20:
                        chs_list[record.nameID].append(record)

            case 3:  # Windows
                match record.langID:
                    case 0x0409:
                        english_list[record.nameID].append(record)
                    case 0x0404 | 0x0C04:
                        cht_list[record.nameID].append(record)
                    case 0x0804:
                        chs_list[record.nameID].append(record)
    return chs_list, cht_list, english_list


def font_get_name(font: TTFont, add_sub_family: bool = False):
    # 尝试获取字体名称
    name_record = font["name"]
    sub_family_name = name_record.getBestSubFamilyName()
    if sub_family_name is None:
        sub_family_name = ""
    (chs_list, cht_list, english_list) = filter_font_name(name_record.names)

    tmp_name = None
    for lang_list in (chs_list, cht_list, english_list):
        if tmp_name:
            break
        for record_list in lang_list.values():
            if tmp_name:
                break
            for record in record_list:
                tmp_name = record.toUnicode()
                if sub_family_name not in tmp_name and add_sub_family:
                    tmp_name += f"-{sub_family_name}"
                break

    return OpenCC("t2s.json").convert(tmp_name) if tmp_name else None


def main():
    os.chdir(os.path.dirname(__file__))
    input_dir = "./input"
    output_dir = "./output"
    os.mkdir(input_dir) if not os.path.exists(input_dir) else None
    os.mkdir(output_dir) if not os.path.exists(output_dir) else None

    ttf_list: list[str] = [
        file
        for file in os.listdir(input_dir)
        if file.endswith(".ttf") or file.endswith(".otf")
    ]
    for ttf_file in ttf_list:
        font = TTFont(os.path.join(input_dir, ttf_file))
        name = font_get_name(font)
        if name is None:
            print("No name found:", ttf_file)
            continue
        file_name = f"{name.replace(' ', '_')}.{ttf_file.split('.')[-1]}"
        # font.save(os.path.join(output_dir, file_name))
        print("Renamed:", file_name)


if __name__ == "__main__":
    main()

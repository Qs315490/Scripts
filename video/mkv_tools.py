from argparse import ArgumentParser
from os import chdir, listdir, path, system
from pymkv import MKVFile, MKVTrack

if __name__ == "__main__":
    parser = ArgumentParser(prog='mkv_tools', description='MKV 文件工具集合')
    subparsers = parser.add_subparsers(title='操作', dest='action')
    # del
    parser_del = subparsers.add_parser("del", help='删除mkv文件中的元素')
    sub_del = parser_del.add_subparsers(dest='object')
    # del audio2
    sub_del_audio2 = sub_del.add_parser('audio2', help="删除mkv文件中的第二音频轨")
    sub_del_audio2.add_argument('file', type=str, help='文件 或 文件夹 路径')
    # del subtitle
    sub_del_subtitle = sub_del.add_parser('subtitle', help="删除mkv文件中的字幕轨和附件")
    sub_del_subtitle.add_argument('file', type=str, help='文件 或 文件夹 路径')
    # del attachments
    sub_del_attachments = sub_del.add_parser('attachments', help="删除mkv文件中的附件")
    sub_del_attachments.add_argument('file', type=str, help='文件 或 文件夹 路径')
    # del title
    sub_del_title = sub_del.add_parser('title', help="删除mkv文件中的标题")
    sub_del_title.add_argument('file', type=str, help='文件 或 文件夹 路径')

    # add
    parser_add = subparsers.add_parser("add", help="向mkv文件添加元素")
    sub_add = parser_add.add_subparsers(dest='object')
    # add subtitle
    sub_add_subtitle = sub_add.add_parser('subtitle')
    sub_add_subtitle.add_argument('file', type=str, help='文件 或 文件夹 路径')

    # edit
    parser_edit = subparsers.add_parser("edit", help="编辑mkv文件元信息")
    sub_edit = parser_edit.add_subparsers(dest='object')
    # edit subtitles
    sub_edit_subtitle = sub_edit.add_parser(
        'subtitles',
        help="编辑mkv文件中的字幕轨名称。第三字幕轨为默认字幕，名称改为“简体中文”。第四字幕轨名称改为“繁体中文”。",
    )
    sub_edit_subtitle.add_argument('file', type=str, help='文件 或 文件夹 路径')

mkv_files = []
sub_files = []


def file_scan(file_path: str):
    """
    扫描文件，获取所有符合要求的文件
    :param file_path: 文件路径
    """
    file_name = file_path
    for file in listdir(file_path):
        if file_name in file:
            if file.endswith(".mkv"):
                mkv_files.append(file)
            if file.endswith(".ass") or file.endswith('.srt'):
                sub_files.append(file)


def dir_scan(dir_path: str, type_fitter: list[str]):
    """
    扫描文件夹，获取所有符合要求的文件
    :param dir_path: 文件夹路径
    :param fitter: 文件类型筛选器，如['mkv', 'subtitle']
    """
    for file in listdir(dir_path):
        if 'mkv' in type_fitter and file.endswith('.mkv'):
            mkv_files.append(file)
        if 'subtitle' in type_fitter and file.endswith('.ass') or file.endswith('.srt'):
            sub_files.append(file)


def scan_path(scan_path: str, type_fitter: list[str]):
    """
    扫描文件或文件夹，获取所有符合要求的文件
    :param scan_path: 文件或文件夹路径
    :param fitter: 文件类型筛选器，如 ['mkv', 'subtitle']
    """
    if path.isfile(scan_path):
        file_scan(scan_path)
    else:
        dir_scan(scan_path, type_fitter)


def audio2_del(file_path: str):
    scan_path(file_path, ['mkv'])
    for file_path in mkv_files:
        mkv = MKVFile(file_path)
        tracks: list[MKVTrack] = mkv.tracks
        flag = False
        for track in tracks[:]:
            if track.track_id == 2 and track.track_type == 'audio':
                mkv.tracks.remove(track)
                flag = True
        if flag:
            mkv.mux(f"./output/{file_path}")


def subtitle_del(file_path: str):
    scan_path(file_path, ['mkv'])
    for file_path in mkv_files:
        mkv = MKVFile(file_path)
        tracks: list[MKVTrack] = mkv.tracks
        flag = False
        for track in tracks[:]:
            if track.track_type == 'subtitles':
                mkv.tracks.remove(track)
                flag = True
        if flag:
            mkv.no_attachments()
            mkv.mux(f"./output/{file_path}")


def attachments_del(file_path: str):
    scan_path(file_path, ['mkv'])
    for file_path in mkv_files:
        mkv = MKVFile(file_path)
        tracks: list[MKVTrack] = mkv.tracks
        flag = False
        for track in tracks[:]:
            if track.track_type == "attachments":
                mkv.tracks.remove(track)
                flag = True
        if flag:
            mkv.mux(f"./output/{file_path}")


def title_del(file_path: str):
    scan_path(file_path, ['mkv'])
    for file_path in mkv_files:
        system(f'mkvpropedit --edit info -d title "{file_path}"')


def lang_code_convert(code: str, name: str = '') -> tuple[str, str]:
    """
    @param code: 语言代码
    @param name: 语言名称
    @return: (语言名称, ISO639名称)
    """
    if code == "":
        return name, "und"
    lang_zh_cn = ['chs', 'sc', 'zh', 'zh-cn', 'zh-hans']
    lang_zh_tw = ['cht', 'tc', 'zh-tw', 'zh-hant']
    lang_jp = ['ja', 'jp']
    if code.lower() in lang_zh_cn:
        return '简体中文', 'chi'
    if code.lower() in lang_zh_tw:
        return '繁体中文', 'chi'
    if code.lower() in lang_jp:
        return "日语", "jpn"
    return name, code


def subtitle_add(file_path: str):
    scan_path(file_path, ['mkv', 'subtitle'])
    for file_path in mkv_files:
        mkv = MKVFile(file_path)
        file_name = path.splitext(file_path)[0]
        sub_list: list[str] = []
        # 筛选字幕文件
        for sub_file in sub_files:
            if file_name in sub_file[:]:
                sub_list.append(sub_file)
                sub_files.remove(sub_file)

        # 开始添加字幕文件
        for sub_file in sub_list:
            mkvtrack = MKVTrack(file_name)
            info = sub_file.replace(file_name, "", 1).split(".")[
                1:-1
            ]  # 获取文件尾部名称
            count = len(info)
            if count == 2:  # 符合jellyfin标注的格式 “语言名称.ISO639名称”
                tmp = lang_code_convert(info[1], info[0])
            elif count == 1:  # 常见格式
                tmp = lang_code_convert(info[0])
            else:  # 不符合格式
                print(f"文件 {sub_file} 无匹配格式，跳过")
                continue
            mkvtrack.track_name = tmp[0]
            mkvtrack.language = tmp[1]
            if "简" in tmp[0]:  # 如果是简体就设置为默认
                mkvtrack.default_track = True
            mkv.add_track(mkvtrack)
            add_track = True

        if add_track:
            # 在文件目录新建output文件夹
            mkv.mux(f"./output/{file_path}")


def subtitle_edit(file_path: str):
    scan_path(file_path, ['mkv'])
    for file_path in mkv_files:
        system(
            'mkvpropedit --edit track:3 -s name="简体中文" -s flag-default=1 '
            f'--edit track:4 -s name="繁体中文" -s flag-default=0 "{file_path}"'
        )


def extract_subtitle(file_path: str):
    scan_path(file_path, ['mkv'])
    for file_path in mkv_files:
        file_name = path.splitext(file_path)[0]
        mkv = MKVFile(file_path)
        tracks: list[MKVTrack] = mkv.tracks
        for track in tracks:
            if track.track_type == "subtitles":
                assert isinstance(track.track_id, int)
                track_name = '.' + track.track_name if track.track_name else ""
                language = '.' + track.language if track.language else ""
                # 文件类型无法使用此库获取，默认 ass 类型
                system(
                    f'mkvextract {file_path} tracks {track.track_id - 1}:'
                    f'[{track.track_id}]{file_name}{track_name}{language}.ass'
                )

if __name__ == "__main__":
    work_path = ''
    args = parser.parse_args()
    if path.isfile(args.file):
        work_path = path.dirname(args.file)
    else:
        work_path = args.file
    chdir(work_path)
    match args.action:
        case 'del':
            match args.object:
                case 'audio2':
                    audio2_del(args.file)
                case 'subtitle':
                    subtitle_del(args.file)
                case 'attachments':
                    pass
                case 'title':
                    title_del(args.file)
        case 'add':
            match args.object:
                case 'subtitle':
                    subtitle_add(args.file)
        case 'edit':
            match args.object:
                case 'subtitle':
                    subtitle_edit(args.file)
        case 'extract':
            match args.object:
                case 'subtitle':
                    extract_subtitle(args.file)

from sys import argv
from os import path, popen, system
import json

if argv[1] is None:
	exit("请输入视频文件路径")

ffprobe_cmd = [
	"ffprobe",
	"-v", "warning",
	"-show_chapters",
	"-of", "json",
	"-i", f'"{argv[1]}"'
]
# 获取视频章节信息
video_chapters = popen(" ".join(ffprobe_cmd)).read()
chapters = json.loads(video_chapters)['chapters']


ffmpeg_cmd_temp = [
	"ffmpeg",
	"-v", "info",
	"-i", f'"{argv[1]}"',
	"-c", "copy"
]

for chapter in chapters:
	chapter_start = chapter['start_time']
	chapter_end = chapter['end_time']
	# 开始分割视频
	ffmpeg_cmd: list[str] = ffmpeg_cmd_temp.copy()
	ffmpeg_cmd.extend([
		"-ss", str(chapter_start),
		"-to", str(chapter_end),
		f'"{path.splitext(argv[1])[0]}_{chapter['tags']['title']}.mkv"'
	])
	system(" ".join(ffmpeg_cmd))
	
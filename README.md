# 这是什么？
自用脚本集

# 参数讲解
参数符号|说明
-|-
<>|必选参数
[]|可选参数
<1>\|<2>|1 或 2

PS: Windows批处理文件在处理多文件时是堆积到参数中的，列如：
```
file.bat file1 file2 file3
```
以上行为就是将 `file1`、`file2`、`file3` 三个文件作为参数传递给 `file.bat` 执行。与Windows10资源管理器行为相同

# 脚本列表

# 脚本介绍
## video
前置程序 `MKVToolNix`，需添加环境变量

## ass-zhconvert.py
```
python ass-zhconvert.py <input.ass>|<mkv_dir>
```
将繁体的字幕文件翻译为简体

### mkv-attachments_del.py
```
python mkv-attachments_del.py <input.mkv>|<mkv_dir>
```
剔除mkv附加文件

### mkv-name_del.bat
删除 mkv 视频的 `标题`，将文件拖到脚本上执行

### mkv-sub_add.py
```
python mkv-sub_add.py <mkv_and_ass_dir>
```
将 `input.ass` 字幕文件添加到 `input.mkv` 视频中，字幕文件前名称因与视频匹配，后缀前字符因为语言代码。
语言|代码
-|-
简体中文|'chs'、'sc'、'zh'、'zh-cn'、'zh-Hans'
繁体中文|'cht'、'tc'、'zh-tw'、'zh-Hant'

### mkv-sub_del.py
```
python mkv-sub_del.py <input.mkv>|<mkv_dir>
```
删除 mkv 视频的 `字幕` 和 `附加文件`


### mkv-sub_edit.bat
将第一字幕轨道名称设置为 `简体中文`，并设置为默认轨道。将第二字幕（如果存在）轨道名称设置为 `繁体中文`，并取消默认轨道。  
将文件拖到脚本上执行
### mkv-sub_ext.bat
获取轨道为2的字幕，将文件拖到脚本上执行

## fonts
### main.py
将 `input` 文件夹的 `ttf`、`otf` 字体转为 `woff2` 输出到 `output`

### ttc2ttf.py
```
python ttc2ttf.py font.ttc 
```
将 `ttc` 字体转为 `ttf`。默认保存到当前目录，使用 `字体源文件名+序号` 命名。

### ttf_rename.py
将 `input` 文件夹的 `ttf`、`otf` 字体重命名，输出到 `output`。获取到的字体名称不一定为中文，有可能会获取到乱码。字体名称可以使用 Windows字体查看器查看，或使用类似软件，至少比这个脚本获得的名称质量好。

## sys_backup
存放 Linux 系统备份和恢复的脚本

### backup.sh
```
backup.sh <dir> <file> [memory use]
```
参数|解释
-|-
`dir`|备份文件夹
`file`|输出文件名
`memory use`|内存占用，默认 1000M

默认压缩算法 `zstd` 存储文件为 `squashfs`

### restore.sh
```
restore.sh <file or device> <dir>
```
参数|解释
-|-
`file or device`|备份文件或设备
`dir`|恢复到文件夹

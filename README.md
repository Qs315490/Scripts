# 这是什么？
自用脚本集

# 参数讲解
参数符号|说明
-|-
<>|必选参数
[]|可选参数
{1\|2}|1 或 2

PS: Windows批处理文件在处理多文件时是堆积到参数中的，列如：
```
file.bat file1 file2 file3
```
以上行为就是将 `file1`、`file2`、`file3` 三个文件作为参数传递给 `file.bat` 执行。与Windows10资源管理器行为相同

# 脚本列表

# 脚本介绍
## fonts
### main.py
将 `input` 文件夹的 `ttf`、`otf`、`ttc` 字体转为 `woff2` 输出到 `output`
请检查输出的字体是否可用，通过 [FontEditor](https://kekee000.github.io/fonteditor/) 可以查看字体是否可用

### ttc2ttf.py
```
python ttc2ttf.py font.ttc 
```
将 `ttc` 字体转为 `ttf`。  
如果未获取到字体名称，程序会使用 `字体源文件名+序号` 命名。

### ttf_rename.py
将 `input` 文件夹的 `ttf`、`otf` 字体重命名，输出到 `output`。获取到的字体名称不一定为中文，有可能会获取到乱码。  
这个脚本获得的名称质量较差，建议使用 Windows字体查看器查看

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

@ECHO OFF
set PATH=%PATH%;C:\Program Files\MKVToolNix

for %%i in (%*) do (
    echo %%i
    :: 编辑第一个字幕名称 第二个字幕名称，设置默认标志关闭
    mkvpropedit --edit track:3 -s name="中文（简体）" -s flag-default=1 --edit track:4 -s name="中文（繁体）" -s flag-default=0 %%i
)

pause
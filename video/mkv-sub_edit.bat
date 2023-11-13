@ECHO OFF
set PATH=%PATH%;C:\Program Files\MKVToolNix

echo %1
:: 编辑第一个字幕名称 第二个字幕名称，设置默认标志关闭
mkvpropedit --edit track:3 -s name="中文（简体）" --edit track:4 -s name="中文（繁体）" -s flag-default=0 %1

pause
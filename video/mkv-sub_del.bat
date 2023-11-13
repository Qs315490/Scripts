@ECHO OFF
set PATH=%PATH%;C:\Program Files\MKVToolNix

GOTO EOF

echo %1
:: 删除所有字幕
mkvpropedit -o %1.output.mkv %1 -S

pause
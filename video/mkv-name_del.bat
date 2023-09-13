@ECHO OFF
set PATH=%PATH%;C:\Program Files\MKVToolNix
GOTO Start

:editmkv
echo %1
:: 编辑第一个字幕名称
mkvpropedit --edit info -d title %1
GOTO:EOF

:Start
for %%i in (%*) do call :editmkv %%i

pause
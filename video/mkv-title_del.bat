@ECHO OFF
set PATH=%PATH%;C:\Program Files\MKVToolNix

for %%i in (%*) do (
    echo %%i
    :: É¾³ý±êÌâ
    mkvpropedit --edit info -d title %1
)

pause
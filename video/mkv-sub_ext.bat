@ECHO OFF
set PATH=%PATH%;C:\Program Files\MKVToolNix

for %%i in (%*) do (
    echo %%i
    mkvextract %%i tracks 2:%%i.ass
)

pause
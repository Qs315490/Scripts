@ECHO OFF
set PATH=%PATH%;C:\Program Files\MKVToolNix

for %%i in (*.mkv) do (
    echo %%i
    :: ɾ������
    mkvpropedit --edit info -d title "%%i"
)

pause
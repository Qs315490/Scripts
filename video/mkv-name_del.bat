@ECHO OFF
set PATH=%PATH%;C:\Program Files\MKVToolNix

echo %1
:: �༭��һ����Ļ����
mkvpropedit --edit info -d title %1

pause
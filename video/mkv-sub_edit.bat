@ECHO OFF
set PATH=%PATH%;C:\Program Files\MKVToolNix
GOTO Start

:editmkv
echo %1
:: �༭��һ����Ļ���� �ڶ�����Ļ���ƣ�����Ĭ�ϱ�־�ر�
mkvpropedit --edit track:3 -s name="���ģ����壩" --edit track:4 -s name="���ģ����壩" -s flag-default=0 %1
GOTO:EOF

:Start
for %%i in (%*) do call :editmkv %%i

pause
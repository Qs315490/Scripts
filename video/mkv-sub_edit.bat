@ECHO OFF
set PATH=%PATH%;C:\Program Files\MKVToolNix

for %%i in (%*) do (
    echo %%i
    :: �༭��һ����Ļ���� �ڶ�����Ļ���ƣ�����Ĭ�ϱ�־�ر�
    mkvpropedit --edit track:3 -s name="���ģ����壩" -s flag-default=1 --edit track:4 -s name="���ģ����壩" -s flag-default=0 %%i
)

pause
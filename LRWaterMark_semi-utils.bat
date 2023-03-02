@echo off
echo 请使用ANSI编码
%echo 若提示找不到文件，请编辑LRWaterMark_semi-utils.bat以修改其指向的目录
cd %~dp0
python "main.py"
pause
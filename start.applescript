-- 获取当前文件路径
set curFilePath to POSIX path of (path to me as text)
-- 获取当前目录
set curDirectory to do shell script "dirname \"" & curFilePath & "\""
-- 执行
do shell script "cd '" & curDirectory & "'; python3 main.py"

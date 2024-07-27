-- get file path
set curFilePath to POSIX path of (path to me as text)
-- get directory path
set curDirectory to do shell script "dirname \"" & curFilePath & "\""
-- get command
set pyPath to "python3"
set cdCmd to "cd '" & curDirectory & "'"
set initCmd to "chmod +x ./install.sh && ./install.sh"
set execCmd to pyPath & " './main.py'"

tell application "Terminal"
	activate -- open terminal
	if not (exists window 1) then
		set newTab to do script ""
	end if
	do script cdCmd in window 1
	do script initCmd in window 1
	do script execCmd in window 1
end tell
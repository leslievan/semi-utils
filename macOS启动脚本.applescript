set scriptPath to POSIX path of ((path to me as text) & "::")
set initShPath to scriptPath & "init.sh"
set cmd to "cd " & quoted form of scriptPath & " && /bin/bash " & quoted form of initShPath

tell application "Terminal"
	activate
	do script cmd
end tell
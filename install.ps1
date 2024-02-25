# Download file
Invoke-WebRequest -Uri "https://exiftool.org/exiftool-12.69.zip" -OutFile exiftool.zip

# Create directory and extract the archive.
$null = New-Item -Path . -Name "exiftool" -ItemType "directory"
Expand-Archive -Path exiftool.zip -DestinationPath exiftool -Force

# Delete the archive
Remove-Item exiftool.zip
Rename-Item -Path ".\exiftool\exiftool(-k).exe" -NewName "exiftool.exe"

# Install Python dependencies
python3 -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

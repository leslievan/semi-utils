# 下载文件
Invoke-WebRequest -Uri https://exiftool.org/Image-ExifTool-12.85.tar.gz -OutFile Image-ExifTool-12.85.tar.gz

# 创建目录
mkdir exiftool

# 解压文件
Expand-Archive -Path Image-ExifTool-12.85.tar.gz -DestinationPath exiftool -Force

# 删除压缩包
Remove-Item Image-ExifTool-12.85.tar.gz

# 下载 python 依赖
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
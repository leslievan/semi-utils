#!/bin/bash

# 下载文件
curl -O https://exiftool.org/Image-ExifTool-12.60.tar.gz

# 创建目录
mkdir -p ./exiftool

# 解压文件
tar -xzf Image-ExifTool-12.60.tar.gz -C ./exiftool --strip-components=1

# 删除压缩包
rm Image-ExifTool-12.60.tar.gz

# 下载 python 依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
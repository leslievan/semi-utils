#!/bin/bash

EXIFTOOL_FILE_NAME="Image-ExifTool-12.92.tar.gz"
EXIFTOOL_FILE_DOWNLOAD_URL="http://file.lsvm.xyz/Image-ExifTool-12.92.tar.gz"

if [ -f "inited" ]; then
  echo "已完成初始化, 开始运行(如需重新初始化, 请删除 inited 文件)"
  exit 0
fi

# 下载文件
curl -O $EXIFTOOL_FILE_DOWNLOAD_URL

# 测试 gzip 压缩的有效性
if ! gzip -t "$EXIFTOOL_FILE_NAME"; then
    echo "下载的 ExifTool gzip 压缩文件格式不正确"
    echo "请检查 url 的有效性： $EXIFTOOL_FILE_DOWNLOAD_URL"
    echo "当前下载的 ExifTool gzip 的格式为："
    file "$EXIFTOOL_FILE_NAME"
    echo "安装未完成，初始化脚本中断"
    exit 1
fi

# 创建目录
mkdir -p ./exiftool

# 解压文件
tar -xzf "$EXIFTOOL_FILE_NAME" -C ./exiftool --strip-components=1

# 删除压缩包
rm "$EXIFTOOL_FILE_NAME"

# 下载 python 依赖
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 初始化完成
touch inited
echo "初始化完成, inited 文件已生成, 如需重新初始化, 请删除 inited 文件"
exit 0

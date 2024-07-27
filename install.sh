#!/bin/bash

if [ -f 'inited' ]; then
  echo '已完成初始化, 开始运行(如需重新初始化, 请删除 inited 文件)'
  exit 0
fi

# 下载文件
curl -O http://file.lsvm.xyz/Image-ExifTool-12.92.tar.gz


# 创建目录
mkdir -p ./exiftool

# 解压文件
tar -xzf Image-ExifTool-12.92.tar.gz -C ./exiftool --strip-components=1

# 删除压缩包
rm Image-ExifTool-12.92.tar.gz

# 下载 python 依赖
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 初始化完成
touch inited
echo '初始化完成, inited 文件已生成, 如需重新初始化, 请删除 inited 文件'
exit 0

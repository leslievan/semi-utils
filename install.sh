#!/bin/bash

if [ -f 'inited' ]; then
  echo '已完成初始化, 开始运行(如需重新初始化, 请删除 inited 文件)'
  exit 0
fi

download_file_name='Image-ExifTool-12.92.tar.gz'

# 优先镜像链接下载
curl -O http://file.lsvm.xyz/$download_file_name

if [ ! -f $download_file_name ]; then
  curl -O https://exiftool.org/$download_file_name
fi

if [ ! -f $download_file_name ]; then
  echo '下载失败,请检查网络连接状态或下载链接是否有效'
  exit 1
fi

# 创建目录
mkdir -p ./exiftool

# 解压文件
tar -xzf $download_file_name -C ./exiftool --strip-components=1

# 删除压缩包
rm $download_file_name

# 下载 python 依赖
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 初始化完成
touch inited
echo '初始化完成, inited 文件已生成, 如需重新初始化, 请删除 inited 文件'
exit 0

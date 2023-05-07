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
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 找到 python3 路径
outdir=$(where python3)
if [ $? -ne 0 ]; then
  echo "找不到 python3 路径"
  exit 1
fi

# 将 #!+python3 路径写入 main.py 的首行
sed -i "1s|^.*$|#!${outdir}|" main.py
if [ $? -ne 0 ]; then
  echo "修改 main.py 首行失败"
  exit 1
fi

# 给 main.py 添加执行权限
chmod +x main.py
if [ $? -ne 0 ]; then
  echo "添加 main.py 执行权限失败"
  exit 1
fi

# 添加软链接到 ~/.local/bin/semi-utils
mkdir -p ~/.local/bin/
ln -s "$(pwd)/main.py" ~/.local/bin/semi-utils
if [ $? -ne 0 ]; then
  echo "添加软链接失败"
  exit 1
fi

echo "semi-utils 安装成功"
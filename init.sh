#!/bin/bash
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# 检测操作系统
OS="$(uname -s)"
ARCH="$(uname -m)"

echo -e "${BOLD}${BLUE}🚀 开始初始化项目环境${NC}\n"

# 检查支持的系统
case "$OS" in
    Linux*)     PLATFORM='Linux';;
    Darwin*)    PLATFORM='macOS';;
    CYGWIN*|MINGW*|MSYS*)
                echo -e "${RED}✗  Windows 请使用 init.bat 脚本${NC}"
                exit 1
                ;;
    *)          echo -e "${RED}✗  不支持的操作系统: $OS${NC}"; exit 1;;
esac

echo -e "${GREEN}✓  检测到系统: ${BOLD}$PLATFORM ($ARCH)${NC}"

# 检查 Python 版本
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓  Python 已安装, 版本: ${BOLD}$PYTHON_VERSION${NC}"

# 创建虚拟环境
if [ ! -d ".venv" ]; then
    echo -e "${GREEN}-  创建虚拟环境...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✓  虚拟环境创建成功${NC}"
else
    echo -e "${GREEN}✓  虚拟环境已存在${NC}"
fi

# 激活虚拟环境
echo -e "${GREEN}-  正在激活虚拟环境...${NC}"
source .venv/bin/activate
echo -e "${GREEN}✓  虚拟环境已激活${NC}"

# 安装依赖
echo -e "${GREEN}-  安装项目依赖...${NC}"
pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple \
    -r requirements.txt
echo -e "${GREEN}✓  依赖安装完成${NC}"

# 检查并安装 ExifTool
echo ""
echo -e "${GREEN}-  检查 ExifTool 工具...${NC}"

if command -v exiftool &> /dev/null; then
    EXIFTOOL_VERSION=$(exiftool -ver)
    echo -e "${GREEN}✓  ExifTool 已安装 (系统命令), 版本: ${BOLD}$EXIFTOOL_VERSION${NC}"
elif [ -f "./exiftool/exiftool" ]; then
    EXIFTOOL_VERSION=$(./exiftool/exiftool -ver)
    echo -e "${GREEN}✓  ExifTool 已安装 (本地), 版本: ${BOLD}$EXIFTOOL_VERSION${NC}"
else
    echo -e "${YELLOW}!  ExifTool 未检测到，开始自动安装...${NC}"

    # 获取最新版本号
    echo -e "${GREEN}-  正在查询最新版本...${NC}"
    LATEST_VERSION=$(curl -s https://exiftool.org/ver.txt 2>/dev/null || echo "13.54")
    echo -e "${GREEN}✓  最新版本: ${BOLD}$LATEST_VERSION${NC}"

    # 创建 exiftool 目录
    mkdir -p exiftool
    cd exiftool

    # 下载 ExifTool (macOS/Linux 使用 Perl 版本)
    EXIFTOOL_URL="https://exiftool.org/Image-ExifTool-${LATEST_VERSION}.tar.gz"
    echo -e "${GREEN}-  正在下载 ExifTool $LATEST_VERSION...${NC}"

    if command -v curl &> /dev/null; then
        curl -L -o exiftool.tar.gz "$EXIFTOOL_URL" --progress-bar
    elif command -v wget &> /dev/null; then
        wget -O exiftool.tar.gz "$EXIFTOOL_URL" --show-progress 2>/dev/null || wget -O exiftool.tar.gz "$EXIFTOOL_URL"
    else
        echo -e "${RED}✗  需要 curl 或 wget 来下载文件${NC}"
        exit 1
    fi

    # 解压
    echo -e "${GREEN}-  正在解压...${NC}"
    tar -xzf exiftool.tar.gz --strip-components=1
    rm exiftool.tar.gz

    # 设置可执行权限
    chmod +x exiftool

    cd ..

    echo -e "${GREEN}✓  ExifTool $LATEST_VERSION 安装完成${NC}"
fi

echo ""
echo -e "${BOLD}${GREEN}✅  环境初始化完成${NC}"
echo -e "${BOLD}${BLUE}🚀  开始启动 Semi-Utils Pro${NC}\n"

python3 ./app.py

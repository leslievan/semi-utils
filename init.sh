#!/bin/bash
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BOLD}${BLUE}🚀 开始初始化项目环境${NC}\n"

# 检查 Python 版本（项目要求 >= 3.13）
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗  未找到 python3，请先安装 Python 3.13 及以上版本${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PY_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 13 ]; }; then
    echo -e "${RED}✗  当前 python3 版本为 ${BOLD}$PYTHON_VERSION${NC}${RED}，但本项目要求 Python >= 3.13${NC}"
    echo -e "${YELLOW}   推荐改用 uv 运行（会自动安装 3.13）：${BOLD}uv run app.py${NC}"
    echo -e "${YELLOW}   或安装 Python 3.13 后重试。${NC}"
    exit 1
fi
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

# 检查 exiftool（读取照片 EXIF 必需，是独立命令行程序，pip 无法安装）
echo -e "${GREEN}-  检查 exiftool...${NC}"
if command -v exiftool &> /dev/null; then
    echo -e "${GREEN}✓  exiftool 已安装${NC}"
else
    echo -e "${YELLOW}!  未检测到 exiftool（读取 EXIF 必需，缺失会导致水印没有文字和 Logo）${NC}"
    if [[ "$OSTYPE" == "darwin"* ]] && command -v brew &> /dev/null; then
        echo -e "${GREEN}-  通过 Homebrew 安装 exiftool...${NC}"
        brew install exiftool || {
            echo -e "${RED}✗  brew 安装 exiftool 失败，请手动安装：https://exiftool.org${NC}"
            exit 1
        }
        echo -e "${GREEN}✓  exiftool 安装完成${NC}"
    else
        echo -e "${RED}✗  请手动安装 exiftool 后重试：${NC}"
        echo -e "${YELLOW}     macOS:  brew install exiftool${NC}"
        echo -e "${YELLOW}     Linux:  sudo apt install libimage-exiftool-perl${NC}"
        echo -e "${YELLOW}     其他:   https://exiftool.org${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${BOLD}${GREEN}✅  环境初始化完成${NC}"
echo -e "${BOLD}${BLUE}🚀  开始启动 Semi-Utils Pro${NC}\n"

python3 ./app.py

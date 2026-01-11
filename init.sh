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

echo ""
echo -e "${BOLD}${GREEN}✅  环境初始化完成${NC}"
echo -e "${BOLD}${BLUE}🚀 开始启动 Semi-Utils Pro${NC}\n"

python3 ./app.py

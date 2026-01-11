#!/bin/bash
set -e
echo "🚀 开始初始化项目环境"
PYTHON_VERSION=$(python3 --version 2>&1 awk "{print $2}")
echo "✓ Python 已安装, 版本: $PYTHON_VERSION"

if ! command -v poetry &> /dev/null; then
  echo "📦 Poetry 未安装, 正在安装..."
  curl -sSL https://file.lsvm.xyz/release/poetry/latest | python3 -
  export PATH="$HOME/.local/bin:$PATH"
else
  echo "✓ Poetry 已安装: $(poetry --version)"
fi

poetry config virtualenvs.in-project true
echo "💡 安装项目依赖"
poetry install --no-root
echo ""
echo "✅ 环境初始化完成"

source .venv/bin/activate
echo "✅ 虚拟环境激活成功"
echo "🚀 开始启动 Semi-Utils Pro"
poetry run python ./app.py
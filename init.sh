#!/bin/bash
set -e
echo "🚀 开始初始化项目环境"
PYTHON_VERSION=$(python --version 2>&1 awk '{print $2}')
echo "✓ Python 已安装, 版本: $PYTHON_VERSION"

if ! command -v poetry &> /dev/null; then
  echo "📦 Poetry 未安装, 正在安装..."
  curl -sSL https://install.python-poetry.org | python3 -
  export PATH="$HOME/.local/bin:$PATH"
else
  echo "✓ Poetry 已安装: $(poetry --version)"
fi

poetry config virtualenvs.in-project true
echo "💡 安装项目依赖"
poetry install

echo ""
echo "✅ 环境初始化完成"
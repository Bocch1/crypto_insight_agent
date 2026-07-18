#!/bin/bash

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║     🎸 Crypto Insight Agent            ║"
echo "║     加密货币智能分析萝卜子              ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未检测到 Python3，请先安装"
    exit 1
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 首次运行，正在创建虚拟环境..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📥 检查依赖..."
pip install -r requirements.txt -q
echo "✅ 依赖已就绪"

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  未检测到 .env 文件"
    echo "📝 正在从模板创建..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请编辑填入 API Key 后重新运行"
fi

echo ""
echo "🌐 正在启动..."
echo "📍 地址: http://localhost:8501"
echo "💡 按 Ctrl+C 停止"
echo ""

streamlit run src/web_app.py
@echo off
chcp 65001 >nul
title Crypto Insight Agent

echo.
echo ╔══════════════════════════════════════════╗
echo ║     🎸 Crypto Insight Agent            ║
echo ║     加密货币智能分析萝卜子              ║
echo ╚══════════════════════════════════════════╝
echo.

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未检测到 Python，请先安装 Python 3.10+
    echo    下载地址: https://www.python.org/downloads/
    pause
    exit /b
)

:: 检查虚拟环境
if not exist "venv" (
    echo 📦 首次运行，正在创建虚拟环境...
    python -m venv venv
    echo ✅ 虚拟环境创建完成
)

:: 激活虚拟环境
call venv\Scripts\activate

:: 安装依赖
echo 📥 检查依赖...
pip install -r requirements.txt -q
echo ✅ 依赖已就绪

:: 检查 .env 文件
if not exist ".env" (
    echo.
    echo ⚠️  未检测到 .env 文件
    echo 📝 正在从模板创建...
    copy .env.example .env
    echo ✅ 已创建 .env 文件，请编辑填入 API Key 后重新运行
    echo.
    echo 💡 或者启动后在网页左侧「API 设置」中填写
    start notepad .env
)

echo.
echo 🌐 正在启动，浏览器打开后即可使用...
echo 📍 地址: http://localhost:8501
echo 💡 按 Ctrl+C 停止
echo.

streamlit run src/web_app.py
pause
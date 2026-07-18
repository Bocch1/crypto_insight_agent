@echo off
title Crypto Insight Agent

echo.
echo ==========================================
echo      Crypto Insight Agent
echo ==========================================
echo.

:: check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found
    echo Please install Python 3.10+
    pause
    exit /b
)

:: check venv
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    echo [OK] Created
)

:: activate venv
call venv\Scripts\activate

:: install dependencies
echo [INFO] Checking dependencies...
pip install -r requirements.txt -q
echo [OK] Ready

:: check .env
if not exist ".env" (
    echo.
    echo [WARN] .env file not found
    echo [INFO] Copying from .env.example...
    copy .env.example .env
    echo [OK] Created .env file
)

echo.
echo Starting...
echo URL: http://localhost:8501
echo Press Ctrl+C to stop
echo.

streamlit run src/web_app.py
pause
@echo off
REM GenAI Stack Backend Setup Script for Windows

echo 🚀 Setting up GenAI Stack Backend...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is required but not installed.
    exit /b 1
)

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo ⬇️ Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create necessary directories
echo 📁 Creating directories...
if not exist "chroma_data" mkdir chroma_data
if not exist "logs" mkdir logs

REM Copy environment file if it doesn't exist
if not exist ".env.local" (
    echo 📝 Creating .env.local file from template...
    copy .env .env.local
    echo ⚠️ Please update .env.local with your actual API keys and secrets
) else (
    echo ✅ .env.local file already exists
)

echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Update .env.local file with your API keys
echo 2. Start the server: uvicorn app.main:app --reload
echo 3. Visit http://localhost:8000/docs for API documentation

pause
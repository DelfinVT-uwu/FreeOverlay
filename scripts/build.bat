@echo off
REM Build script for FreeOverlay on Windows
REM Usage: scripts\build.bat

setlocal enabledelayedexpansion

echo ========================================
echo 🚀 FreeOverlay Build Script
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found in PATH!
    echo    Install Python from https://www.python.org/
    echo    Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python version: %PYTHON_VERSION%
echo.

REM Check PyInstaller
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing PyInstaller...
    python -m pip install PyInstaller
)

REM Install dependencies
echo 📦 Installing dependencies...
python -m pip install -q -r python\requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies!
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

REM Run build
echo 🔨 Building executable...
python scripts/build.py
if errorlevel 1 (
    echo ❌ Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ Build completed successfully!
echo ========================================
echo.
echo 📁 Output directory: dist\
echo 📦 Executable: dist\FreeOverlay.exe
echo.
pause

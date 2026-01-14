@echo off
echo ============================================
echo    FreeVR Overlay - Cyber Watch v9
echo    OpenGL Textures - Sin Flicker
echo ============================================
echo.

if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
    echo.
    echo Instalando dependencias...
    venv\Scripts\pip install -r requirements.txt
    echo.
)

echo Iniciando Cyber Watch...
venv\Scripts\python cyber_watch.py

pause

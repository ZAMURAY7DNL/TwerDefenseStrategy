@echo off
chcp 65001 >nul
echo 🔧 Iniciando Inspector de Tactical Defense...
echo.

REM Obtener directorio del script
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."

cd /d "%PROJECT_DIR%"

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no está instalado o no está en PATH
    echo Por favor instala Python 3.8+ desde https://python.org
    pause
    exit /b 1
)

echo ✅ Python detectado
echo 📁 Directorio del proyecto: %PROJECT_DIR%
echo.

REM Ejecutar inspector
python dev_tools/inspector.py

if errorlevel 1 (
    echo.
    echo ❌ El inspector cerró con errores
    pause
)

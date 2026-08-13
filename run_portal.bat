@echo off
REM ============================================================
REM Medical Device Change Tool - Web Portal Launcher
REM ============================================================
chcp 65001 > nul
setlocal

cd /d "%~dp0"

echo.
echo ============================================================
echo   Medical Device Change Assessment Tool - Web Portal
echo ============================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Creating virtual environment...
    python -m venv .venv
)

".venv\Scripts\python.exe" -m pip show streamlit deep-translator >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [INFO] Installing required packages...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)

echo.
echo Starting portal... Access it at:
echo   http://localhost:8501           (this PC only)
echo   http://%COMPUTERNAME%:8501      (same network, if firewall allows)
echo.

".venv\Scripts\streamlit.exe" run app.py --server.address 0.0.0.0 --server.port 8501

pause

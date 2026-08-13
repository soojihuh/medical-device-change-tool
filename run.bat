@echo off
REM ============================================================
REM Medical Device Change Tool - Windows Quick Run Script
REM ============================================================
chcp 65001 > nul
setlocal

cd /d "%~dp0"

echo.
echo ============================================================
echo   Medical Device Change Assessment Tool
echo ============================================================
echo.

REM 1. Python check
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo         Please install Python from https://www.python.org/downloads/
    echo         and check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM 2. Install dependencies if needed
python -c "import docx" 2>nul
if %ERRORLEVEL% neq 0 (
    echo [INFO] Installing required packages...
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install python-docx.
        pause
        exit /b 1
    )
)

REM 3. Menu
echo Select mode:
echo   [1] Interactive mode  (answer step-by-step)
echo   [2] Config file mode  (use example_config.json)
echo   [3] Run tests
echo   [Q] Quit
echo.
set /p MODE="Enter choice: "

if /i "%MODE%"=="1" (
    python main.py
) else if /i "%MODE%"=="2" (
    python main.py --config example_config.json
) else if /i "%MODE%"=="3" (
    python test.py
) else (
    echo Bye.
    exit /b 0
)

echo.
echo Done. Output files are in the output\ folder.
pause

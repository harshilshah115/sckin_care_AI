@echo off
echo ========================================
echo AI Backend Diagnostic Tool
echo ========================================
echo.

cd /d "d:\Harshil Projects\Sckin Care\backend"

echo [1/4] Checking virtual environment...
if exist "venv\Scripts\activate.bat" (
    echo ✓ Virtual environment found
) else (
    echo ✗ Virtual environment NOT found
    echo Please create it with: python -m venv venv
    pause
    exit /b 1
)

echo.
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [3/4] Checking installed packages...
echo.
pip list | findstr /i "google"
echo.

echo.
echo [4/4] Installing/Upgrading google-genai...
echo.
pip install --upgrade google-genai==0.2.2

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Now restart your Django server:
echo   python manage.py runserver
echo.
pause

@echo off
echo ========================================
echo Restarting Django Server
echo ========================================
echo.

cd /d "d:\Harshil Projects\Sckin Care\backend"

echo [1] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [2] Stopping any running Django servers...
echo Press CTRL+C if server is running in another window
echo.

echo [3] Starting Django server...
echo.
python manage.py runserver

pause

@echo off
REM Startup script for Etsy Order Automation Web Interface (Windows)

echo =========================================
echo   Etsy Order Automation - Web Interface
echo =========================================
echo.

REM Check if virtual environment exists
if not exist "etsy_env" (
    echo Creating virtual environment...
    python -m venv etsy_env
)

REM Activate virtual environment
echo Activating virtual environment...
call etsy_env\Scripts\activate.bat

REM Install/update requirements
echo Installing dependencies...
pip install -q -r requirements.txt

echo.
echo Starting web application...
echo The app will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo =========================================
echo.

REM Start Streamlit
streamlit run web_app.py

pause

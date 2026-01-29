@echo off
echo ====================================================================
echo INSTALLING DEPENDENCIES FOR SCM CHATBOT
echo ====================================================================
echo.

cd /d "%~dp0"

echo This will install all required packages to your Python environment.
echo.
echo Choose installation method:
echo.
echo 1. Install to SYSTEM Python (recommended if venv doesn't work)
echo 2. Install to VIRTUAL ENVIRONMENT (recommended for isolation)
echo.
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" goto SYSTEM
if "%choice%"=="2" goto VENV
echo Invalid choice. Exiting.
pause
exit

:SYSTEM
echo.
echo Installing to system Python...
echo ====================================================================
pip install pandas numpy scikit-learn groq gradio python-dotenv langchain langchain-groq langchain-core sentence-transformers
echo.
echo ====================================================================
echo ✅ Installation complete!
echo.
echo Now run: python main.py
echo ====================================================================
pause
exit

:VENV
echo.
echo Setting up virtual environment...
echo ====================================================================
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install pandas numpy scikit-learn groq gradio python-dotenv langchain langchain-groq langchain-core sentence-transformers

echo.
echo ====================================================================
echo ✅ Installation complete!
echo.
echo To use the virtual environment:
echo 1. Run: venv\Scripts\activate
echo 2. Then run: python main.py
echo.
echo OR just double-click START_HERE.bat
echo ====================================================================
pause

@echo off
echo ====================================================================
echo SCM CHATBOT - GUARANTEED START SCRIPT
echo ====================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

echo [Step 1/5] Checking virtual environment...
if not exist "venv\Scripts\python.exe" (
    echo Virtual environment not found. Creating new one...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment!
        echo.
        echo Falling back to system Python...
        goto INSTALL_SYSTEM
    )
)

echo [Step 2/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo WARNING: Could not activate venv. Using system Python.
    goto INSTALL_SYSTEM
)

echo Virtual environment activated!
echo Using: venv\Scripts\python.exe
echo.

echo [Step 3/5] Installing dependencies to virtual environment...
venv\Scripts\pip.exe install pandas numpy scikit-learn groq gradio python-dotenv langchain langchain-groq langchain-core sentence-transformers --quiet --upgrade
goto CHECK_API

:INSTALL_SYSTEM
echo [Step 3/5] Installing dependencies to system Python...
pip install pandas numpy scikit-learn groq gradio python-dotenv langchain langchain-groq langchain-core sentence-transformers --quiet --upgrade

:CHECK_API
echo.
echo [Step 4/5] Checking GROQ API Key...
if not exist .env (
    echo WARNING: .env file not found!
    echo Creating template...
    echo GROQ_API_KEY=your_api_key_here > .env
    echo.
    echo IMPORTANT: Edit .env file and add your Groq API key from:
    echo https://console.groq.com/
    echo.
    echo Press any key to continue anyway (Legacy mode will work)...
    pause > nul
)

echo.
echo [Step 5/5] Starting SCM Chatbot...
echo ====================================================================
echo.
echo 🚀 Application starting...
echo 📱 Open browser at: http://localhost:7860
echo 🛑 Press Ctrl+C to stop
echo.
echo ====================================================================
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ====================================================================
    echo ERROR: Application failed to start!
    echo ====================================================================
    echo.
    pause
)

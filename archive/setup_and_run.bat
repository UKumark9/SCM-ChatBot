@echo off
echo ========================================
echo SCM Chatbot Setup and Run
echo ========================================

REM Activate virtual environment
echo.
echo [1/4] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if activation worked
if errorlevel 1 (
    echo ERROR: Virtual environment not found!
    echo Creating new virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM Install dependencies
echo.
echo [2/4] Installing dependencies...
pip install pandas numpy scikit-learn groq gradio python-dotenv langchain langchain-groq langchain-core --quiet

REM Check API key
echo.
echo [3/4] Checking GROQ_API_KEY...
if not exist .env (
    echo WARNING: .env file not found!
    echo Creating template .env file...
    echo GROQ_API_KEY=your_api_key_here > .env
    echo Please edit .env and add your Groq API key
    pause
)

REM Run the application
echo.
echo [4/4] Starting SCM Chatbot...
echo.
echo ========================================
echo Opening UI at http://localhost:7860
echo Press Ctrl+C to stop
echo ========================================
echo.

python main.py

pause

@echo off
echo ====================================================================
echo FORCING AGENTIC MODE - All Modes Enabled
echo ====================================================================
echo.

cd /d "%~dp0"

echo This will start the application with ALL modes initialized.
echo You will be able to switch between Agentic, Enhanced, and Legacy modes.
echo.

python main.py --init-all

echo.
echo ====================================================================
echo If you see "Agent Orchestrator initialized" above, it worked!
echo ====================================================================
pause

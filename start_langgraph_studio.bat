@echo off
REM LangGraph Studio Launcher for Windows
REM Automatically activates venv and starts LangGraph dev server

echo ========================================
echo  LangGraph Studio Launcher
echo ========================================
echo.

REM Activate virtual environment
echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment
    echo Make sure venv exists: python -m venv venv
    pause
    exit /b 1
)
echo      Done!
echo.

REM Check if langgraph is installed
echo [2/3] Checking LangGraph installation...
python -c "import langgraph" 2>nul
if errorlevel 1 (
    echo ERROR: LangGraph not installed
    echo Run: pip install -r requirements.txt
    pause
    exit /b 1
)
echo      Done!
echo.

REM Start LangGraph Studio
echo [3/3] Starting LangGraph Studio...
echo.
echo ========================================
echo  LangGraph Studio is starting!
echo ========================================
echo.
echo  Local:   http://localhost:8123
echo  API:     http://localhost:8123/docs
echo.
echo  Press Ctrl+C to stop
echo ========================================
echo.

REM Try using langgraph command if in PATH, otherwise use python -m
where langgraph >nul 2>nul
if %errorlevel%==0 (
    langgraph dev
) else (
    echo Using fallback method (langgraph not in PATH)...
    python -c "from langgraph_cli.cli import cli; cli()" dev
)

pause

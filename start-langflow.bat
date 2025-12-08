@echo off
echo Starting LangFlow Visual Builder...
echo.
echo Using Python 3.11 venv at: venv-langflow
echo.
call "venv-langflow\Scripts\activate.bat"
langflow run --host 127.0.0.1 --port 7860
pause

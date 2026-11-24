@echo off
rem Startet den YouTube Downloader (Windows)
cd /d "%~dp0"
if not exist .venv (
  py -3 -m venv .venv || python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -q --upgrade -r requirements.txt
python app.py
pause

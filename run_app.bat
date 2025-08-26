@echo off
cd %~dp0
call .venv\Scripts\activate.bat
python app_gui.py
pause

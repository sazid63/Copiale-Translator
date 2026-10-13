@echo off
REM Copiale Translator (Windows) — double-click to open.
cd /d "%~dp0"
python copiale_gui.py
if errorlevel 1 pause

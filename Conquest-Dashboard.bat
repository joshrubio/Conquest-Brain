@echo off
REM  Conquest dashboard — double-click to open.
REM  Starts the local server (127.0.0.1:8765) and the browser.
cd /d "%~dp0"
tasklist /fi "imagename eq python.exe" /v 2>nul | find "serve.py" >nul
if errorlevel 1 (
  start "Conquest server" /min python tools\serve.py
  timeout /t 2 >nul
)
start "" http://localhost:8765

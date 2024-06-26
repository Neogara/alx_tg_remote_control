@echo off
set SCRIPT_PATH=%CD%\run.bat
set KEY=HKCU\Software\Microsoft\Windows\CurrentVersion\Run

reg add "%KEY%" /v "alx_tg_bot" /t REG_SZ /d "\"%SCRIPT_PATH%\"" /f
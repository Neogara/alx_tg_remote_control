@echo off
title alx_tg_remote_control

REM Укажите путь к интерпретатору Python
set PYTHON_PATH=python

REM Укажите относительный путь к вашему Python-скрипту
set SCRIPT_PATH=src\main.py

REM Проверка, запущен ли скрипт от имени администратора
net session >nul 2>&1
if %errorlevel% NEQ 0 (
  echo Запуск скрипта от имени администратора...
  powershell Start-Process -Verb RunAs "%~f0"
  exit /b
)

REM Запуск Python-скрипта
cd /d %~dp0
%PYTHON_PATH% %SCRIPT_PATH%

pause
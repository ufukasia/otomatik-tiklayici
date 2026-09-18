@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Otomatik Tiklayici

where pythonw.exe >nul 2>&1
if %errorlevel%==0 (
    start "" pythonw.exe "otomatik_tiklayici.py"
    exit /b
)

where python.exe >nul 2>&1
if %errorlevel%==0 (
    python "otomatik_tiklayici.py"
    if errorlevel 1 pause
    exit /b
)

echo.
echo  Python bulunamadi.
echo  https://www.python.org/downloads/ adresinden kurun ve
echo  kurulum sirasinda "Add python.exe to PATH" kutusunu isaretleyin.
echo.
pause

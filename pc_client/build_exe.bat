@echo off
chcp 65001 >nul
title 10D FCD - Commercial Installer Builder
cd /d "%~dp0"

echo ================================================================
echo    10D FCD Commercial Installer Builder (PyInstaller + Inno)
echo ================================================================
echo.

echo [1/3] Building onedir application folder (PyInstaller)...
pyinstaller --noconfirm --clean 10D_FCD.spec

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b %errorlevel%
)

echo.
echo [2/3] Compiling Setup Installer (Inno Setup)...

set "ISCC_PATH=C:\Users\duni2\AppData\Local\Programs\Inno Setup 6\ISCC.exe"
if not exist "%ISCC_PATH%" (
    set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)
if not exist "%ISCC_PATH%" (
    set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if not exist "%ISCC_PATH%" (
    echo [WARNING] ISCC.exe not found. Skipping Inno Setup packaging.
    echo Standalone portable folder is available at: %~dp0dist\10D_FCD\
    pause
    exit /b 0
)

"%ISCC_PATH%" installer.iss

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Inno Setup compilation failed.
    pause
    exit /b %errorlevel%
)

echo.
echo ================================================================
echo [3/3] Build & Packaging Complete!
echo.
echo Standalone Folder: %~dp0dist\10D_FCD\
echo Official Installer: %~dp0Output\10D_FCD_Setup_v2.1.8.exe
echo ================================================================
echo.
pause


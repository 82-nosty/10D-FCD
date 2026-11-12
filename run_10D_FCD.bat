@echo off
setlocal
title 10D FCD
pushd "%~dp0pc_client"
python app.py
if errorlevel 1 goto ON_ERROR
popd
exit /b 0

:ON_ERROR
echo.
echo ============================================================
echo [ERROR] Application terminated with an error code.
echo ============================================================
echo.
pause
popd
exit /b 1

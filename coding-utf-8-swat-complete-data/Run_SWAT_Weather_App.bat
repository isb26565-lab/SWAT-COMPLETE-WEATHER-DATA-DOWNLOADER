@echo off
setlocal
cd /d "%~dp0"
set "PYTHON_EXE=C:\Users\shuja\anaconda3\python.exe"
if exist "%PYTHON_EXE%" (
    "%PYTHON_EXE%" swat_weather_app.py
) else (
    echo Could not find Anaconda Python at %PYTHON_EXE%.
    echo Update PYTHON_EXE in this file or install Python.
    pause
    exit /b 1
)
if errorlevel 1 (
    echo.
    echo The app could not start. Make sure Python and the required packages are installed.
    pause
)
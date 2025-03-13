@echo off
setlocal enabledelayedexpansion

:: Check if Python is installed and get version
python --version > temp.txt 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python and try again.
    del temp.txt
    PAUSE
    exit /b 1
)

:: Read Python version from temp file
set /p PYTHON_VERSION=<temp.txt
del temp.txt

:: Extract version number
for /f "tokens=2" %%I in ("%PYTHON_VERSION%") do set VERSION=%%I
for /f "tokens=1,2,3 delims=." %%a in ("%VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
    set PATCH=%%c
)

:: Check version constraints (3.10 to 3.12)
if %MAJOR% NEQ 3 (
    echo Error: Python version must be between 3.10 and 3.12
    echo Current version: %VERSION%
    PAUSE
    exit /b 1
)

if %MINOR% LSS 10 (
    echo Error: Python version must be between 3.10 and 3.12
    echo Current version: %VERSION%
    PAUSE
    exit /b 1
)

if %MINOR% GTR 12 (
    echo Error: Python version must be between 3.10 and 3.12
    echo Current version: %VERSION%
    PAUSE
    exit /b 1
)

echo Python version %VERSION% found - OK

:: Set variables
set VENV_DIR=venv
set REQUIREMENTS=requirements.txt
set MAIN_SCRIPT=main.py

:: Check if requirements.txt exists
if not exist %REQUIREMENTS% (
    echo Requirements file not found: %REQUIREMENTS%
    PAUSE
    exit /b 1
)

:: Check if virtual environment exists
if exist %VENV_DIR% (
    echo Virtual environment found
    :: Activate virtual environment
    call %VENV_DIR%\Scripts\activate.bat
    
    :: Install/Update dependencies
    echo Checking and updating dependencies...
    python -m pip install -r %REQUIREMENTS% --quiet
) else (
    echo Creating new virtual environment...
    python -m venv %VENV_DIR%
    
    :: Activate virtual environment
    call %VENV_DIR%\Scripts\activate.bat
    
    :: Upgrade pip
    python -m pip install --upgrade pip --quiet
    
    :: Install dependencies
    echo Installing dependencies...
    python -m pip install -r %REQUIREMENTS% --quiet
)



echo Setup Completed
PAUSE
@echo off

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
    
) else (
    echo please run setup.bat before run-gui.bat
    PAUSE
    exit /b 1
)

:: Check if main.py exists
if not exist %MAIN_SCRIPT% (
    echo Main script not found: %MAIN_SCRIPT%
    PAUSE
    exit /b 1
)

:: Launch the program
echo Launching program...
python %MAIN_SCRIPT%

:: Deactivate virtual environment
deactivate
PAUSE
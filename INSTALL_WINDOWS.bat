:: INSTALL_WINDOWS.bat

SETLOCAL

:: Make sure tht the latest version of pip is installed.
:: TIPS: pip is the package installer for Python. You can use it to install
:: packages from the Python Package Index and other indexes.
echo "===============================================================".
echo "Updating Python dependencies..."
python -m pip install --user --upgrade pip

:: Install a virtual environment to download all the required python packages.
:: TIPS: virtualenv is a tool for creating isolated Python environments.
:: More info: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/
python -m pip install --user virtualenv


:: Create a virtual environment.
:: TIPS: this will create another folder (named env) in the current repository
echo "===============================================================".
echo "Creating virtual environment..."
python -m venv env
echo "Virtual environment created in /env directory."

echo "==============================================================="
echo "Activating the virtual environment..."
@echo off
call env\Scripts\activate.bat
@echo on
python -m pip install --upgrade pip

@ECHO OFF

:: Install all the dependencies
:: TIPS: the requirements.txt file contains all the dependencies, namely the
:: python packages which will be installed in the virtual environment.
ECHO "==============================================================="
ECHO "Installing Verbify-TTS dependencies..."
python -m pip install -r requirements.txt


:: Set up the command to start the verbify-tts system.
:: TIPS: this will create a file named START_TTS.bat in the current repository.
:: This file will be used to start the system, thus it is important to move it
:: in the window startup folder
ECHO "==============================================================="
ECHO "Creating the START_TTS.bat file..."
:: get current directory path in a variable
call :setup_launch_script


:: Move the launch script in the startup folder of windows
SET STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
ECHO "==============================================================="
ECHO "Moving the START_TTS.bat file in the startup folder..."
ECHO "Startup folder: %STARTUP_DIR%"
move START_TTS.bat "%STARTUP_DIR%"

:: Remind the user the two lines which have to be set up.
echo "==============================================================="
echo "Almost there! The last step is MANUAL."
echo "The following two commands are needed to call the Verbify-TTS service."
:: save the python path of this newly create virtual environment in a variable
python -c "import sys; print(sys.executable)" > tmp_python_path.txt
:: read the python path from the file
for /f "tokens=1" %%a in (tmp_python_path.txt) do set PYTHON_PATH=%%a
echo %PYTHON_PATH%
echo ""
echo "- COMMAND 1: READ THE TEXT (recommended key combination: ALT + ESC)"
echo "The following is to ask the service to read the selected text:"
echo %PYTHON_PATH% %CWD%\command_read.py
echo ""
echo "- COMMAND 2: STOP READING (recommended key combination: ALT + END)"
echo "The following is to stop the current reading:"
echo %PYTHON_PATH% %CWD%\command_stop.py

EXIT /B 0


:setup_launch_script
    SET START_TTS_FILE=%CD%\START_TTS.bat
    ECHO cd %CD% > START_TTS.bat
    ECHO call env\Scripts\activate.bat >> START_TTS.bat
    ECHO python server.py >> START_TTS.bat
    ECHO New file created: %START_TTS_FILE%
    EXIT /B 0


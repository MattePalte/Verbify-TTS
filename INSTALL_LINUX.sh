#!/bin/bash

# Make sure tht the latest version of pip is installed.
# TIPS: pip is the package installer for Python. You can use it to install
# packages from the Python Package Index and other indexes.
echo "===============================================================".
echo "Updating Python dependencies..."
python3 -m pip install --user --upgrade pip


# Install a virtual environment to download all the required python packages.
# TIPS: virtualenv is a tool for creating isolated Python environments.
# More info: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/
python3 -m pip install --user virtualenv


# Create a virtual environment.
# TIPS: this will create another folder (named env) in the current repository
echo "===============================================================".
echo "Creating virtual environment..."
python3 -m venv env
echo "Virtual environment created in /env directory."

# Activate the virtual environment
echo "==============================================================="
echo "Activating the virtual environment..."
source env/bin/activate
python3 -m pip install --upgrade pip


# Install all the dependencies
# TIPS: the requirements.txt file contains all the dependencies, namely the
# python packages which will be installed in the virtual environment.
echo "==============================================================="
echo "Installing Verbify-TTS dependencies..."
python3 -m pip install -r requirements.txt


# Set up the command to start the verbify-tts system.
# TIPS: this will create a file named START_TTS.sh in the current repository.
setup_launch_script() {
    cwd=$(pwd)
    echo "==============================================================="
    echo "Creating launch script (STARTUP_TTS.sh)..."
    echo '#!/bin/bash' > START_TTS.sh
    echo "cd ""$cwd" >> START_TTS.sh
    echo 'source env/bin/activate' >> START_TTS.sh
    echo 'python3 server.py' >> START_TTS.sh
    chmod +x START_TTS.sh
    echo 'New file created: START_TTS.sh'
}
setup_launch_script

# Create the launch script according to the Systemctl template
create_verbify_autostart_file_for_systemd() {
    cwd=$(pwd)
    echo "==============================================================="
    echo 'Creating (systemd) file: verbify_autostart.service ...'
    echo '[Unit]' > verbify_autostart.service
    echo 'Description=Verbify-TTS' >> verbify_autostart.service
    echo 'After=network.target' >> verbify_autostart.service
    echo '[Service]' >> verbify_autostart.service
    echo 'ExecStart='$cwd'/START_TTS.sh' >> verbify_autostart.service
    echo 'ExecStop=/bin/kill -9 $MAINPID' >> verbify_autostart.service
    echo '[Install]' >> verbify_autostart.service
    echo 'WantedBy=multi-user.target' >> verbify_autostart.service
    sudo mv verbify_autostart.service /etc/systemd/system/verbify-tts.service
    sudo systemctl enable verbify-tts.service
}


# ask the user if it has sudo rights to install the autostart file
echo "==============================================================="
echo "Do you have sudo (administrator) rights? [y/n] "
echo "Verbify-TTS needs them to move the autostart file in the etc/systemd/system/ directory."
echo "In this way Verbify-TTS will be automatically started when the computer is started."
echo "If you have sudo rights, type 'y', press enter, then insert the password."
echo "Otherwise, type 'n' and press enter to finish the installation."
read -r answer
if [ "$answer" == "y" ]; then
    # install the autostart file
    # Change the setting of the system so that the program runs at every startup
    # of the Linux system.
    echo "Creating a link in: /etc/systemd/system/verbify-tts..."
    create_verbify_autostart_file_for_systemd
else
    echo "The autostart file will not be installed."
    echo "You have to start the script by running ./START_TTS.sh in a terminal at every startup"
fi


# Remind the user the two lines which have to be set up.
echo "==============================================================="
echo "Almost there! The last step is MANUAL."
echo "The following two commands are needed to call the Verbify-TTS service."
cwd=$(pwd)
echo ""
echo "- COMMAND 1: READ THE TEXT (recommended key combination: ALT + ESC)"
echo "The following is to ask the service to read the selected text:"
echo "$cwd""/env/bin/python ""$cwd""/command_read.py"
echo ""
echo "- COMMAND 2: STOP READING (recommended key combination: ALT + END)"
echo "The following is to stop the current reading:"
echo "$cwd""/env/bin/python ""$cwd""/command_stop.py"


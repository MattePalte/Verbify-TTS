#!/bin/bash

# call this script with
# ./INSTALL_LINUX.sh

# install pipx
echo "==============================================================="
echo "Installing pipx..."
echo "==============================================================="
python3 -m pip install --user pipx
python3 -m pipx ensurepath
echo "==============================================================="
echo "Pipx has been installed."
echo "==============================================================="

# install Verbify-TTS
echo "==============================================================="
echo "Installing Verbify-TTS..."
echo "==============================================================="
pipx install ${PWD}/
echo "==============================================================="
echo "Verbify-TTS has been installed."
echo "==============================================================="

SERVICE_NAME="verbify-tts-pipx"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
LOCAL_SERVICE_FILE="$PWD/$SERVICE_NAME.service"

PIPX_PATH=$(which pipx)

echo "Using pipx from: $PIPX_PATH"

# ask the user if it has sudo rights to install the autostart file
echo "==============================================================="
echo "Do you have sudo (administrator) rights? [y/n] "
echo "Verbify-TTS needs them to move the autostart file in the etc/systemd/system/ directory."
echo "In this way Verbify-TTS will be automatically started when the computer is started."
echo "If you have sudo rights, type 'y', press enter, then insert the password."
echo "Otherwise, type 'n' and press enter to finish the installation."
read -r answer
if [ "$answer" == "y" ]; then
    # check if the user is root
    # if [ "$(id -u)" -ne 0 ]; then
    #     echo "You need to run this script as root. Please use sudo."
    #     exit 1
    # else
    # install the autostart file
    # Change the setting of the system so that the program runs at every startup
    # of the Linux system.
    echo "Creating the systemd service file for Verbify-TTS..."
    echo "in current directory: $PWD"

    echo "==============================================================="

    # Create a systemd service file for Verbify-TTS
    echo "[Unit]" > $LOCAL_SERVICE_FILE
    echo "Description=Verbify-TTS Server" >> $LOCAL_SERVICE_FILE
    echo "After=network.target" >> $LOCAL_SERVICE_FILE

    echo "[Service]" >> $LOCAL_SERVICE_FILE
    # add pipx path to the environment
    echo "Environment=\"PATH=$(dirname "$PIPX_PATH"):$PATH\"" >> $LOCAL_SERVICE_FILE
    # echo "Environment=\"PYTHONPATH=$(python3 -m site)\"" >> $LOCAL_SERVICE_FILE
    echo "ExecStart=$(dirname "$PIPX_PATH")/verbify_tts_server" >> $LOCAL_SERVICE_FILE
    echo 'ExecStop=/bin/kill -9 $MAINPID' >> $LOCAL_SERVICE_FILE
    echo "User=$USER" >> $LOCAL_SERVICE_FILE

    echo "[Install]" >> $LOCAL_SERVICE_FILE
    echo "WantedBy=multi-user.target" >> $LOCAL_SERVICE_FILE

    # copy
    sudo cp $LOCAL_SERVICE_FILE $SERVICE_FILE
    echo "==============================================================="
    echo "The systemd service file has been created at $SERVICE_FILE"
    echo "==============================================================="

    # Reload systemd and enable the service
    sudo systemctl daemon-reload
    sudo systemctl enable $SERVICE_NAME

    # Start the service
    sudo systemctl start $SERVICE_NAME

    echo "==============================================================="
    echo "Verbify-TTS server has been configured to start at system boot."
    echo "You can check the status of the service with the following command:"
    echo "systemctl status $SERVICE_NAME"
    echo "==============================================================="

else
    echo "The autostart file will not be installed."
    echo "You will need to start the Verbify-TTS server manually every time you start your computer."
    echo "To start the server, open a terminal and type:"
    echo "verbify_tts_server"
    echo "To stop the server, simply close the terminal"
fi

# Remind the user the two lines which have to be set up.
echo "==============================================================="
echo "Almost there! The last step is MANUAL."
echo "The following two commands are needed to call the Verbify-TTS service."
echo ""
echo "- COMMAND 1: READ THE TEXT (recommended key combination: ALT + ESC)"
echo "The following is to ask the service to read the selected text:"
echo "verbify_tts_command_read"
echo ""
echo "- COMMAND 2: STOP READING (recommended key combination: ALT + END)"
echo "The following is to stop the current reading:"
echo "verbify_tts_command_stop"


# Automatic Setup of the key combinations
echo "==============================================================="
echo "Do you want to set up the key combinations automatically? [y/n]"
echo "If you have autokey installed, type 'y' and press enter."
echo "Otherwise, type 'n' and press enter to finish the installation."
read -r answer

if [ "$answer" == "y" ]; then
    # check if autokey is installed
    if ! command -v autokey-gtk &> /dev/null; then
        echo "Autokey is not installed. Installing autokey-gtk..."
        sudo apt-get install autokey-gtk
    fi

    # Create the autokey script
    echo "Creating the autokey script..."
    mkdir -p ~/.config/autokey/data/verbify_tts
    # Copy autokey configuration files for Verbify TTS
    SCRIPT_DIR="$PWD/verbify_tts/configuration/keyboard_shortcuts/linux"

    # Check if the script directory exists
    if [ -d "$SCRIPT_DIR" ]; then
        # Copy the Python scripts
        cp "$SCRIPT_DIR/shortcut_read.py" ~/.config/autokey/data/verbify_tts/
        cp "$SCRIPT_DIR/shortcut_stop.py" ~/.config/autokey/data/verbify_tts/

        # Copy the JSON configuration files
        cp "$SCRIPT_DIR/.shortcut_read.json" ~/.config/autokey/data/verbify_tts/
        cp "$SCRIPT_DIR/.shortcut_stop.json" ~/.config/autokey/data/verbify_tts/

        echo "Autokey scripts for Verbify-TTS have been set up."
        echo "Please restart autokey (or log out and log in again) to apply the changes."
    else
        echo "Error: Could not find keyboard shortcut files at $SCRIPT_DIR"
        echo "You will need to set up the key combinations manually."
    fi
fi

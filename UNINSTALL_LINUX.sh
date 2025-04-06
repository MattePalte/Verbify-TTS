#!/bin/bash
# This script uninstalls Verbify-TTS and removes the systemd service

SERVICE_NAME="verbify-tts-pipx"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

echo "==============================================================="
echo "Uninstalling Verbify-TTS..."
echo "==============================================================="

# Check if systemd service is installed
if [ -f "$SERVICE_FILE" ]; then
    echo "Removing Verbify-TTS systemd service..."
    echo "==============================================================="

    # Ask for sudo permissions
    echo "Do you have sudo (administrator) rights? [y/n]"
    echo "Sudo rights are needed to remove the service file from /etc/systemd/system/"
    read -r answer

    if [ "$answer" == "y" ]; then
        # Stop and disable the service
        sudo systemctl stop $SERVICE_NAME
        sudo systemctl disable $SERVICE_NAME

        # Remove the service file
        sudo rm $SERVICE_FILE
        sudo systemctl daemon-reload

        echo "Verbify-TTS service has been removed successfully."
    else
        echo "Cannot remove systemd service without sudo rights."
        echo "The service may continue to start automatically at boot."
    fi
else
    echo "Verbify-TTS service is not installed. Skipping service removal."
fi

echo "==============================================================="
echo "Uninstalling Verbify-TTS package..."
echo "==============================================================="

# Uninstall the package with pipx
pipx uninstall verbify-tts

echo "==============================================================="
echo "Verbify-TTS has been uninstalled."
echo "==============================================================="

echo "If you wish to remove pipx as well, you can run:"
echo "python3 -m pip uninstall pipx"
echo "==============================================================="
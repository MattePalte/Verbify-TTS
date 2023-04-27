#!/bin/bash

# Start virtual environment
source venv38/bin/activate

# Start the server
python -m verbify_tts.services.pose_tracking

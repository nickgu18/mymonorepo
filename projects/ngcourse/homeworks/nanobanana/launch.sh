#!/bin/bash

# Check if uv is installed
if ! command -v uv &> /dev/null
then
    echo "uv could not be found, please install it first. For example: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "./.venv" ]; then
    echo "Creating virtual environment with uv..."
    uv venv
fi

# Activate the virtual environment
source ./.venv/bin/activate

# Install dependencies
echo "Installing dependencies with uv..."
uv pip install -r requirements.txt

# Run the application
echo "Launching Nano Banana Image Generator..."
python app.py

#!/bin/bash
# Launcher for Linux and macOS
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

./venv/bin/python paraphrase.py

#!/bin/bash
echo "Starting VisionScan..."

if [ ! -f ".venv/bin/python" ]; then
    echo "Virtual environment not found. Initializing..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Python 3 is required but not found. Please install Python 3.12+."
        exit 1
    fi
    echo "Installing uv package manager..."
    .venv/bin/python -m pip install uv
    echo "Syncing dependencies..."
    .venv/bin/python -m uv sync
fi

.venv/bin/python main.py

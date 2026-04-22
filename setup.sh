#!/bin/bash
set -euo pipefail

echo "=== WatchingAI Setup ==="

PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v py &> /dev/null; then
    PYTHON_CMD="py"
fi

if [ -n "$PYTHON_CMD" ]; then
    echo "Python found: $PYTHON_CMD"
    echo "Installing watchingai..."
    "$PYTHON_CMD" -m pip install --upgrade watchingai
else
    echo "Error: Python not found. Please install Python 3.9+ first."
    exit 1
fi

mkdir -p "$HOME/.watchingai"

echo "=== WatchingAI Setup Complete ==="

#!/bin/bash
set -euo pipefail

echo "=== WatchingAI Setup ==="

WATCHINGAI_DIR="$HOME/.watchingai"
mkdir -p "$WATCHINGAI_DIR"

PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

if [ -n "$PYTHON_CMD" ]; then
    echo "Python found: $PYTHON_CMD"
    echo "Installing watchingai via pip..."
    "$PYTHON_CMD" -m pip install watchingai
else
    echo "Error: Python not found. Please install Python 3.9+ first."
    exit 1
fi

echo "=== WatchingAI Setup Complete ==="
echo "Run 'watchingai' or 'python -m watchingai' to start."

#!/bin/bash
set -euo pipefail

echo "=== WatchingAI Setup ==="

find_python() {
    if command -v python3 &> /dev/null; then echo "python3"
    elif command -v python &> /dev/null; then echo "python"
    elif command -v py &> /dev/null; then echo "py"
    fi
}

PYTHON_CMD=$(find_python)

if [ -z "$PYTHON_CMD" ]; then
    echo "Python not found. Installing..."
    case "$(uname -s)" in
        MINGW*|MSYS*|CYGWIN*)
            if command -v winget &> /dev/null; then
                winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements
            else
                echo "Error: winget not found. Please install Python 3.9+ manually: https://www.python.org/downloads/"
                exit 1
            fi
            ;;
        Darwin*)
            if command -v brew &> /dev/null; then
                brew install python3
            else
                echo "Error: brew not found. Please install Python 3.9+ manually: https://www.python.org/downloads/"
                exit 1
            fi
            ;;
        *)
            if command -v apt-get &> /dev/null; then
                sudo apt-get update && sudo apt-get install -y python3 python3-pip
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y python3 python3-pip
            else
                echo "Error: Please install Python 3.9+ manually: https://www.python.org/downloads/"
                exit 1
            fi
            ;;
    esac
    PYTHON_CMD=$(find_python)
    if [ -z "$PYTHON_CMD" ]; then
        echo "Error: Python installation failed. Please install Python 3.9+ manually."
        exit 1
    fi
fi

echo "Python found: $PYTHON_CMD"
echo "Installing watchingai..."
"$PYTHON_CMD" -m pip install --upgrade watchingai

mkdir -p "$HOME/.watchingai"

echo "=== WatchingAI Setup Complete ==="

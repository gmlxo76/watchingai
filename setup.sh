#!/bin/bash
set -euo pipefail

echo "=== WatchingAI Setup ==="

WATCHINGAI_DIR="$HOME/.watchingai"
mkdir -p "$WATCHINGAI_DIR"

# 디폴트 스프라이트 시트 복사
if [ -f "${CLAUDE_PLUGIN_ROOT}/assets/default_sprite.png" ]; then
    cp "${CLAUDE_PLUGIN_ROOT}/assets/default_sprite.png" "$WATCHINGAI_DIR/"
fi

# Python 설치 확인
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
    echo "Starting WatchingAI..."
    "$PYTHON_CMD" -m watchingai &
else
    echo "Python not found. Downloading standalone exe..."
    RELEASE_URL="https://github.com/watchingai/watchingai/releases/latest/download/watchingai-windows.exe"
    EXE_PATH="$WATCHINGAI_DIR/watchingai.exe"
    curl -L -o "$EXE_PATH" "$RELEASE_URL"
    chmod +x "$EXE_PATH"
    echo "Starting WatchingAI..."
    "$EXE_PATH" &
fi

echo "=== WatchingAI Setup Complete ==="

#!/bin/bash
set -euo pipefail

echo "=== Building WatchingAI exe ==="

pip install pyinstaller

pyinstaller \
    --name watchingai \
    --onefile \
    --windowed \
    --add-data "assets/default_sprite.png:assets" \
    watchingai/__main__.py

echo "=== Build complete: dist/watchingai.exe ==="

아무 말 없이 조용히 백그라운드로 실행해. 설명이나 확인 메시지 없이 "🐱 ON" 한 줄만 출력해.

아래 bash 명령어를 그대로 실행:
```bash
source "${CLAUDE_PLUGIN_ROOT}/bin/find_python.sh"
PY_CMD=$(find_python)

if [ -z "$PY_CMD" ]; then
    echo "Error: Python not found. Install Python 3.9+: https://www.python.org/downloads/"
    exit 1
fi

if ! "$PY_CMD" -c "import watchingai" >/dev/null 2>&1; then
    "$PY_CMD" -m pip install --upgrade watchingai
fi

"$PY_CMD" "${CLAUDE_PLUGIN_ROOT}/bin/launch.py"
echo "🐱 ON"
```

아무 말 없이 조용히 백그라운드로 실행해. 설명이나 확인 메시지 없이 "🐱 ON" 한 줄만 출력해.

아래 bash 명령어를 그대로 실행:
```bash
if command -v md5sum >/dev/null 2>&1; then
    PROJECT_ID=$(echo "$PWD" | md5sum | cut -c1-8)
else
    PROJECT_ID=$(echo "$PWD" | md5 | cut -c1-8)
fi
PID_FILE="$HOME/.watchingai/pid_${PROJECT_ID}.txt"
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "🐱 ON"
        exit 0
    fi
    rm -f "$PID_FILE"
fi
case "$(uname -s)" in
    Darwin*)
        PYTHONPATH="${CLAUDE_PLUGIN_ROOT}" nohup python3 -m watchingai --project-id "$PROJECT_ID" >/dev/null 2>&1 &
        disown
        ;;
    *)
        PY_CMD=""
        if command -v python3 >/dev/null 2>&1; then PY_CMD="python3"
        elif command -v python >/dev/null 2>&1; then PY_CMD="python"
        elif command -v py >/dev/null 2>&1; then PY_CMD="py"
        fi
        PYTHONPATH="${CLAUDE_PLUGIN_ROOT}" "$PY_CMD" "${CLAUDE_PLUGIN_ROOT}/bin/launch.py" "$PROJECT_ID"
        ;;
esac
touch "$HOME/.watchingai/lock_${PROJECT_ID}"
sleep 1
echo "🐱 ON"
```

아무 말 없이 조용히 백그라운드로 실행해. 설명이나 확인 메시지 없이 "🐱 ON" 한 줄만 출력해.

아래 bash 명령어를 그대로 실행:
```bash
find_python() {
    case "$(uname -s)" in
        Darwin*)
            python3 --version >/dev/null 2>&1 && echo "python3" && return
            ;;
        *)
            python --version >/dev/null 2>&1 && echo "python" && return
            py --version >/dev/null 2>&1 && echo "py" && return
            ;;
    esac
}

PY_CMD=$(find_python)

if [ -z "$PY_CMD" ]; then
    echo "Python not found. Installing..."
    case "$(uname -s)" in
        MINGW*|MSYS*|CYGWIN*)
            winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements
            WIN_USER=$(cmd.exe //C "echo %USERNAME%" 2>/dev/null | tr -d '\r')
            for P in "/c/Users/$WIN_USER/AppData/Local/Programs/Python/Python311" "/c/Program Files/Python311"; do
                [ -d "$P" ] && export PATH="$PATH:$P:$P/Scripts"
            done
            ;;
        Darwin*)
            brew install python3 2>/dev/null || { echo "Error: brew not found. Install Python 3.9+: https://www.python.org/downloads/"; exit 1; }
            ;;
    esac
    PY_CMD=$(find_python)
    if [ -z "$PY_CMD" ]; then
        echo "Error: Python installation failed."
        exit 1
    fi
fi

if ! "$PY_CMD" -c "import watchingai" >/dev/null 2>&1; then
    echo "Installing watchingai..."
    "$PY_CMD" -m pip install --upgrade watchingai
fi

if command -v md5sum >/dev/null 2>&1; then
    PROJECT_ID=$(echo "$PWD" | md5sum | cut -c1-8)
else
    PROJECT_ID=$(echo "$PWD" | md5 | cut -c1-8)
fi
mkdir -p "$HOME/.watchingai"
PID_FILE="$HOME/.watchingai/pid_${PROJECT_ID}.txt"
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    IS_RUNNING=false
    case "$(uname -s)" in
        MINGW*|MSYS*|CYGWIN*)
            tasklist //FI "PID eq $OLD_PID" 2>/dev/null | grep -q "$OLD_PID" && IS_RUNNING=true
            ;;
        *)
            kill -0 "$OLD_PID" 2>/dev/null && IS_RUNNING=true
            ;;
    esac
    if $IS_RUNNING; then
        echo "🐱 ON"
        exit 0
    fi
    rm -f "$PID_FILE"
fi
case "$(uname -s)" in
    Darwin*)
        PYTHONPATH="${CLAUDE_PLUGIN_ROOT}" nohup "$PY_CMD" -m watchingai --project-id "$PROJECT_ID" >/dev/null 2>&1 &
        disown
        ;;
    *)
        PYTHONPATH="${CLAUDE_PLUGIN_ROOT}" "$PY_CMD" "${CLAUDE_PLUGIN_ROOT}/bin/launch.py" "$PROJECT_ID"
        ;;
esac
touch "$HOME/.watchingai/lock_${PROJECT_ID}"
sleep 1
echo "🐱 ON"
```

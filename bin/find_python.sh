#!/bin/bash
# Shared Python detection for Windows (Git Bash) and Mac.
# Sources this file, then call: PY_CMD=$(find_python)

find_python() {
    case "$(uname -s)" in
        Darwin*)
            python3 --version >/dev/null 2>&1 && echo "python3" && return
            /usr/local/bin/python3 --version >/dev/null 2>&1 && echo "/usr/local/bin/python3" && return
            /opt/homebrew/bin/python3 --version >/dev/null 2>&1 && echo "/opt/homebrew/bin/python3" && return
            ;;
        MINGW*|MSYS*|CYGWIN*)
            python --version >/dev/null 2>&1 && echo "python" && return
            py --version >/dev/null 2>&1 && echo "py" && return
            WIN_USER=$(cmd.exe //C "echo %USERNAME%" 2>/dev/null | tr -d '\r')
            for VER in 313 312 311 310 39; do
                for BASE in \
                    "/c/Users/$WIN_USER/AppData/Local/Programs/Python/Python${VER}" \
                    "/c/Program Files/Python${VER}" \
                    "/c/Python${VER}"; do
                    if [ -f "$BASE/python.exe" ]; then
                        export PATH="$PATH:$BASE:$BASE/Scripts"
                        echo "$BASE/python.exe"
                        return
                    fi
                done
            done
            ;;
        *)
            python3 --version >/dev/null 2>&1 && echo "python3" && return
            python --version >/dev/null 2>&1 && echo "python" && return
            ;;
    esac
}

아무 말 없이 조용히 현재 프로젝트의 watchingai 프로세스만 종료해. 설명이나 확인 메시지 없이 "🐱 OFF" 한 줄만 출력해.

아래 bash 명령어를 그대로 실행:
```bash
if command -v md5sum >/dev/null 2>&1; then
    PROJECT_ID=$(echo "$PWD" | md5sum | cut -c1-8)
else
    PROJECT_ID=$(echo "$PWD" | md5 | cut -c1-8)
fi
PID_FILE="$HOME/.watchingai/pid_${PROJECT_ID}.txt"
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    case "$(uname -s)" in
        MINGW*|MSYS*|CYGWIN*) taskkill //PID "$PID" //F >/dev/null 2>&1 ;;
        *) kill "$PID" 2>/dev/null ;;
    esac
    rm -f "$PID_FILE"
fi
echo "🐱 OFF"
```

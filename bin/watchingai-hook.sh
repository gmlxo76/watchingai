#!/bin/bash
WATCHINGAI_DIR="$HOME/.watchingai"
mkdir -p "$WATCHINGAI_DIR"

if command -v md5sum >/dev/null 2>&1; then
    PROJECT_ID=$(echo "$PWD" | md5sum | cut -c1-8)
else
    PROJECT_ID=$(echo "$PWD" | md5 | cut -c1-8)
fi
STATUS_FILE="$WATCHINGAI_DIR/status_${PROJECT_ID}.json"
SESSION_LOG="$WATCHINGAI_DIR/session_log_${PROJECT_ID}.txt"
LOCK_FILE="$WATCHINGAI_DIR/lock_${PROJECT_ID}"

echo "$PWD" > "$WATCHINGAI_DIR/project_${PROJECT_ID}.path"

INPUT=$(cat)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S")

get_val() {
    echo "$INPUT" | sed -n "s/.*\"$1\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p" | head -1
}

HOOK_EVENT=$(get_val "hook_event_name")
TOOL_NAME=$(get_val "tool_name")

write_status() {
    cat > "$STATUS_FILE" << EOF
{"status":"$1","detail":"$2","timestamp":"$TIMESTAMP","elapsed_seconds":0}
EOF
}

log_action() {
    echo "$1" >> "$SESSION_LOG"
}

build_summary() {
    if [ ! -f "$SESSION_LOG" ]; then
        echo "작업 완료"
        return
    fi
    EDIT_COUNT=$(grep -c "edit" "$SESSION_LOG" 2>/dev/null || true)
    CMD_COUNT=$(grep -c "cmd" "$SESSION_LOG" 2>/dev/null || true)
    READ_COUNT=$(grep -c "read" "$SESSION_LOG" 2>/dev/null || true)
    ERR_COUNT=$(grep -c "error" "$SESSION_LOG" 2>/dev/null || true)
    EDIT_COUNT=${EDIT_COUNT:-0}; CMD_COUNT=${CMD_COUNT:-0}
    READ_COUNT=${READ_COUNT:-0}; ERR_COUNT=${ERR_COUNT:-0}
    PARTS=""
    [ "$EDIT_COUNT" -gt 0 ] && PARTS="파일 ${EDIT_COUNT}개 편집"
    [ "$CMD_COUNT" -gt 0 ] && PARTS="${PARTS:+$PARTS, }명령 ${CMD_COUNT}회 실행"
    [ "$READ_COUNT" -gt 0 ] && PARTS="${PARTS:+$PARTS, }파일 ${READ_COUNT}개 탐색"
    [ "$ERR_COUNT" -gt 0 ] && PARTS="${PARTS:+$PARTS, }에러 ${ERR_COUNT}건"
    [ -z "$PARTS" ] && PARTS="작업 완료"
    echo "$PARTS"
}

case "$HOOK_EVENT" in
    SessionStart)
        rm -f "$SESSION_LOG"
        rm -f "$LOCK_FILE"
        write_status "idle" ""
        ;;
    SessionEnd)
        rm -f "$SESSION_LOG"
        rm -f "$LOCK_FILE"
        PID_FILE="$WATCHINGAI_DIR/pid_${PROJECT_ID}.txt"
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            case "$(uname -s)" in
                MINGW*|MSYS*|CYGWIN*) taskkill //PID "$PID" //F >/dev/null 2>&1 ;;
                *) kill "$PID" 2>/dev/null ;;
            esac
            rm -f "$PID_FILE"
        fi
        write_status "idle" ""
        ;;
    UserPromptSubmit)
        rm -f "$LOCK_FILE"
        write_status "thinking" "요청 처리 중..."
        ;;
    Stop)
        SUMMARY=$(build_summary)
        rm -f "$SESSION_LOG"
        write_status "idle" "[세션종료] $SUMMARY"
        ;;
    *)
        if [ -f "$LOCK_FILE" ]; then
            exit 0
        fi
        case "$HOOK_EVENT" in
            PreToolUse)
                case "$TOOL_NAME" in
                    Edit|Write)
                        log_action "edit"
                        write_status "working" "파일 편집 중" ;;
                    Bash|PowerShell)
                        log_action "cmd"
                        write_status "working" "명령 실행 중" ;;
                    Read|Glob|Grep)
                        log_action "read"
                        write_status "working" "파일 탐색 중" ;;
                    *)
                        write_status "working" "$TOOL_NAME 실행 중" ;;
                esac
                ;;
            PostToolUse)
                write_status "working" "작업 중"
                ;;
            PostToolUseFailure)
                log_action "error"
                write_status "error" "$TOOL_NAME 실패"
                ;;
        esac
        ;;
esac

exit 0

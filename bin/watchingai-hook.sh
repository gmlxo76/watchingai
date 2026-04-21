#!/bin/bash
WATCHINGAI_DIR="$HOME/.watchingai"
mkdir -p "$WATCHINGAI_DIR"

PROJECT_ID=$(echo "$PWD" | md5sum | cut -c1-8)
STATUS_FILE="$WATCHINGAI_DIR/status_${PROJECT_ID}.json"
SESSION_LOG="$WATCHINGAI_DIR/session_log_${PROJECT_ID}.txt"

# 현재 프로젝트 경로 기록 (앱에서 참조)
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
    EDIT_COUNT=$(grep -c "edit" "$SESSION_LOG" 2>/dev/null || echo 0)
    CMD_COUNT=$(grep -c "cmd" "$SESSION_LOG" 2>/dev/null || echo 0)
    READ_COUNT=$(grep -c "read" "$SESSION_LOG" 2>/dev/null || echo 0)
    ERR_COUNT=$(grep -c "error" "$SESSION_LOG" 2>/dev/null || echo 0)
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
        write_status "idle" ""
        ;;
    Stop)
        SUMMARY=$(build_summary)
        rm -f "$SESSION_LOG"
        write_status "idle" "[세션종료] $SUMMARY"
        ;;
    SessionEnd)
        write_status "idle" ""
        ;;
    UserPromptSubmit)
        write_status "thinking" "요청 처리 중..."
        ;;
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
        write_status "done" "완료"
        ;;
    PostToolUseFailure)
        log_action "error"
        write_status "error" "$TOOL_NAME 실패"
        ;;
esac

exit 0

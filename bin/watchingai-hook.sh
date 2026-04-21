#!/bin/bash
WATCHINGAI_DIR="$HOME/.watchingai"
STATUS_FILE="$WATCHINGAI_DIR/status.json"
mkdir -p "$WATCHINGAI_DIR"

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

case "$HOOK_EVENT" in
    SessionStart|Stop|SessionEnd)
        write_status "idle" ""
        ;;
    UserPromptSubmit)
        write_status "thinking" "요청 처리 중..."
        ;;
    PreToolUse)
        case "$TOOL_NAME" in
            Edit|Write) write_status "working" "파일 편집 중" ;;
            Bash|PowerShell) write_status "working" "명령 실행 중" ;;
            Read|Glob|Grep) write_status "working" "파일 탐색 중" ;;
            *) write_status "working" "$TOOL_NAME 실행 중" ;;
        esac
        ;;
    PostToolUse)
        write_status "done" "완료"
        ;;
    PostToolUseFailure)
        write_status "error" "$TOOL_NAME 실패"
        ;;
esac

exit 0

#!/bin/bash
set -euo pipefail

WATCHINGAI_DIR="$HOME/.watchingai"
STATUS_FILE="$WATCHINGAI_DIR/status.json"
mkdir -p "$WATCHINGAI_DIR"

HOOK_INPUT=$(cat)
HOOK_EVENT=$(echo "$HOOK_INPUT" | jq -r '.hook_event_name // empty')
TOOL_NAME=$(echo "$HOOK_INPUT" | jq -r '.tool_name // empty')
TOOL_INPUT=$(echo "$HOOK_INPUT" | jq -r '.tool_input // empty')

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S")

write_status() {
    local status="$1"
    local detail="$2"
    cat > "$STATUS_FILE" << STATUSEOF
{
  "status": "$status",
  "detail": "$detail",
  "timestamp": "$TIMESTAMP",
  "elapsed_seconds": 0
}
STATUSEOF
}

case "$HOOK_EVENT" in
    "SessionStart")
        write_status "idle" ""
        ;;
    "UserPromptSubmit")
        write_status "thinking" "요청 처리 중..."
        ;;
    "PreToolUse")
        case "$TOOL_NAME" in
            "Edit"|"Write")
                FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.file_path // "unknown"')
                write_status "working" "$FILE_PATH 편집 중"
                ;;
            "Bash"|"PowerShell")
                COMMAND=$(echo "$TOOL_INPUT" | jq -r '.command // ""' | head -c 50)
                write_status "working" "명령 실행: $COMMAND"
                ;;
            "Read"|"Glob"|"Grep")
                write_status "working" "파일 탐색 중"
                ;;
            *)
                write_status "working" "$TOOL_NAME 실행 중"
                ;;
        esac
        ;;
    "PostToolUse")
        write_status "done" "완료"
        ;;
    "PostToolUseFailure")
        write_status "error" "$TOOL_NAME 실패"
        ;;
    "Stop")
        write_status "idle" ""
        ;;
    "SessionEnd")
        write_status "idle" ""
        ;;
esac

exit 0

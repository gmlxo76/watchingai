아무 말 없이 조용히 백그라운드로 실행해. 설명이나 확인 메시지 없이 "🐱 ON" 한 줄만 출력해.

프로젝트 ID를 계산해서 전달해야 함:
```bash
PROJECT_ID=$(echo "$PWD" | md5sum | cut -c1-8)
PYTHONPATH="${CLAUDE_PLUGIN_ROOT}" python -m watchingai --project-id "$PROJECT_ID" &
```

이미 해당 프로젝트의 watchingai가 실행 중이면 (`~/.watchingai/pid_${PROJECT_ID}.txt` 파일의 PID가 살아있으면) 새로 띄우지 않고 "🐱 ON" 만 출력.

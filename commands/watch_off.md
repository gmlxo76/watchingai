아무 말 없이 조용히 현재 프로젝트의 watchingai 프로세스만 종료해. 설명이나 확인 메시지 없이 "🐱 OFF" 한 줄만 출력해.

프로젝트 ID로 해당 프로세스를 찾아서 종료:
```bash
PROJECT_ID=$(echo "$PWD" | md5sum | cut -c1-8)
PID_FILE="$HOME/.watchingai/pid_${PROJECT_ID}.txt"
```

`$PID_FILE`이 있으면 해당 PID를 kill. 없으면 그냥 "🐱 OFF" 출력.

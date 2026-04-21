# WatchingAI

Claude Code의 작업 상태를 데스크톱 위에 스프라이트 캐릭터로 표시하는 Claude Code 플러그인 + Windows 데스크톱 위젯 앱.

## 기능

- Claude Code hooks로 실시간 상태 감지 (대기/생각/작업/완료/에러)
- 투명 위젯에 스프라이트 애니메이션 표시
- 마우스 호버 시 현재 작업 내용 + 경과 시간 표시
- 드래그로 자유 위치 이동
- 위치 프리셋 (좌상단/우상단/좌하단/우하단/작업표시줄 근처)
- 스프라이트 시트 커스터마이징 (행/열 자유 지정)
- 시스템 트레이에서 설정 관리

## 설치

### Claude Code 플러그인으로 설치 (권장)

```
/plugin https://github.com/watchingai/watchingai
```

플러그인 설치 시 데스크톱 앱이 자동으로 설치됩니다.

### 수동 설치

```bash
pip install watchingai
```

## 사용법

```bash
# 앱 실행
python -m watchingai
```

Claude Code를 사용하면 자동으로 상태가 감지되어 스프라이트가 변합니다.

## 설정

설정 파일: `~/.watchingai/config.json`

```json
{
  "position": {
    "preset": "bottom-right",
    "custom": null
  },
  "sprite": {
    "sheet": "default_sprite.png",
    "frame_width": 64,
    "frame_height": 64,
    "animations": {
      "idle": { "row": 1, "columns": [1, 2, 3] },
      "thinking": { "row": 3, "columns": [1, 2] },
      "working": { "row": 4, "columns": [1, 2, 3, 4] },
      "done": { "row": 6, "columns": [2, 4] },
      "error": { "row": 8, "columns": [1, 2, 3] }
    }
  },
  "size": 64,
  "poll_interval_ms": 1500
}
```

### 커스텀 스프라이트

1. 스프라이트 시트 이미지를 `~/.watchingai/`에 넣기
2. `config.json`에서 `sheet` 경로와 `animations` 매핑 수정
3. 행/열 인덱스는 1부터 시작

## 상태 목록

| 상태 | 설명 |
|------|------|
| Idle | Claude Code 비활성 |
| Thinking | LLM 응답 대기 중 |
| Working | 코드 생성/편집 중 |
| Done | 작업 완료 |
| Error | 에러 발생 |

## 기술 스택

- Python 3 + PyQt6
- Claude Code Plugin (bash hooks)

## 라이선스

MIT

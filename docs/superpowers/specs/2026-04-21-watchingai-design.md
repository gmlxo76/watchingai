# WatchingAI - 설계 스펙

## 개요

Claude Code 플러그인 + Windows 데스크톱 위젯 앱. Claude Code의 작업 상태를 감지하여 화면 위에 애니메이션 스프라이트 캐릭터로 표시한다. 플러그인은 hooks를 통해 상태를 로컬 파일에 기록하고, 데스크톱 앱은 해당 파일을 폴링하여 스프라이트 애니메이션을 렌더링한다.

## 아키텍처

두 개의 컴포넌트로 구성:

### A. Claude Code 플러그인
- hooks를 등록하여 Claude Code 상태 변화 감지
- 상태를 `~/.watchingai/status.json`에 기록
- setup 스크립트로 데스크톱 앱 자동 설치 (pip 또는 exe)

### B. Python 데스크톱 앱 (PyQt)
- `~/.watchingai/status.json`을 1~2초 주기로 폴링
- 투명, 프레임 없는, 항상 최상위 창에 스프라이트 애니메이션 렌더링
- 시스템 트레이 아이콘으로 설정 관리
- 사용자 설정을 `~/.watchingai/config.json`에 저장

## 상태 감지

### Claude Code Hooks 매핑

| Hook 이벤트 | 앱 상태 |
|-------------|---------|
| 세션 시작 | Idle |
| LLM 요청 시작 (thinking) | Thinking |
| 도구 호출 시작 (edit/write/bash 등) | Working |
| 응답 완료 | Done → 몇 초 후 Idle로 전환 |
| 에러 발생 | Error → 몇 초 후 Idle로 전환 |
| 세션 종료 | Idle |

### 상태 파일 (`~/.watchingai/status.json`)

```json
{
  "status": "working",
  "detail": "src/main.py 편집 중",
  "timestamp": "2026-04-21T19:30:00",
  "elapsed_seconds": 12
}
```

`timestamp`가 30초 이상 갱신되지 않으면 앱이 자동으로 Idle 상태로 전환한다.

## 데스크톱 앱 UI/UX

### 위젯
- 투명 배경 + 프레임 없는 창 (frameless)
- 항상 최상위 표시 (always-on-top)
- 드래그로 자유 이동
- 상태별 스프라이트 시트 기반 애니메이션

### 호버 툴팁
- 현재 상태 + 작업 내용 + 경과 시간 표시
- 예: "작업 중 — src/main.py 편집 중 (12초)"

### 위치 프리셋
- 좌상단 / 우상단 / 좌하단 / 우하단 / 작업표시줄 근처
- 디폴트: 우하단
- 사용자 변경 시 설정에 저장

### 시스템 트레이 메뉴
- 위치 프리셋 선택
- 스프라이트 테마 변경 (디폴트 제공 + 커스텀 이미지 경로 지정)
- 스프라이트 크기 조절
- 앱 시작/종료

## 스프라이트 시트 시스템

스프라이트 시트 이미지를 사용한다. 각 행(row)은 하나의 애니메이션 동작, 각 열(column)은 해당 동작의 프레임이다. 행/열 인덱스는 1부터 시작한다 (1-based). 사용자는 상태별로 어떤 행의 어떤 열들을 사용할지 자유롭게 지정할 수 있다.

### 설정 예시 (`~/.watchingai/config.json`)

```json
{
  "position": {
    "preset": "bottom-right",
    "custom": null
  },
  "sprite": {
    "sheet": "cat_01.png",
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

디폴트 스프라이트 시트를 기본 제공한다. 사용자는 원하는 스프라이트 시트 이미지로 교체하고 행/열 매핑을 조정할 수 있다.

## 플러그인 구조

```
watchingai-plugin/
├── plugin.json          # 플러그인 메타정보
├── setup.sh             # 데스크톱 앱 설치 스크립트
├── hooks/               # Claude Code hooks 정의
│   └── status-hook.sh   # 상태 변경 시 status.json 기록
└── skills/              # (선택) /watchingai 슬래시 커맨드
    └── watchingai.md    # 설정 변경, 상태 확인
```

## 설치 흐름

1. 사용자가 Claude Code에서 플러그인 설치
2. setup 스크립트 자동 실행:
   - Python 설치 여부 확인
   - **Python 있음** → `pip install watchingai`로 앱 설치
   - **Python 없음** → GitHub Releases에서 exe 다운로드
3. 앱 실행 + hooks 등록 완료

## 데스크톱 앱 배포

- PyPI: `watchingai` 패키지 (pip install)
- GitHub Releases: PyInstaller로 빌드한 exe
- 동일한 소스코드, 빌드 방식만 다름

## 에러 처리

- **앱이 꺼져있을 때**: 플러그인은 status.json에 계속 기록. 앱이 다시 켜지면 최신 상태를 바로 반영.
- **Claude Code 비정상 종료**: status.json의 timestamp가 30초 이상 갱신 안 되면 자동으로 Idle 전환.
- **잘못된 스프라이트 시트**: 지정한 행/열이 이미지 범위를 벗어나면 디폴트 스프라이트로 폴백.
- **설정 파일 없음/손상**: 디폴트 설정으로 자동 생성.

## 상태 목록

| 상태 | 설명 | 스프라이트 예시 |
|------|------|----------------|
| Idle | Claude Code 비활성 | 자는 캐릭터 |
| Thinking | LLM 응답 대기 중 | 갸우뚱하는 캐릭터 |
| Working | 코드 생성/편집 중 | 타이핑하는 캐릭터 |
| Done | 작업 완료 | 기지개 펴는 캐릭터 |
| Error | 에러 발생 | 놀란 캐릭터 |

## 기술 스택

- **플러그인**: Shell 스크립트 (bash), JSON 설정
- **데스크톱 앱**: Python 3, PyQt5/6
- **패키징**: PyPI (pip), PyInstaller (exe)
- **대상 플랫폼**: Windows (공개 배포)

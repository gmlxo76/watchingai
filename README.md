# WatchingAI

Claude Code의 작업 상태를 데스크톱 위에 스프라이트 캐릭터로 표시하는 Claude Code 플러그인 + Windows 데스크톱 위젯 앱.

## 기능

- Claude Code hooks로 실시간 상태 감지 (대기/생각/작업/완료/에러)
- 투명 위젯에 스프라이트 애니메이션 표시
- 마우스 호버 시 현재 작업 내용 + 경과 시간 실시간 표시
- 드래그로 자유 위치 이동
- 위치 프리셋 (좌상단/우상단/좌하단/우하단/작업표시줄 근처)
- 원본 크기 기준 비율 조절 (50%~300%)
- 상태별 프레임 커스터마이징 (트레이에서 설정)
- 시스템 트레이에서 설정 관리

## 설치

### Claude Code 플러그인으로 설치 (권장)

```
/plugin marketplace add gmlxo76/watchingai
/plugin install watchingai@watchingai
```

플러그인 설치 시 훅 등록 + 데스크톱 앱이 자동으로 설치됩니다.

### 수동 설치

```bash
pip install watchingai
```

## 사용법

### 앱 실행/종료

Claude Code에서 커스텀 커맨드로 간편하게 사용:

```
/watch_on   — 위젯 앱 실행
/watch_off  — 위젯 앱 종료
```

또는 터미널에서 직접:

```bash
watchingai
# 또는
python -m watchingai
```

### 작동 원리

1. Claude Code에서 작업하면 훅이 자동으로 상태를 감지
2. `~/.watchingai/status.json`에 상태 기록
3. 데스크톱 위젯이 1.5초마다 폴링하여 캐릭터 애니메이션 전환

### 트레이 메뉴

시스템 트레이 아이콘 우클릭:

- **위치** — 프리셋 선택 (좌상단/우상단/좌하단/우하단/작업표시줄)
- **크기** — 50%~300% 비율 조절
- **프레임 설정** — 상태별 애니메이션 프레임 선택
- **상태 테스트** — 훅 없이 상태 전환 테스트
- **종료**

## 상태 목록

| 상태 | 설명 |
|------|------|
| Idle | Claude Code 비활성 |
| Thinking | 요청 처리 중 |
| Working | 코드 생성/편집/명령 실행 중 |
| Done | 작업 완료 |
| Error | 에러 발생 |

## 기술 스택

- Python 3 + PyQt6
- Claude Code Plugin (hooks)

## 라이선스

MIT

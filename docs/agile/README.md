# AI T-Rex Runner Automator - 애자일 문서

이 디렉토리에는 Jira 프로젝트(DIN)에 import할 수 있는 애자일 문서가 포함되어 있습니다.

## 파일 구조

```
docs/agile/
├── README.md                    # 이 파일
├── JIRA_BACKLOG.md             # 전체 백로그 (마크다운)
├── jira_import_epics.csv       # Epic import용 CSV
├── jira_import_stories.csv     # User Story import용 CSV
└── jira_import_tasks.csv       # Sub-task import용 CSV
```

## Jira Import 가이드

### 방법 1: CSV Import (권장)

1. Jira 프로젝트 이동: https://letscoding.atlassian.net/jira/software/projects/DIN
2. **Project Settings** → **External System Import** → **CSV**
3. CSV 파일을 다음 순서로 import:
   1. `jira_import_epics.csv` (Epic 먼저)
   2. `jira_import_stories.csv` (Epic Link 연결됨)
   3. `jira_import_tasks.csv` (Parent 연결됨)

### 방법 2: 수동 입력

`JIRA_BACKLOG.md` 파일을 참고하여 수동으로 이슈를 생성합니다.

### 방법 3: MCP Atlassian (설정 필요)

1. `.mcp.json.example`을 `.mcp.json`으로 복사
2. Atlassian API 토큰 설정
3. Claude Code 재시작 후 자동 연동

## 프로젝트 개요

### Epics (3개)
| Epic | 설명 | 예상 기간 |
|------|------|-----------|
| Phase 1: MVP | 기본 픽셀 감지 기반 자동 플레이 | Sprint 1-2 |
| Phase 2: 고도화 | 익룡 탐지 및 정밀 타이밍 보정 | Sprint 3-4 |
| Phase 3: 지능화 | 강화학습 기반 자율 에이전트 | Sprint 5-6 |

### User Stories (11개)
- Phase 1: 4개 (US-01 ~ US-04)
- Phase 2: 4개 (US-05 ~ US-08)
- Phase 3: 3개 (US-09 ~ US-11)

### Tasks (42개)
- Phase 1: 14개 (T-01 ~ T-14)
- Phase 2: 14개 (T-15 ~ T-28)
- Phase 3: 14개 (T-29 ~ T-42)

### Story Points 합계
- Phase 1: 16 points
- Phase 2: 23 points
- Phase 3: 26 points
- **Total: 65 points**

## Sprint 계획

| Sprint | 목표 | User Stories | Story Points |
|--------|------|--------------|--------------|
| 1 | 화면 캡처 및 기본 전처리 | US-01, US-02 | 8 |
| 2 | 장애물 탐지 및 점프 기능 완성 | US-03, US-04 | 8 |
| 3 | 익룡 탐지 및 숙기 기능 | US-05, US-06 | 13 |
| 4 | 속도 적응 및 최적화 | US-07, US-08 | 10 |
| 5-6 | 강화학습 환경 및 에이전트 | US-09, US-10, US-11 | 26 |

## 성공 지표

| 지표 | 목표 값 |
|------|---------|
| 평균 점수 | 5,000점 이상 |
| 처리 지연 시간 | 50ms 이하 |

## 다음 단계

1. Jira에 이슈 import
2. 팀원 할당
3. Sprint 1 시작
4. Daily Standup 진행

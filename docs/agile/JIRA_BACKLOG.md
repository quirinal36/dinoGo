# AI T-Rex Runner Automator - Jira Backlog

> **프로젝트 키**: DIN
> **Jira URL**: https://letscoding.atlassian.net/jira/software/projects/DIN

---

## Epics 개요

| Epic ID | Epic Name | 설명 | 우선순위 |
|---------|-----------|------|----------|
| EPIC-01 | Phase 1: MVP | 기본 픽셀 감지 기반 자동 플레이 | Highest |
| EPIC-02 | Phase 2: 고도화 | 익룡 탐지 및 정밀 타이밍 보정 | High |
| EPIC-03 | Phase 3: 지능화 | 강화학습 기반 자율 에이전트 | Medium |

---

## EPIC-01: Phase 1 - MVP (Minimum Viable Product)

### Epic 상세
- **목표**: 고정된 속도에서 선인장 10개 이상 통과
- **성공 기준**: 기본 장애물 감지 및 점프 명령 전송 성공
- **예상 기간**: Sprint 1-2

### User Stories

#### US-01: 화면 캡처 기능
**As a** 시스템
**I want to** 게임 화면을 실시간으로 캡처할 수 있도록
**So that** 장애물 위치를 분석할 수 있습니다

**Acceptance Criteria:**
- [ ] 초당 30프레임 이상 캡처 가능
- [ ] 게임 캔버스 영역만 정확히 추출
- [ ] 캡처 지연 시간 10ms 이하

**Story Points**: 5

---

#### US-02: 이미지 전처리 기능
**As a** 시스템
**I want to** 캡처된 이미지를 전처리할 수 있도록
**So that** 장애물 탐지 정확도를 높일 수 있습니다

**Acceptance Criteria:**
- [ ] 컬러 → 흑백 변환 구현
- [ ] 노이즈 제거 필터 적용
- [ ] 윤곽선(Edge) 추출 기능

**Story Points**: 3

---

#### US-03: 기본 장애물 탐지
**As a** 시스템
**I want to** 선인장 장애물을 탐지할 수 있도록
**So that** 적절한 시점에 점프 명령을 내릴 수 있습니다

**Acceptance Criteria:**
- [ ] ROI(Region of Interest) 영역 설정
- [ ] 검은색 픽셀 감지 로직 구현
- [ ] 장애물과의 수평 거리 계산

**Story Points**: 5

---

#### US-04: 키보드 입력 제어
**As a** 시스템
**I want to** 저지연 키보드 입력을 전송할 수 있도록
**So that** 정확한 타이밍에 공룡을 점프시킬 수 있습니다

**Acceptance Criteria:**
- [ ] PyDirectInput 기반 입력 시스템
- [ ] Space 키 점프 명령 구현
- [ ] 입력 지연 5ms 이하

**Story Points**: 3

---

### Tasks for EPIC-01

| Task ID | Task Name | User Story | 담당자 | 예상시간 | 상태 |
|---------|-----------|------------|--------|----------|------|
| T-01 | MSS 라이브러리 설정 및 화면 캡처 모듈 구현 | US-01 | - | 4h | To Do |
| T-02 | 캡처 영역 좌표 설정 로직 구현 | US-01 | - | 2h | To Do |
| T-03 | FPS 측정 및 최적화 | US-01 | - | 2h | To Do |
| T-04 | OpenCV 그레이스케일 변환 구현 | US-02 | - | 2h | To Do |
| T-05 | Canny Edge Detection 적용 | US-02 | - | 2h | To Do |
| T-06 | 전처리 파이프라인 통합 | US-02 | - | 2h | To Do |
| T-07 | 공룡 앞 ROI 영역 정의 | US-03 | - | 2h | To Do |
| T-08 | 픽셀 밀도 기반 장애물 감지 알고리즘 | US-03 | - | 4h | To Do |
| T-09 | 거리 계산 함수 구현 | US-03 | - | 2h | To Do |
| T-10 | PyDirectInput 환경 설정 | US-04 | - | 1h | To Do |
| T-11 | 점프 명령 전송 함수 구현 | US-04 | - | 2h | To Do |
| T-12 | 입력 지연 측정 및 최적화 | US-04 | - | 2h | To Do |
| T-13 | 메인 게임 루프 통합 | - | - | 4h | To Do |
| T-14 | 통합 테스트 및 버그 수정 | - | - | 4h | To Do |

---

## EPIC-02: Phase 2 - 고도화 (Optimization)

### Epic 상세
- **목표**: 다양한 장애물에 대응 (익룡 포함)
- **성공 기준**: 익룡 탐지 및 숙기 기능, 속도 적응
- **예상 기간**: Sprint 3-4

### User Stories

#### US-05: 익룡 탐지 기능
**As a** 시스템
**I want to** 익룡(Pterodactyl)을 탐지할 수 있도록
**So that** 높이에 따라 점프 또는 숙기를 결정할 수 있습니다

**Acceptance Criteria:**
- [ ] 익룡 형태 패턴 인식
- [ ] 높이별 익룡 분류 (상단/중단/하단)
- [ ] 선인장과 익룡 구분 가능

**Story Points**: 8

---

#### US-06: 숙기(Duck) 기능
**As a** 시스템
**I want to** 하향 키(↓) 입력으로 숙기를 할 수 있도록
**So that** 높이가 높은 익룡을 피할 수 있습니다

**Acceptance Criteria:**
- [ ] Down Arrow 키 입력 구현
- [ ] 숙기 지속 시간 제어
- [ ] 점프 vs 숙기 결정 로직

**Story Points**: 5

---

#### US-07: 게임 속도 측정
**As a** 시스템
**I want to** 현재 게임 속도를 측정할 수 있도록
**So that** 반응 거리를 동적으로 조정할 수 있습니다

**Acceptance Criteria:**
- [ ] 프레임 간 장애물 이동 거리 계산
- [ ] 속도 추정 알고리즘 구현
- [ ] 속도 변화 트래킹

**Story Points**: 5

---

#### US-08: 동적 임계값 조정
**As a** 시스템
**I want to** 속도에 따라 반응 거리를 조정할 수 있도록
**So that** 빠른 속도에서도 정확한 타이밍에 반응할 수 있습니다

**Acceptance Criteria:**
- [ ] 속도-거리 매핑 함수 구현
- [ ] Search Window 동적 확장
- [ ] 점프 타이밍 보정 로직

**Story Points**: 5

---

### Tasks for EPIC-02

| Task ID | Task Name | User Story | 담당자 | 예상시간 | 상태 |
|---------|-----------|------------|--------|----------|------|
| T-15 | 익룡 이미지 템플릿 수집 | US-05 | - | 2h | To Do |
| T-16 | 템플릿 매칭 알고리즘 구현 | US-05 | - | 4h | To Do |
| T-17 | 익룡 높이 분류 로직 | US-05 | - | 3h | To Do |
| T-18 | 장애물 타입 분류기 통합 | US-05 | - | 2h | To Do |
| T-19 | Down Arrow 키 입력 함수 | US-06 | - | 1h | To Do |
| T-20 | 숙기 지속 시간 타이머 | US-06 | - | 2h | To Do |
| T-21 | 행동 결정 로직 (Jump/Duck/Stay) | US-06 | - | 3h | To Do |
| T-22 | 프레임 간 이동 거리 계산 | US-07 | - | 3h | To Do |
| T-23 | 속도 추정 알고리즘 | US-07 | - | 3h | To Do |
| T-24 | 속도 데이터 버퍼링 및 평활화 | US-07 | - | 2h | To Do |
| T-25 | 속도-거리 매핑 함수 설계 | US-08 | - | 2h | To Do |
| T-26 | 동적 ROI 확장 로직 | US-08 | - | 3h | To Do |
| T-27 | 타이밍 보정 파라미터 튜닝 | US-08 | - | 4h | To Do |
| T-28 | Phase 2 통합 테스트 | - | - | 4h | To Do |

---

## EPIC-03: Phase 3 - 지능화 (Intelligence)

### Epic 상세
- **목표**: 자가 학습을 통한 성능 향상
- **성공 기준**: 인간의 기록을 넘어서는 초고속 단계 생존
- **예상 기간**: Sprint 5-6

### User Stories

#### US-09: RL 환경 구축
**As a** 개발자
**I want to** OpenAI Gym 호환 환경을 구축할 수 있도록
**So that** 강화학습 에이전트를 학습시킬 수 있습니다

**Acceptance Criteria:**
- [ ] Gym 환경 클래스 구현 (reset, step, render)
- [ ] 상태 공간 정의 (observation space)
- [ ] 행동 공간 정의 (action space)
- [ ] 보상 함수 설계

**Story Points**: 8

---

#### US-10: RL 에이전트 학습
**As a** 시스템
**I want to** PPO/DQN 알고리즘으로 에이전트를 학습할 수 있도록
**So that** 자율적으로 최적의 행동을 결정할 수 있습니다

**Acceptance Criteria:**
- [ ] Stable Baselines3 통합
- [ ] 학습 파이프라인 구축
- [ ] 하이퍼파라미터 튜닝
- [ ] 모델 저장/로드 기능

**Story Points**: 13

---

#### US-11: 성능 평가 및 비교
**As a** 개발자
**I want to** 규칙 기반 vs RL 에이전트 성능을 비교할 수 있도록
**So that** 각 접근법의 장단점을 파악할 수 있습니다

**Acceptance Criteria:**
- [ ] 평가 메트릭 정의 (평균 점수, 최고 점수, 생존 시간)
- [ ] 자동화된 평가 스크립트
- [ ] 결과 시각화 및 리포트

**Story Points**: 5

---

### Tasks for EPIC-03

| Task ID | Task Name | User Story | 담당자 | 예상시간 | 상태 |
|---------|-----------|------------|--------|----------|------|
| T-29 | Gym 환경 기본 구조 구현 | US-09 | - | 4h | To Do |
| T-30 | 상태 공간(Observation) 정의 | US-09 | - | 3h | To Do |
| T-31 | 행동 공간(Action) 정의 | US-09 | - | 2h | To Do |
| T-32 | 보상 함수 설계 및 구현 | US-09 | - | 4h | To Do |
| T-33 | 환경-게임 연동 테스트 | US-09 | - | 3h | To Do |
| T-34 | Stable Baselines3 설정 | US-10 | - | 2h | To Do |
| T-35 | PPO 에이전트 학습 스크립트 | US-10 | - | 4h | To Do |
| T-36 | DQN 에이전트 학습 스크립트 | US-10 | - | 4h | To Do |
| T-37 | 하이퍼파라미터 튜닝 실험 | US-10 | - | 8h | To Do |
| T-38 | 모델 체크포인트 저장/로드 | US-10 | - | 2h | To Do |
| T-39 | 평가 메트릭 정의 | US-11 | - | 2h | To Do |
| T-40 | 자동화 평가 스크립트 | US-11 | - | 3h | To Do |
| T-41 | 결과 시각화 (Matplotlib/TensorBoard) | US-11 | - | 3h | To Do |
| T-42 | 최종 성능 리포트 작성 | US-11 | - | 2h | To Do |

---

## Sprint 계획 (제안)

### Sprint 1 (2주)
- **목표**: 화면 캡처 및 기본 전처리
- **User Stories**: US-01, US-02
- **Story Points**: 8

### Sprint 2 (2주)
- **목표**: 장애물 탐지 및 점프 기능 완성
- **User Stories**: US-03, US-04
- **Story Points**: 8

### Sprint 3 (2주)
- **목표**: 익룡 탐지 및 숙기 기능
- **User Stories**: US-05, US-06
- **Story Points**: 13

### Sprint 4 (2주)
- **목표**: 속도 적응 및 최적화
- **User Stories**: US-07, US-08
- **Story Points**: 10

### Sprint 5-6 (4주)
- **목표**: 강화학습 환경 및 에이전트
- **User Stories**: US-09, US-10, US-11
- **Story Points**: 26

---

## Definition of Done (DoD)

- [ ] 코드 작성 완료 및 린팅 통과
- [ ] 단위 테스트 작성 및 통과
- [ ] 코드 리뷰 완료
- [ ] 기능 테스트 완료
- [ ] 문서화 완료 (README, 주석)
- [ ] 성능 기준 충족 (지연 시간 등)

---

## 기술 부채 및 리스크

| 리스크 | 영향 | 완화 방안 |
|--------|------|-----------|
| 화면 캡처 성능 부족 | High | MSS 외 대안 라이브러리 조사 |
| 브라우저 호환성 이슈 | Medium | Chrome 전용으로 제한 |
| RL 학습 시간 과다 | High | GPU 활용, 샘플 효율적 알고리즘 |
| 게임 UI 변경 | Low | 템플릿 업데이트 프로세스 정립 |

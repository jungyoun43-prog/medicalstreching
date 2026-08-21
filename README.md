# 체형교정 운동처방 Agent

거북목·라운드숄더·척추측만 사용자의 신체 조건, 운동 목적, 가용 도구를 입력받아
맞춤 교정운동 프로그램을 **생성 → 안전성 검증 → 재시도** 루프로 처방하는 Agentic AI (Medical AI Study 4주차 MVP).

> ⚠ 교육용 프로젝트입니다. 의학적 진단·치료를 제공하지 않으며, 모든 출력에 전문가 상담 고지를 포함합니다.

## 단순 프롬프트와 다른 점 (Agentic 요소)

| 요소 | 구현 위치 | 내용 |
|---|---|---|
| **Decision** | `graph/nodes.py::screen_node` | red flag(방사통·저림·NRS≥7·외상) 감지 시 처방 대신 병원 안내(`REFER`)로 분기 — 그래프 구조상 우회 불가 |
| **Tool Use** | `tools/retrieval.py` | 운동은 팀이 직접 구축한 DB 30개에서만 검색 — LLM이 지어낸 운동 원천 차단 |
| **Validation** | `eval/validator.py` | 금기·도구·시간·난이도·DB존재를 **LLM 없이 순수 Python 규칙**으로 검증 |
| **Loop** | `graph/nodes.py::feedback_node` | 위반 사유를 제약(제외 목록·전략 변경)으로 변환해 Composer 재호출, 최대 3회 |

## 빠른 시작

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# 웹 UI 데모 (API 키 불필요)
.venv/bin/streamlit run app.py           # http://localhost:8501

# CLI 데모
.venv/bin/python main.py --list          # 테스트 케이스 12개 목록
.venv/bin/python main.py --case N1       # 성공 사례
.venv/bin/python main.py --case R1       # red flag 분기 사례
.venv/bin/python main.py --case C1       # 검증 실패 → 루프 → 통과 사례
.venv/bin/python main.py --case I2       # 3회 재시도 후 FAIL 사례

# 전체 평가 (12케이스 기대 라벨 비교 + 안전성 지표)
.venv/bin/python -m eval.run_eval
```

LLM 모드: `export ANTHROPIC_API_KEY=...` 설정 시 Composer가 LLM(기본 `claude-opus-5`)으로 전환됩니다.
다른 모델은 `export POSTURE_LLM="openai:gpt-..."` (해당 `langchain-*` 패키지 설치 필요).
LLM 호출이 실패하면 자동으로 오프라인 Composer로 폴백합니다.

## Workflow

```
Input → Intake Parser → Red Flag Screening ─(위험)→ 🏥 REFER
                              │(안전)
                        Exercise Retrieval (Tool: DB 필터) ─(후보<4)→ FAIL
                              │
                        Program Composer ←──────────────┐
                              │                          │
                        Safety Validator ─(위반)→ Constraint Feedback  (max 3회)
                              │(통과)                     │(3회 초과)
                        ✅ PASS / REVISED                FAIL
```

최종 라벨: `PASS`(1회 통과) / `REVISED`(루프 후 통과) / `REFER`(병원 안내) / `FAIL`(조건 충족 불가 → 완화 제안)

## 현재 평가 결과 (오프라인 모드, 결정적 재현 가능)

라벨 일치 **12/12**, 최종 출력 안전성 위반(금기·hallucination) **0건**.

## 구조 및 역할 분담

| 디렉토리 | 내용 | 담당 역할 |
|---|---|---|
| `data/` | 운동 라이브러리 30개(`exercises.json`), 테스트 케이스 12개 | Data |
| `tools/` | DB 검색, 입력 정규화, Composer, LLM 연동 | Retrieval / Tool |
| `graph/` | LangGraph State·Node·Edge·Loop | Agent Workflow |
| `eval/` | Safety Validator, 평가 스크립트 | Evaluation |
| `app.py` | Streamlit 웹 UI (설문 폼 + 결과 카드 + 실행 로그) | Integration |
| `main.py` | CLI 데모, 출력 카드 | Integration |

브랜치 규칙: `main`에서 역할별 브랜치(`feat/data`, `feat/tool`, `feat/graph`, `feat/eval`, `feat/integration`)를 따고 PR로 병합.

## TODO (시간 남으면)

- [ ] `data/assets/` 운동 이미지 추가 (현재 placeholder 경로만 존재)
- [ ] 자연어 설문 입력 → Intake Parser LLM 파싱
- [ ] Europe PMC API로 운동별 근거 논문 첨부
- [ ] Streamlit Community Cloud 배포 (GitHub 연동)

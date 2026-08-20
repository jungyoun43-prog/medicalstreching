"""LangGraph 노드 및 분기 함수.

Agentic 요소 매핑:
  screen_node  → DECISION   (red flag이면 처방 대신 병원 안내로 분기)
  retrieve_node→ TOOL USE   (운동 DB 검색 — LLM이 지어낸 운동 차단)
  validate_node→ VALIDATION (규칙 기반 안전성 검증)
  feedback_node→ LOOP       (위반을 제약으로 변환해 Composer 재호출)
"""
from eval.validator import PROGRAM_MIN, validate
from graph.state import AgentState
from tools.composer import naive_compose
from tools.intake import normalize
from tools.llm import compose_with_llm
from tools.retrieval import db_by_id, search_exercises

MAX_ATTEMPTS = 3

DISCLAIMER = "본 프로그램은 교육용 데모이며 의료 전문가의 진단·상담을 대체하지 않습니다."


# ---------- 노드 ----------

def intake_node(state: AgentState) -> dict:
    user = normalize(state["user"])
    return {
        "user": user,
        "attempts": 0,
        "excluded_ids": [],
        "strategy": "balanced",
        "log": [f"[Intake] 정규화 완료 — {user['condition_suspected']}, NRS {user['pain']['nrs']}, "
                f"도구 {user['equipment'] or '없음'}, 하루 {user['time_per_day_min']}분, {user['level']}"],
    }


RED_FLAG_LABELS = {"numbness": "저림/감각 이상", "night_pain": "야간통", "recent_trauma": "최근 외상"}


def screen_node(state: AgentState) -> dict:
    """DECISION: red flag 스크리닝. 그래프 구조상 어떤 경로도 이 노드를 우회할 수 없다."""
    user = state["user"]
    flags = [RED_FLAG_LABELS.get(k, k) for k, v in user["red_flags"].items() if v]
    if user["pain"]["nrs"] >= 7:
        flags.append(f"심한 통증(NRS {user['pain']['nrs']})")
    if user["pain"].get("radiating"):
        flags.append("방사통")
    if flags:
        reason = ", ".join(flags)
        return {"route": "refer", "result": "REFER", "reason": reason,
                "log": [f"[Screening] ⚠ red flag 감지: {reason} → 운동 처방 중단, 병원 안내"]}
    return {"route": "proceed", "log": ["[Screening] red flag 없음 → 처방 진행"]}


def retrieve_node(state: AgentState) -> dict:
    """TOOL USE: 운동 DB 검색 (질환·도구·난이도 하드 필터)."""
    user = state["user"]
    candidates = search_exercises(user["condition_suspected"], user["equipment"], user["level"])
    log = [f"[Retrieval] 후보 {len(candidates)}개 검색됨: "
           + ", ".join(e["id"] for e in candidates)]
    if len(candidates) < PROGRAM_MIN:
        return {"candidates": candidates, "route": "fail",
                "reason": f"조건에 맞는 후보 운동이 {len(candidates)}개뿐 (최소 {PROGRAM_MIN}개 필요)",
                "log": log + ["[Retrieval] 후보 부족 → FAIL 경로"]}
    return {"candidates": candidates, "route": "compose", "log": log}


def compose_node(state: AgentState) -> dict:
    """프로그램 초안 생성. LLM이 있으면 LLM, 없으면 규칙 기반(오프라인 모드)."""
    attempts = state["attempts"] + 1
    program = compose_with_llm(state["user"], state["candidates"],
                               state["excluded_ids"], state.get("violations", []))
    source = "LLM"
    if program is None:
        program = naive_compose(state["candidates"], state["excluded_ids"], state["strategy"])
        source = f"offline/{state['strategy']}"
    return {
        "program": program, "attempts": attempts,
        "log": [f"[Composer:{source}] 시도 {attempts} — "
                + ", ".join(f"{e['id']}({e['duration_min']}분)" for e in program)],
    }


def validate_node(state: AgentState) -> dict:
    """VALIDATION: 규칙 기반 안전성 검증."""
    violations = validate(state["program"], state["user"], db_by_id())
    if violations:
        log = [f"[Validator] ✗ 위반 {len(violations)}건: "
               + " / ".join(v["detail"] for v in violations)]
    else:
        log = ["[Validator] ✓ 모든 안전성 검사 통과"]
    return {"violations": violations, "log": log}


def feedback_node(state: AgentState) -> dict:
    """LOOP: 위반 내역을 다음 Composer 호출의 제약으로 변환."""
    excluded = set(state["excluded_ids"])
    strategy = state["strategy"]
    for v in state["violations"]:
        if v["exercise_id"] and v["rule"] in (
                "contraindication", "equipment", "difficulty", "condition_mismatch", "not_in_db"):
            excluded.add(v["exercise_id"])
        if v["rule"] == "time_budget":
            strategy = "shortest"
    return {
        "excluded_ids": sorted(excluded), "strategy": strategy,
        "log": [f"[Feedback] 제외 목록 {sorted(excluded) or '없음'}, 전략 → {strategy} → 재생성"],
    }


def finalize_node(state: AgentState) -> dict:
    result = "PASS" if state["attempts"] == 1 else "REVISED"
    return {"result": result,
            "log": [f"[Output] {result} — 시도 {state['attempts']}회 만에 검증 통과"]}


def refer_node(state: AgentState) -> dict:
    return {"program": [],
            "log": ["[Output] REFER — 아래 증상은 운동으로 해결할 단계가 아닙니다. "
                    "정형외과/재활의학과 진료를 먼저 받으세요: " + state["reason"]]}


def fail_node(state: AgentState) -> dict:
    reason = state.get("reason") or (
        f"{MAX_ATTEMPTS}회 재시도 후에도 안전성 검증을 통과하지 못함 — 마지막 위반: "
        + " / ".join(v["detail"] for v in state.get("violations", []))
    )
    return {"result": "FAIL", "reason": reason, "program": [],
            "log": [f"[Output] FAIL — {reason}",
                    "[Output] 제안: 가용 시간을 늘리거나, 통증·기저질환에 대해 전문가와 상담 후 재시도하세요."]}


# ---------- 분기 함수 (conditional edges) ----------

def route_after_screen(state: AgentState) -> str:
    return state["route"]                      # "refer" | "proceed"


def route_after_retrieve(state: AgentState) -> str:
    return state["route"]                      # "compose" | "fail"


def route_after_validate(state: AgentState) -> str:
    if not state["violations"]:
        return "finalize"
    if state["attempts"] >= MAX_ATTEMPTS:
        return "fail"
    return "retry"

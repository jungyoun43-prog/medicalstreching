"""Safety Validator — 규칙 기반, LLM 없이 결정적으로 동작.

"금기 운동 0건"은 프롬프트로 보장할 수 없고 이 코드 레벨 검증으로만
보장된다. 위반은 {"rule", "exercise_id", "detail"} 목록으로 반환하고,
그래프의 feedback 노드가 이를 다음 Composer 호출의 제약으로 변환한다.
"""
from tools.retrieval import LEVEL_RANK

PROGRAM_MIN, PROGRAM_MAX = 4, 6


def validate(program: list[dict], user: dict, db_by_id: dict[str, dict]) -> list[dict]:
    violations: list[dict] = []

    if not PROGRAM_MIN <= len(program) <= PROGRAM_MAX:
        violations.append({
            "rule": "program_size", "exercise_id": None,
            "detail": f"운동 개수 {len(program)}개 (허용: {PROGRAM_MIN}~{PROGRAM_MAX}개)",
        })

    ids = [e["id"] for e in program]
    if len(ids) != len(set(ids)):
        violations.append({"rule": "duplicate", "exercise_id": None, "detail": "중복 운동 포함"})

    user_flags = set(user.get("conditions", []))
    owned = set(user.get("equipment", []))
    rank = LEVEL_RANK.get(user["level"], 1)

    for e in program:
        ex = db_by_id.get(e["id"])
        if ex is None:  # hallucination — DB에 없는 운동
            violations.append({
                "rule": "not_in_db", "exercise_id": e["id"],
                "detail": f"{e['id']}는 운동 DB에 없음 (hallucination)",
            })
            continue
        if user["condition_suspected"] not in ex["condition"]:
            violations.append({
                "rule": "condition_mismatch", "exercise_id": ex["id"],
                "detail": f"{ex['name']}은(는) {user['condition_suspected']} 대상 운동이 아님",
            })
        hits = user_flags & set(ex["contraindications"])
        if hits:
            violations.append({
                "rule": "contraindication", "exercise_id": ex["id"],
                "detail": f"{ex['name']} — 금기 해당: {', '.join(sorted(hits))}",
            })
        missing = set(ex["equipment"]) - owned
        if missing:
            violations.append({
                "rule": "equipment", "exercise_id": ex["id"],
                "detail": f"{ex['name']} — 없는 도구 필요: {', '.join(sorted(missing))}",
            })
        if ex["difficulty"] > rank:
            violations.append({
                "rule": "difficulty", "exercise_id": ex["id"],
                "detail": f"{ex['name']} — 난이도 {ex['difficulty']} > 사용자 레벨({user['level']})",
            })

    total = sum(db_by_id[i]["duration_min"] for i in ids if i in db_by_id)
    if total > user["time_per_day_min"]:
        violations.append({
            "rule": "time_budget", "exercise_id": None,
            "detail": f"총 {total}분 > 가용 시간 {user['time_per_day_min']}분",
        })

    return violations

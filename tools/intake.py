"""사용자 입력(설문 JSON) 정규화.

MVP에서는 구조화된 설문 JSON을 받는다. 자연어 입력 파싱(LLM)은
tools.llm.parse_natural 로 확장 가능하다.
"""

VALID_CONDITIONS = {"거북목", "라운드숄더", "척추측만"}
VALID_LEVELS = {"beginner", "intermediate"}

DEFAULTS = {
    "conditions": [],
    "equipment": [],
    "goal": "자세 교정",
    "time_per_day_min": 20,
    "level": "beginner",
}


class IntakeError(ValueError):
    pass


def normalize(raw: dict) -> dict:
    user = {**DEFAULTS, **raw}

    if user.get("condition_suspected") not in VALID_CONDITIONS:
        raise IntakeError(
            f"condition_suspected는 {sorted(VALID_CONDITIONS)} 중 하나여야 합니다: "
            f"{user.get('condition_suspected')!r}"
        )
    if user["level"] not in VALID_LEVELS:
        raise IntakeError(f"level은 {sorted(VALID_LEVELS)} 중 하나여야 합니다: {user['level']!r}")

    pain = {"site": "", "nrs": 0, "radiating": False, **user.get("pain", {})}
    if not 0 <= int(pain["nrs"]) <= 10:
        raise IntakeError(f"NRS는 0~10이어야 합니다: {pain['nrs']}")
    user["pain"] = pain

    user["red_flags"] = {
        "numbness": False, "night_pain": False, "recent_trauma": False,
        **user.get("red_flags", {}),
    }
    user["time_per_day_min"] = int(user["time_per_day_min"])
    return user

"""프로그램 Composer.

- LLM 모드: tools.llm.compose_with_llm 이 후보 중에서 선택 (API 키 필요)
- 오프라인 모드: naive_compose — 결정적 규칙 기반 선택

naive_compose는 의도적으로 금기를 확인하지 않는다. 실제 LLM처럼
"그럴듯하지만 안전하지 않을 수 있는" 초안을 만들고, Safety Validator가
잡아내서 루프가 돌게 하는 것이 데모의 핵심이다.
"""

PROGRAM_SIZE = 4
TYPE_ORDER = {"stretching": 0, "mobility": 1, "strengthening": 2}


def naive_compose(candidates: list[dict], excluded_ids: list[str],
                  strategy: str = "balanced", k: int = PROGRAM_SIZE) -> list[dict]:
    pool = [e for e in candidates if e["id"] not in set(excluded_ids)]

    if strategy == "shortest":
        chosen = sorted(pool, key=lambda e: (e["duration_min"], e["id"]))[:k]
    else:  # balanced: 스트레칭 2 + 가동성 1 + 강화로 채우기
        chosen = [e for e in pool if e["type"] == "stretching"][:2]
        chosen += [e for e in pool if e["type"] == "mobility"][:1]
        for e in pool:
            if len(chosen) >= k:
                break
            if e["type"] == "strengthening" and e not in chosen:
                chosen.append(e)
        for e in pool:  # 그래도 모자라면 남은 후보로 채움
            if len(chosen) >= k:
                break
            if e not in chosen:
                chosen.append(e)

    # 프로그램 순서: 스트레칭 → 가동성 → 강화
    return sorted(chosen, key=lambda e: (TYPE_ORDER[e["type"]], e["id"]))

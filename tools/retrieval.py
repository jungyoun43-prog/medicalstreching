"""운동 라이브러리 DB 검색 Tool.

Agent가 지어낸 운동을 쓰지 못하게, 프로그램에 들어갈 수 있는 운동은
이 모듈이 반환한 후보로 제한된다.

의도적으로 여기서는 금기(contraindication)를 필터링하지 않는다 —
금기 검출은 Safety Validator의 책임이고, 그래야 검증 실패 → 재생성
루프가 실제로 동작하는 모습을 보여줄 수 있다.
"""
import json
from functools import lru_cache
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "exercises.json"

LEVEL_RANK = {"beginner": 1, "intermediate": 2}


@lru_cache(maxsize=1)
def load_db() -> tuple[dict, ...]:
    with open(DB_PATH, encoding="utf-8") as f:
        return tuple(json.load(f))


def db_by_id() -> dict[str, dict]:
    return {e["id"]: e for e in load_db()}


def search_exercises(condition: str, equipment: list[str], level: str) -> list[dict]:
    """질환·보유 도구·난이도로 후보 운동을 필터링한다 (하드 제약)."""
    rank = LEVEL_RANK.get(level, 1)
    owned = set(equipment)
    return [
        e for e in load_db()
        if condition in e["condition"]
        and e["difficulty"] <= rank
        and set(e["equipment"]) <= owned
    ]

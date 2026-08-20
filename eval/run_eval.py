"""평가 스크립트 — 테스트 케이스 12개 전체 실행.

  python -m eval.run_eval

각 케이스의 기대 라벨(PASS/REVISED/REFER/FAIL)과 실제 결과를 비교하고,
안전성 핵심 지표(금기 포함 0건, hallucination 0건)를 별도로 집계한다.
불일치가 있으면 exit code 1.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval.validator import validate  # noqa: E402
from graph.workflow import run  # noqa: E402
from tools.retrieval import db_by_id  # noqa: E402

CASES_PATH = Path(__file__).resolve().parent.parent / "data" / "test_cases.json"


def main() -> int:
    with open(CASES_PATH, encoding="utf-8") as f:
        cases = json.load(f)

    rows, mismatches = [], 0
    safety_violations = 0  # 최종 출력에 금기/hallucination이 남아있는 건수

    for c in cases:
        state = run(c["input"])
        actual = state.get("result", "?")
        ok = actual == c["expected"]
        mismatches += not ok

        # 핵심 안전 지표: 최종 프로그램을 다시 한 번 독립 검증
        final_violations = []
        if state.get("program"):
            final_violations = validate(state["program"], state["user"], db_by_id())
        safety_violations += len(final_violations)

        rows.append((c["id"], c["expected"], actual, state.get("attempts", 0),
                     "✓" if ok else "✗ MISMATCH", c["description"]))

    print(f"{'ID':4s} {'기대':9s} {'실제':9s} {'시도':4s} {'판정':10s} 설명")
    print("-" * 100)
    for r in rows:
        print(f"{r[0]:4s} {r[1]:9s} {r[2]:9s} {r[3]:^4d} {r[4]:10s} {r[5]}")

    n = len(cases)
    print("-" * 100)
    print(f"라벨 일치: {n - mismatches}/{n}")
    print(f"최종 출력 안전성 위반(금기·hallucination 등): {safety_violations}건 (목표: 0)")

    if mismatches or safety_violations:
        print("\n❌ 평가 실패")
        return 1
    print("\n✅ 전체 통과")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""데모 CLI.

사용법:
  python main.py --case N1                  # data/test_cases.json의 케이스 실행
  python main.py --input my_intake.json     # 직접 만든 설문 JSON 실행
  python main.py --list                     # 케이스 목록

API 키 없이 실행하면 오프라인(규칙 기반) Composer로 동작한다.
"""
import argparse
import json
from pathlib import Path

from graph.nodes import DISCLAIMER
from graph.workflow import run

CASES_PATH = Path(__file__).resolve().parent / "data" / "test_cases.json"


def load_cases() -> dict[str, dict]:
    with open(CASES_PATH, encoding="utf-8") as f:
        return {c["id"]: c for c in json.load(f)}


def print_result(state: dict) -> None:
    print("\n===== Agent 실행 로그 =====")
    for line in state["log"]:
        print(" ", line)

    print("\n===== 최종 결과 =====")
    print(f"판정: {state.get('result', '?')}")
    if state.get("reason"):
        print(f"사유: {state['reason']}")

    program = state.get("program") or []
    if program:
        total = sum(e["duration_min"] for e in program)
        print(f"\n📋 맞춤 교정운동 프로그램 (총 {total}분, {len(program)}개)")
        for i, e in enumerate(program, 1):
            print(f"\n  {i}. {e['name']}  [{e['type']}, {e['duration_min']}분]")
            print(f"     처방: {e['dose']}")
            print(f"     방법: {e['cues']}")
            if e["equipment"]:
                print(f"     도구: {', '.join(e['equipment'])}")
            print(f"     이미지: {e['image']}")
    print(f"\n⚠ {DISCLAIMER}")


def main() -> None:
    ap = argparse.ArgumentParser(description="체형교정 운동처방 Agent 데모")
    ap.add_argument("--case", help="test_cases.json의 케이스 id (예: N1, R1, C1, I2)")
    ap.add_argument("--input", help="사용자 설문 JSON 파일 경로")
    ap.add_argument("--list", action="store_true", help="테스트 케이스 목록 출력")
    args = ap.parse_args()

    if args.list:
        for cid, c in load_cases().items():
            print(f"  {cid:3s}  [{c['expected']:7s}]  {c['description']}")
        return

    if args.case:
        cases = load_cases()
        if args.case not in cases:
            ap.error(f"케이스 {args.case!r} 없음. --list로 확인하세요.")
        user_input = cases[args.case]["input"]
        print(f"케이스 {args.case}: {cases[args.case]['description']}")
    elif args.input:
        with open(args.input, encoding="utf-8") as f:
            user_input = json.load(f)
    else:
        ap.error("--case 또는 --input 중 하나를 지정하세요.")
        return

    print_result(run(user_input))


if __name__ == "__main__":
    main()

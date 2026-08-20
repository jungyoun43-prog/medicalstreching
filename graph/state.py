import operator
from typing import Annotated, Any, TypedDict


class AgentState(TypedDict, total=False):
    user: dict[str, Any]            # 정규화된 사용자 프로필
    route: str                      # 분기 결과 ("refer" | "proceed" | "compose" | "fail")
    candidates: list[dict]          # Tool: 운동 DB 검색 결과
    excluded_ids: list[str]         # 검증 실패로 제외된 운동 id (누적)
    strategy: str                   # Composer 전략 ("balanced" | "shortest")
    program: list[dict]             # 현재 프로그램
    violations: list[dict]          # 마지막 검증의 위반 목록
    attempts: int                   # Composer 시도 횟수
    result: str                     # PASS | REVISED | REFER | FAIL
    reason: str                     # REFER / FAIL 사유
    log: Annotated[list[str], operator.add]  # 데모용 실행 로그 (append 누적)

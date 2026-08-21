"""LLM 연동 (선택).

API 키가 있으면 LangChain 경유로 Claude를 사용한다.
  export ANTHROPIC_API_KEY=...          # 기본: claude-opus-5
  export POSTURE_LLM="openai:gpt-5.2"     # 다른 provider/모델로 교체 시

키가 없으면 None을 반환하고, 그래프는 오프라인(규칙 기반) Composer로
동일하게 동작한다 — 데모/평가는 키 없이도 재현 가능하다.
"""
import json
import os
import re
from pathlib import Path

DEFAULT_MODEL = "anthropic:claude-opus-5"


def _load_dotenv() -> None:
    """프로젝트 루트의 .env 파일에서 환경변수를 읽는다 (예: ANTHROPIC_API_KEY=...).

    .env는 .gitignore에 포함되어 있어 저장소에 올라가지 않는다.
    """
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()


def get_llm():
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")):
        return None
    try:
        from langchain.chat_models import init_chat_model
        return init_chat_model(os.environ.get("POSTURE_LLM", DEFAULT_MODEL))
    except Exception:
        return None


def compose_with_llm(user: dict, candidates: list[dict], excluded_ids: list[str],
                     violations: list[dict], k: int = 4) -> list[dict] | None:
    """후보 목록 안에서만 k개를 고르게 한다. 실패 시 None (naive로 폴백)."""
    llm = get_llm()
    if llm is None:
        return None

    slim = [
        {key: e[key] for key in
         ("id", "name", "type", "duration_min", "contraindications", "equipment")}
        for e in candidates if e["id"] not in set(excluded_ids)
    ]
    feedback = ""
    if violations:
        feedback = (
            "\n직전 프로그램은 안전성 검증에 실패했다. 위반 내역:\n"
            + json.dumps(violations, ensure_ascii=False, indent=1)
            + "\n같은 위반이 반복되지 않게 선택을 바꿔라."
        )
    prompt = f"""너는 교정운동 프로그램을 구성하는 보조 시스템이다.
아래 후보 목록에 있는 운동만 사용할 수 있다. 목록 밖의 운동 id를 쓰면 안 된다.

사용자 정보:
{json.dumps({key: user[key] for key in ('condition_suspected', 'conditions', 'equipment', 'time_per_day_min', 'level', 'goal')}, ensure_ascii=False)}

후보 운동 목록:
{json.dumps(slim, ensure_ascii=False)}
{feedback}
규칙:
- 정확히 {k}개 선택, 총 duration_min 합이 {user['time_per_day_min']}분 이하
- 사용자의 conditions에 해당하는 contraindications를 가진 운동 금지
- 순서: stretching → mobility → strengthening

id 배열만 JSON으로 출력하라. 예: ["EX-002", "EX-003", "EX-010", "EX-001"]"""

    try:
        text = llm.invoke(prompt).content
        if isinstance(text, list):  # content block 리스트인 경우
            text = "".join(b.get("text", "") for b in text if isinstance(b, dict))
        match = re.search(r"\[.*?\]", text, re.S)
        ids = json.loads(match.group(0)) if match else []
        by_id = {e["id"]: e for e in candidates}
        program = [by_id[i] for i in ids if i in by_id]
        return program if program else None
    except Exception:
        return None

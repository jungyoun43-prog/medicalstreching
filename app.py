"""Streamlit 웹 UI — 체형교정 운동처방 Agent.

실행:
  streamlit run app.py

API 키 없이 오프라인(규칙 기반) 모드로 동작하며,
ANTHROPIC_API_KEY 설정 시 Composer가 LLM 모드로 전환된다.
"""
from pathlib import Path

import streamlit as st

from graph.nodes import DISCLAIMER
from graph.workflow import run

DATA_DIR = Path(__file__).resolve().parent / "data"

CONDITION_VOCAB = [
    "어깨 충돌증후군", "손목 통증", "무릎 통증",
    "어지럼증", "고혈압", "급성 요통", "임신", "급성 경추 방사통",
]
EQUIPMENT_VOCAB = ["폼롤러", "밴드", "수건"]
RED_FLAG_OPTIONS = {
    "팔/손 저림·감각 이상": "numbness",
    "밤에 잠을 깨울 정도의 통증(야간통)": "night_pain",
    "최근 낙상·사고 등 외상": "recent_trauma",
}

RESULT_STYLE = {
    "PASS": ("✅ PASS", "1회 생성으로 안전성 검증을 통과했습니다.", st.success),
    "REVISED": ("🔁 REVISED", "1차 프로그램이 검증에 걸려, 루프를 돌아 안전하게 재구성했습니다.", st.info),
    "REFER": ("🏥 REFER", "운동으로 해결할 단계가 아닙니다. 정형외과/재활의학과 진료를 먼저 받으세요.", st.error),
    "FAIL": ("⚠️ FAIL", "조건을 만족하는 안전한 프로그램을 구성하지 못했습니다.", st.warning),
}

st.set_page_config(page_title="체형교정 운동처방 Agent", page_icon="🧘", layout="centered")

st.title("🧘 체형교정 운동처방 Agent")
st.caption("Medical AI Study 1조 · 생성 → 안전성 검증 → 재시도 루프 데모 "
           "(오프라인 모드 — API 키 불필요)")

with st.form("intake"):
    st.subheader("1. 기본 정보")
    c1, c2, c3 = st.columns(3)
    age = c1.number_input("나이", min_value=10, max_value=90, value=25)
    sex = c2.selectbox("성별", ["여성", "남성"])
    condition = c3.selectbox("의심 질환", ["거북목", "라운드숄더", "척추측만"])

    st.subheader("2. 통증과 위험 신호")
    nrs = st.slider("통증 정도 (NRS, 0=없음 ~ 10=최악)", 0, 10, 2)
    site = st.text_input("통증 부위", "목/어깨")
    radiating = st.checkbox("팔이나 다리로 뻗치는 통증(방사통)이 있다")
    red_flags_sel = st.multiselect("해당되는 증상 (해당 시 병원 안내로 분기됩니다)",
                                   list(RED_FLAG_OPTIONS))

    st.subheader("3. 조건")
    conditions = st.multiselect("기저 상태 (금기 매칭에 사용)", CONDITION_VOCAB)
    equipment = st.multiselect("보유 도구", EQUIPMENT_VOCAB)
    c4, c5 = st.columns(2)
    time_min = c4.slider("하루 운동 가능 시간(분)", 5, 60, 20)
    level = c5.radio("운동 수준", ["beginner", "intermediate"], horizontal=True,
                     format_func=lambda x: "초급" if x == "beginner" else "중급")

    submitted = st.form_submit_button("🏃 맞춤 프로그램 생성", use_container_width=True)

if submitted:
    user_input = {
        "age": age, "sex": "F" if sex == "여성" else "M",
        "condition_suspected": condition,
        "pain": {"site": site, "nrs": nrs, "radiating": radiating},
        "red_flags": {v: (k in red_flags_sel) for k, v in RED_FLAG_OPTIONS.items()},
        "conditions": conditions,
        "goal": "자세 교정",
        "equipment": equipment,
        "time_per_day_min": time_min,
        "level": level,
    }

    with st.spinner("Agent가 판단 → 검색 → 생성 → 검증 중..."):
        state = run(user_input)

    result = state.get("result", "?")
    label, desc, render = RESULT_STYLE.get(result, (result, "", st.info))
    render(f"**{label}** — {desc}")
    if state.get("reason"):
        st.caption(f"사유: {state['reason']}")

    with st.expander("🔍 Agent 실행 로그 (판단·Tool·검증·루프 과정)", expanded=True):
        st.code("\n".join(state.get("log", [])), language=None)

    program = state.get("program") or []
    if program:
        total = sum(e["duration_min"] for e in program)
        st.subheader(f"📋 맞춤 교정운동 프로그램 — 총 {total}분, {len(program)}개")
        for i, e in enumerate(program, 1):
            with st.container(border=True):
                img, body = st.columns([1, 2])
                img_path = DATA_DIR / e["image"]
                if img_path.exists():
                    img.image(str(img_path), use_container_width=True)
                body.markdown(f"**{i}. {e['name']}**  \n"
                              f"`{e['type']}` · {e['duration_min']}분")
                body.markdown(f"**처방** {e['dose']}")
                body.markdown(f"**방법** {e['cues']}")
                if e["equipment"]:
                    body.markdown(f"**도구** {', '.join(e['equipment'])}")

    st.warning(f"⚠ {DISCLAIMER}")

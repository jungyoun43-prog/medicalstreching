"""LangGraph StateGraph 조립.

Input → Intake → Red Flag Screening ─(refer)→ REFER
                        │(proceed)
                   Retrieval(Tool) ─(후보 부족)→ FAIL
                        │
                    Composer ←─────────┐
                        │              │
                    Validator ─(위반)→ Feedback   (max 3회)
                        │(통과)         │(초과)
                    Final Output      FAIL
"""
from langgraph.graph import END, START, StateGraph

from graph import nodes
from graph.state import AgentState


def build_graph():
    g = StateGraph(AgentState)

    g.add_node("intake", nodes.intake_node)
    g.add_node("screen_red_flags", nodes.screen_node)
    g.add_node("retrieve", nodes.retrieve_node)
    g.add_node("compose", nodes.compose_node)
    g.add_node("validate", nodes.validate_node)
    g.add_node("feedback", nodes.feedback_node)
    g.add_node("finalize", nodes.finalize_node)
    g.add_node("refer", nodes.refer_node)
    g.add_node("fail", nodes.fail_node)

    g.add_edge(START, "intake")
    g.add_edge("intake", "screen_red_flags")
    g.add_conditional_edges("screen_red_flags", nodes.route_after_screen,
                            {"refer": "refer", "proceed": "retrieve"})
    g.add_conditional_edges("retrieve", nodes.route_after_retrieve,
                            {"compose": "compose", "fail": "fail"})
    g.add_edge("compose", "validate")
    g.add_conditional_edges("validate", nodes.route_after_validate,
                            {"finalize": "finalize", "retry": "feedback", "fail": "fail"})
    g.add_edge("feedback", "compose")  # ← LOOP

    g.add_edge("finalize", END)
    g.add_edge("refer", END)
    g.add_edge("fail", END)
    return g.compile()


def run(user_input: dict) -> dict:
    """단일 사용자 입력에 대해 그래프를 실행하고 최종 상태를 반환한다."""
    app = build_graph()
    return app.invoke({"user": user_input, "log": []})

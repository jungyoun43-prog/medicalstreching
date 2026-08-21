"""운동 픽토그램 생성기 — data/assets/EX-0XX.png 30장.

물리치료 안내서 스타일의 스틱 픽토그램을 matplotlib으로 그린다.
스타일 규칙: 인물=틸, 소품(벽·바닥·도구)=회색, 동작 방향=앰버 화살표.
더 좋은 이미지가 생기면 같은 파일명(EX-001.png ~)으로 교체만 하면 된다.

실행: python scripts/generate_assets.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch

OUT = Path(__file__).resolve().parent.parent / "data" / "assets"
OUT.mkdir(parents=True, exist_ok=True)

BG, INK, PROP, ACC = "#F7FAF9", "#0E7C6B", "#93A6A2", "#C77F1A"


def new_fig():
    fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
    ax.set_xlim(0, 10); ax.set_ylim(0, 7.5); ax.axis("off")
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    fig.subplots_adjust(0, 0, 1, 1)
    return fig, ax


def seg(ax, *pts, color=INK, lw=5, ls="-"):
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color, lw=lw,
            ls=ls, solid_capstyle="round", solid_joinstyle="round", zorder=3)


def head(ax, x, y, r=0.42):
    ax.add_patch(Circle((x, y), r, color=INK, zorder=4))


def arrow(ax, p1, p2, rad=0.0):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=15,
                                 color=ACC, lw=2.4, zorder=5,
                                 connectionstyle=f"arc3,rad={rad}"))


def floor(ax):
    seg(ax, (0.8, 0.95), (9.2, 0.95), color=PROP, lw=3)


def wall(ax, x):
    seg(ax, (x, 0.95), (x, 7.2), color=PROP, lw=3)


def roller(ax, x, y=1.42, r=0.45):
    ax.add_patch(Circle((x, y), r, fill=False, color=PROP, lw=4, zorder=2))


def stand_side(ax, x=5.0):
    seg(ax, (x, 3.2), (x - 0.1, 2.05), (x - 0.15, 0.95))
    seg(ax, (x, 3.2), (x + 0.25, 2.05), (x + 0.3, 0.95))
    seg(ax, (x, 3.2), (x, 5.15))
    return (x, 5.15), (x, 3.2)  # shoulder, hip


def stand_front(ax, x=5.0):
    seg(ax, (x, 3.2), (x - 0.45, 2.0), (x - 0.55, 0.95))
    seg(ax, (x, 3.2), (x + 0.45, 2.0), (x + 0.55, 0.95))
    seg(ax, (x, 3.2), (x, 5.15))
    return (x, 5.15), (x, 3.2)


def quadruped(ax, arch=0.0):
    """네발기기. arch>0 등 위로 말기, <0 등 내리기."""
    seg(ax, (4.1, 0.95), (4.1, 2.55))            # 허벅지(무릎-엉덩이)
    seg(ax, (6.3, 2.55), (6.3, 0.95))            # 팔
    mid = (5.2, 2.55 + arch)
    seg(ax, (4.1, 2.55), mid, (6.3, 2.55))       # 척추
    head(ax, 6.85, 2.35 if arch >= 0 else 2.7, r=0.38)
    return (6.3, 2.55), (4.1, 2.55)


# ---------- 거북목 ----------

def ex001(ax):  # 친 턱 당기기
    floor(ax); sh, _ = stand_side(ax)
    seg(ax, sh, (5.1, 4.2), (5.25, 3.4))         # 팔
    head(ax, 4.95, 5.85)
    arrow(ax, (6.2, 5.85), (5.5, 5.85))          # 턱을 뒤로


def ex002(ax):  # 상부승모근 스트레칭
    floor(ax); sh, _ = stand_front(ax)
    head(ax, 5.45, 5.75)                         # 옆으로 기울인 머리
    seg(ax, sh, (5.9, 5.9), (5.5, 6.25))         # 손이 머리 위
    seg(ax, sh, (4.6, 4.3), (4.55, 3.5))         # 반대팔 아래
    arrow(ax, (4.7, 6.3), (5.15, 6.15), rad=-0.3)


def ex003(ax):  # 견갑거근 스트레칭
    floor(ax); sh, _ = stand_front(ax)
    head(ax, 5.4, 5.55)                          # 대각선 아래로 숙임
    seg(ax, sh, (5.95, 6.0), (5.55, 5.95))       # 손이 뒤통수
    seg(ax, sh, (4.6, 4.3), (4.55, 3.5))
    arrow(ax, (5.9, 5.2), (5.55, 4.9))


def ex004(ax):  # 흉쇄유돌근 스트레칭
    floor(ax); sh, _ = stand_front(ax)
    head(ax, 4.7, 6.05)                          # 대각선 위로 젖힘
    seg(ax, sh, (5.3, 4.9))                      # 손이 쇄골
    ax.add_patch(Circle((5.3, 4.9), 0.13, color=INK, zorder=4))
    arrow(ax, (4.35, 6.35), (3.95, 6.7))


def ex005(ax):  # 벽 친 턱 슬라이드
    floor(ax); wall(ax, 5.75)
    sh, _ = stand_side(ax, 5.35)
    seg(ax, sh, (5.35, 4.2))
    head(ax, 5.3, 5.85)
    arrow(ax, (4.4, 5.85), (5.0, 5.85))          # 뒤통수를 벽으로


def ex006(ax):  # 폼롤러 흉추 신전
    floor(ax); roller(ax, 5.7)
    seg(ax, (3.0, 0.95), (3.55, 2.1), (4.35, 1.45))          # 발-무릎-엉덩이
    seg(ax, (4.35, 1.45), (5.7, 1.95), (6.35, 2.35))         # 롤러 위 흉추 신전
    seg(ax, (6.35, 2.35), (6.9, 2.0))                        # 손이 뒤통수 쪽
    head(ax, 6.95, 2.7, r=0.38)
    arrow(ax, (6.5, 3.4), (7.1, 3.65), rad=-0.3)


def ex007(ax):  # 수건 경추 신전 보조
    floor(ax); sh, _ = stand_side(ax)
    seg(ax, (5.0, 5.5), (5.95, 4.75), color=PROP, lw=4)      # 수건
    seg(ax, sh, (5.6, 4.6), (5.95, 4.75))                    # 팔-손
    head(ax, 4.8, 5.95)                                      # 살짝 젖힌 머리
    arrow(ax, (4.6, 6.5), (4.1, 6.3), rad=-0.3)


def ex008(ax):  # 등척성 목 강화
    floor(ax); sh, _ = stand_front(ax)
    head(ax, 5.0, 5.85)
    seg(ax, sh, (4.15, 5.35), (4.5, 5.9))                    # 손바닥이 이마
    seg(ax, sh, (5.6, 4.3), (5.6, 3.5))
    arrow(ax, (3.9, 5.85), (4.35, 5.85))
    arrow(ax, (6.1, 5.85), (5.65, 5.85))


def ex009(ax):  # 엎드려 목 신전근 강화
    floor(ax)
    seg(ax, (2.6, 1.2), (4.7, 1.3), (6.4, 1.5))              # 다리-몸통
    seg(ax, (6.4, 1.5), (7.3, 1.35))                         # 팔은 몸 옆
    head(ax, 7.0, 2.05, r=0.38)                              # 살짝 든 머리
    arrow(ax, (7.35, 2.5), (7.35, 3.1))


def ex010(ax):  # 어깨 으쓱-이완
    floor(ax); sh, _ = stand_front(ax)
    head(ax, 5.0, 5.9)
    seg(ax, sh, (4.35, 4.3), (4.3, 3.5))
    seg(ax, sh, (5.65, 4.3), (5.7, 3.5))
    arrow(ax, (4.1, 5.0), (4.1, 5.6))
    arrow(ax, (5.9, 5.0), (5.9, 5.6))


# ---------- 라운드숄더 ----------

def ex011(ax):  # 도어웨이 가슴 스트레칭
    floor(ax); wall(ax, 3.55); wall(ax, 6.45)
    sh, _ = stand_front(ax)
    head(ax, 5.0, 5.85)
    seg(ax, sh, (4.1, 5.5), (3.65, 6.3))                     # ㄴ자 팔
    seg(ax, sh, (5.9, 5.5), (6.35, 6.3))
    arrow(ax, (5.0, 6.7), (5.0, 7.15))                       # 가슴 열기(전방) 상징


def ex012(ax):  # 소흉근 코너 스트레칭
    floor(ax); wall(ax, 3.55); wall(ax, 6.45)
    sh, _ = stand_front(ax)
    head(ax, 5.0, 5.85)
    seg(ax, sh, (3.7, 6.5))                                  # 대각선 팔
    seg(ax, sh, (6.3, 6.5))
    arrow(ax, (5.0, 6.7), (5.0, 7.15))


def ex013(ax):  # 밴드 풀어파트
    floor(ax); sh, _ = stand_front(ax)
    head(ax, 5.0, 5.9)
    seg(ax, (3.3, 5.15), (5.0, 4.75), (6.7, 5.15), color=PROP, lw=3, ls=(0, (4, 3)))  # 밴드(처짐)
    seg(ax, sh, (3.3, 5.15))
    seg(ax, sh, (6.7, 5.15))
    arrow(ax, (3.2, 5.15), (2.5, 5.15))
    arrow(ax, (6.8, 5.15), (7.5, 5.15))


def ex014(ax):  # 밴드 로우
    floor(ax); wall(ax, 2.5)
    sh, _ = stand_side(ax, 5.4)
    head(ax, 5.35, 5.85)
    seg(ax, (2.5, 4.55), (4.75, 4.45), color=PROP, lw=3, ls=(0, (4, 3)))  # 밴드
    seg(ax, sh, (5.9, 4.6), (4.75, 4.45))                    # 당긴 팔
    arrow(ax, (6.1, 4.85), (6.8, 4.95))                      # 팔꿈치 뒤로


def ex015(ax):  # 월 슬라이드
    floor(ax); wall(ax, 5.75)
    sh, _ = stand_side(ax, 5.35)
    head(ax, 5.3, 5.85)
    seg(ax, sh, (5.6, 5.9), (5.5, 6.75))                     # 벽 따라 올린 팔
    arrow(ax, (6.3, 5.6), (6.3, 6.6))


def ex016(ax):  # 프론 Y-T-W
    floor(ax)
    seg(ax, (2.4, 1.2), (4.5, 1.3), (6.1, 1.5))              # 몸통
    seg(ax, (6.1, 1.5), (7.35, 2.3))                         # Y 팔
    seg(ax, (6.1, 1.5), (7.5, 1.85))
    head(ax, 6.75, 1.85, r=0.38)
    arrow(ax, (7.5, 2.55), (7.8, 2.9))


def ex017(ax):  # 폼롤러 가슴 열기
    floor(ax); roller(ax, 5.0)
    seg(ax, (3.0, 0.95), (3.4, 2.15), (3.95, 1.75))          # 발-무릎-엉덩이
    seg(ax, (3.95, 1.75), (6.05, 1.95))                      # 롤러 위 몸통
    head(ax, 6.6, 2.1, r=0.38)
    seg(ax, (5.9, 1.95), (6.35, 1.05))                       # 벌려 떨어뜨린 팔
    seg(ax, (5.75, 1.95), (5.35, 1.05))
    arrow(ax, (6.6, 1.5), (7.15, 1.2))


def ex018(ax):  # 견갑 후인·하강
    floor(ax); sh, _ = stand_side(ax)
    head(ax, 4.95, 5.85)
    seg(ax, sh, (5.1, 4.2), (5.2, 3.4))
    arrow(ax, (6.15, 5.05), (5.6, 4.95))                     # 뒤로
    arrow(ax, (5.55, 4.75), (5.55, 4.2))                     # 아래로


def ex019(ax):  # 밴드 외회전
    floor(ax); sh, _ = stand_front(ax)
    head(ax, 5.0, 5.9)
    seg(ax, sh, (5.55, 4.35), (6.5, 4.5))                    # 팔꿈치 90도
    seg(ax, (3.6, 4.5), (6.5, 4.5), color=PROP, lw=3, ls=(0, (4, 3)))
    seg(ax, sh, (4.45, 4.35), (4.4, 3.55))
    arrow(ax, (6.7, 4.6), (7.4, 4.85), rad=-0.25)


def ex020(ax):  # 캣카우
    floor(ax)
    quadruped(ax, arch=0.75)
    arrow(ax, (5.2, 3.75), (5.2, 4.35))
    arrow(ax, (5.2, 2.2), (5.2, 1.65))


# ---------- 척추측만 ----------

def ex021(ax):  # 사이드 플랭크
    floor(ax)
    seg(ax, (2.8, 1.15), (4.7, 1.9), (6.0, 2.45))            # 일직선 몸
    seg(ax, (6.0, 2.45), (6.1, 1.0), (7.0, 1.0))             # 팔꿈치 지지
    head(ax, 6.55, 2.75, r=0.38)
    arrow(ax, (4.6, 2.4), (4.6, 3.0))


def ex022(ax):  # 버드독
    floor(ax)
    seg(ax, (4.35, 0.95), (4.35, 2.55))                      # 지지 무릎
    seg(ax, (6.2, 2.55), (6.2, 0.95))                        # 지지 팔
    seg(ax, (4.35, 2.55), (6.2, 2.55))                       # 척추
    seg(ax, (6.2, 2.55), (7.55, 2.75))                       # 뻗은 팔
    seg(ax, (4.35, 2.55), (2.85, 2.6))                       # 뻗은 다리
    head(ax, 6.75, 2.4, r=0.38)
    arrow(ax, (7.65, 2.85), (8.25, 2.95))
    arrow(ax, (2.75, 2.65), (2.15, 2.7))


def ex023(ax):  # 데드버그
    floor(ax)
    seg(ax, (4.4, 1.3), (6.15, 1.4))                         # 바닥의 등
    head(ax, 6.75, 1.5, r=0.38)
    seg(ax, (4.4, 1.3), (4.15, 2.6), (3.55, 2.85))           # 든 다리(굽힘)
    seg(ax, (4.4, 1.3), (3.05, 2.0))                         # 뻗은 다리
    seg(ax, (6.15, 1.4), (6.15, 2.9))                        # 든 팔
    seg(ax, (6.15, 1.4), (7.45, 2.05))                       # 뻗은 팔
    arrow(ax, (7.55, 2.15), (8.05, 2.4))
    arrow(ax, (2.95, 1.95), (2.45, 1.7))


def ex024(ax):  # 차일드 포즈 측면
    floor(ax)
    seg(ax, (4.1, 0.95), (4.35, 1.95), (5.6, 1.6))           # 무릎-엉덩이-어깨
    seg(ax, (5.6, 1.6), (7.25, 1.2))                         # 뻗은 팔
    seg(ax, (5.6, 1.6), (7.15, 1.5))
    head(ax, 6.05, 1.95, r=0.38)
    arrow(ax, (7.4, 1.25), (8.0, 1.25))


def ex025(ax):  # 오픈북 흉추 회전
    floor(ax)
    seg(ax, (3.3, 1.4), (4.35, 1.4), (5.5, 1.35))            # 옆으로 누운 몸
    seg(ax, (5.5, 1.35), (6.3, 1.85), (7.05, 1.5))           # 굽힌 무릎
    head(ax, 2.85, 1.5, r=0.38)
    seg(ax, (4.35, 1.4), (3.4, 1.15))                        # 바닥 팔
    seg(ax, (4.35, 1.4), (4.5, 2.9))                         # 여는 팔
    arrow(ax, (4.45, 3.15), (3.7, 3.0), rad=-0.4)


def ex026(ax):  # 요방형근 스트레칭
    floor(ax)
    seg(ax, (5.0, 3.2), (4.55, 2.0), (4.45, 0.95))
    seg(ax, (5.0, 3.2), (5.45, 2.0), (5.55, 0.95))
    seg(ax, (5.0, 3.2), (5.55, 5.05))                        # 옆으로 기운 몸통
    head(ax, 5.85, 5.55, r=0.4)
    seg(ax, (5.55, 5.05), (6.65, 6.15))                      # 넘긴 팔
    seg(ax, (5.55, 5.05), (5.2, 4.0))
    arrow(ax, (6.35, 6.6), (7.0, 6.25), rad=-0.3)


def ex027(ax):  # 플랭크
    floor(ax)
    seg(ax, (2.7, 1.25), (4.7, 1.6), (6.25, 1.95))           # 일직선 몸
    seg(ax, (6.25, 1.95), (6.35, 1.0), (7.2, 1.0))           # 전완 지지
    head(ax, 6.85, 2.15, r=0.38)


def ex028(ax):  # 광배근 스트레칭
    floor(ax); wall(ax, 7.1)
    seg(ax, (3.85, 0.95), (3.95, 2.1), (4.0, 3.4))           # 다리
    seg(ax, (4.15, 0.95), (4.2, 2.1), (4.0, 3.4))
    seg(ax, (4.0, 3.4), (5.6, 3.95))                         # 숙인 몸통
    seg(ax, (5.6, 3.95), (7.0, 4.35))                        # 뻗은 팔
    head(ax, 5.85, 3.5, r=0.38)
    arrow(ax, (5.0, 4.6), (4.4, 4.4))


def ex029(ax):  # 골반 경사
    floor(ax)
    head(ax, 3.0, 1.45, r=0.38)
    seg(ax, (3.55, 1.35), (5.45, 1.3))                       # 등
    seg(ax, (5.45, 1.3), (6.2, 2.35), (6.6, 0.95))           # 세운 무릎
    seg(ax, (3.9, 1.3), (4.6, 1.1))                          # 팔은 옆
    arrow(ax, (5.45, 1.75), (5.05, 2.05), rad=-0.4)


def ex030(ax):  # 벽 천사
    floor(ax); wall(ax, 5.75)
    sh, _ = stand_side(ax, 5.35)
    head(ax, 5.3, 5.85)
    seg(ax, sh, (5.6, 5.85), (5.5, 6.7))                     # 올라간 팔
    seg(ax, sh, (5.65, 4.75), (5.55, 4.0), color=PROP, lw=4)  # 내려간 팔(이전 위치)
    arrow(ax, (6.35, 4.6), (6.35, 6.4), rad=-0.25)


DRAWERS = {
    "EX-001": ex001, "EX-002": ex002, "EX-003": ex003, "EX-004": ex004,
    "EX-005": ex005, "EX-006": ex006, "EX-007": ex007, "EX-008": ex008,
    "EX-009": ex009, "EX-010": ex010, "EX-011": ex011, "EX-012": ex012,
    "EX-013": ex013, "EX-014": ex014, "EX-015": ex015, "EX-016": ex016,
    "EX-017": ex017, "EX-018": ex018, "EX-019": ex019, "EX-020": ex020,
    "EX-021": ex021, "EX-022": ex022, "EX-023": ex023, "EX-024": ex024,
    "EX-025": ex025, "EX-026": ex026, "EX-027": ex027, "EX-028": ex028,
    "EX-029": ex029, "EX-030": ex030,
}


def main():
    for ex_id, draw in DRAWERS.items():
        fig, ax = new_fig()
        draw(ax)
        fig.savefig(OUT / f"{ex_id}.png", facecolor=BG)
        plt.close(fig)
    print(f"{len(DRAWERS)}장 생성 완료 → {OUT}")


if __name__ == "__main__":
    main()

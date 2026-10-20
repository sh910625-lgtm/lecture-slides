"""manim 장면 공통 스타일 (슬라이드 템플릿과 같은 색).

scenes.py 맨 위에서:

    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / ".claude/skills/lecture-slides/scripts"))
    from manim_style import *

규칙: LaTeX가 없으므로 MathTex / Tex / DecimalNumber / add_coordinates 금지. 글자는 모두 T().
"""
from manim import *  # noqa: F401,F403
import numpy as np  # noqa: F401

BG = "#222A35"
CARD = "#2C3746"
A1, A2, A3, A4, A5 = "#1F608B", "#2980B9", "#4098D4", "#7BB8E1", "#9FCBE9"
MUTED = "#B4C0CE"
GRID = "#3A4758"
FONT = "Pretendard"

config.background_color = BG


def T(s, size=36, color=WHITE, bold=False):
    """한글 텍스트 (Pretendard)."""
    return Text(s, font=FONT, font_size=size, color=color, weight=BOLD if bold else NORMAL)


def plain_axes(x_range, y_range, x_length, y_length, **kw):
    """눈금·화살표 없는 축. 막대그래프는 x_range=[0, n+0.6]로 두고 범주를 1..n에 놓아야
    y축이 첫 막대를 관통하지 않는다."""
    return Axes(x_range=x_range, y_range=y_range, x_length=x_length, y_length=y_length,
                axis_config={"color": MUTED, "stroke_width": 2, "include_ticks": False}, tips=False, **kw)


def bar(ax, x0, x1, h, color, opacity=1.0, stroke=0):
    """축 좌표 (x0..x1, 0..h)를 채우는 막대."""
    bl, tr = ax.c2p(x0, 0), ax.c2p(x1, h)
    r = Rectangle(width=max(tr[0] - bl[0], 1e-3), height=max(tr[1] - bl[1], 1e-3),
                  fill_color=color, fill_opacity=opacity, stroke_color=BG, stroke_width=stroke)
    r.move_to([(bl[0] + tr[0]) / 2, (bl[1] + tr[1]) / 2, 0])
    return r


def bar_chart(ax, probs, labels, colors=(A2, A3, A4), width=0.64, size=32):
    """범주 0..n-1을 축 위치 1..n에 그린 막대 + 위 라벨. (bars, tags) 반환."""
    bars, tags = VGroup(), VGroup()
    for i, (p, s) in enumerate(zip(probs, labels)):
        b = bar(ax, i + 1 - width / 2, i + 1 + width / 2, p, colors[i % len(colors)])
        bars.add(b)
        tags.add(T(s, size, WHITE, True).next_to(b, UP, buff=0.12))
    return bars, tags


def x_labels(ax, names, size=28):
    return VGroup(*[T(str(n), size, MUTED).next_to(ax.c2p(i + 1, 0), DOWN, buff=0.2) for i, n in enumerate(names)])

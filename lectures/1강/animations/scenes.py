"""1강 확률변수와 확률분포 - manim 애니메이션

렌더링 (프로젝트 루트에서):
    C:/Users/KDP/.venvs/manim/Scripts/python.exe .claude/skills/lecture-slides/scripts/render_anims.py lectures/1강/animations/scenes.py

LaTeX 없이 Text(Pretendard)만 사용한다.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / ".claude/skills/lecture-slides/scripts"))
from manim_style import *  # noqa: E402,F403


class RandomVariableMap(Scene):
    """근원사건 -> 실수 대응 (확률변수)"""

    def construct(self):
        evs = ["HH", "HT", "TH", "TT"]
        vals = {"HH": 2, "HT": 1, "TH": 1, "TT": 0}
        boxes = VGroup()
        for e in evs:
            r = RoundedRectangle(corner_radius=0.12, width=2.4, height=0.95, fill_color=A1,
                                 fill_opacity=1, stroke_width=0)
            boxes.add(VGroup(r, T(e, 42, bold=True).move_to(r)))
        boxes.arrange(DOWN, buff=0.35).move_to(LEFT * 3.6 + DOWN * 0.75)

        circles = {}
        for v in (2, 1, 0):
            c = Circle(radius=0.55, fill_color=A3, fill_opacity=1, stroke_width=0)
            circles[v] = VGroup(c, T(str(v), 46, bold=True).move_to(c))
        col = VGroup(*circles.values()).arrange(DOWN, buff=0.85).move_to(RIGHT * 3.6 + DOWN * 0.75)

        h1 = T("표본공간 S", 32, MUTED).next_to(boxes, UP, buff=0.45)
        h2 = T("X의 값", 32, MUTED).move_to([col.get_x(), h1.get_y(), 0])
        title = T("X = 앞면이 나온 횟수", 44, A4, True).to_edge(UP, buff=0.45)

        self.play(FadeIn(title, shift=DOWN * 0.2))
        self.play(LaggedStart(*[FadeIn(b, shift=RIGHT * 0.3) for b in boxes], lag_ratio=0.15), FadeIn(h1))
        self.play(LaggedStart(*[GrowFromCenter(c) for c in circles.values()], lag_ratio=0.15), FadeIn(h2))
        for b, e in zip(boxes, evs):
            c = circles[vals[e]]
            arr = Arrow(b.get_right(), c.get_left(), buff=0.15, color=A4, stroke_width=5,
                        max_tip_length_to_length_ratio=0.06)
            self.play(GrowArrow(arr), b[0].animate.set_fill(A2), run_time=0.7)
            self.play(Indicate(c, color=A4, scale_factor=1.15), run_time=0.5)
        self.wait(2)


class CoinDistribution(Scene):
    """막대그래프가 자라고, 쌓으면 합이 1"""

    def construct(self):
        title = T("동전 두 번 던지기 · X의 확률분포", 40, WHITE).to_edge(UP, buff=0.45)
        ax = Axes(x_range=[0, 3.6, 1], y_range=[0, 1.1, 0.25], x_length=6.4, y_length=5.2,
                  axis_config={"color": MUTED, "stroke_width": 2, "include_ticks": False},
                  tips=False).move_to(LEFT * 2.0 + DOWN * 0.45)
        xl = VGroup(*[T(str(x), 30, MUTED).next_to(ax.c2p(x + 1, 0), DOWN, buff=0.2) for x in range(3)])
        yl = VGroup(*[T(s, 24, MUTED).next_to(ax.c2p(0, y), LEFT, buff=0.15)
                      for y, s in [(0.25, "0.25"), (0.5, "0.5"), (0.75, "0.75"), (1, "1")]])
        grid = VGroup(*[DashedLine(ax.c2p(0, y), ax.c2p(3.6, y), color="#3A4758", stroke_width=1.5)
                        for y in (0.25, 0.5, 0.75)])
        self.play(FadeIn(title), Create(ax), FadeIn(xl), FadeIn(yl), FadeIn(grid))

        ps, labels, colors = [0.25, 0.5, 0.25], ["1/4", "1/2", "1/4"], [A2, A3, A4]
        bars, tags = VGroup(), VGroup()
        for x, (p, s, c) in enumerate(zip(ps, labels, colors)):
            b = bar(ax, x + 0.68, x + 1.32, p, c)
            bars.add(b)
            tags.add(T(s, 34, WHITE, True).next_to(b, UP, buff=0.15))
        for b, t in zip(bars, tags):
            self.play(GrowFromEdge(b, DOWN), FadeIn(t, shift=UP * 0.2), run_time=0.8)
        self.wait(0.8)

        # 쌓아서 합이 1임을 보여 주기
        one = DashedLine(ax.c2p(0, 1), ax.c2p(0, 1) + RIGHT * 9.4, color=A5, stroke_width=3)
        self.play(Create(one), run_time=0.8)
        base = np.array([4.6, ax.c2p(0, 0)[1], 0])
        stack, y = VGroup(), base[1]
        for b, c in zip(bars, colors):
            nb = b.copy()
            nb.generate_target()
            nb.target.move_to([base[0], y + b.height / 2, 0])
            y += b.height
            stack.add(nb)
        self.play(LaggedStart(*[MoveToTarget(nb) for nb in stack], lag_ratio=0.35), run_time=2.2)
        total = T("합 = 1", 40, A5, True).next_to(stack, LEFT, buff=0.35)
        self.play(Write(total), Indicate(stack, color=A5, scale_factor=1.04))
        self.wait(2)


class BallDraw(Scene):
    """흰 공 3, 검은 공 2에서 2개 꺼내기 -> 확률분포"""

    def construct(self):
        title = T("흰 공 3개, 검은 공 2개에서 2개 꺼내기", 38).to_edge(UP, buff=0.45)
        bag = RoundedRectangle(corner_radius=0.5, width=3.4, height=3.2, fill_color=CARD, fill_opacity=1,
                               stroke_color=A3, stroke_width=4).move_to(LEFT * 4.7 + DOWN * 0.5)
        neck = Line(bag.get_corner(UL) + RIGHT * 0.5, bag.get_corner(UR) + LEFT * 0.5, color=BG, stroke_width=10)

        def ball(white):
            return Circle(radius=0.32, fill_color=WHITE if white else "#0E1620", fill_opacity=1,
                          stroke_color=MUTED, stroke_width=3)

        spots = [(-0.9, 0.5), (0, 0.6), (0.9, 0.5), (-0.45, -0.5), (0.45, -0.5)]
        balls = [ball(i < 3) for i in range(5)]
        for b, (dx, dy) in zip(balls, spots):
            b.move_to(bag.get_center() + RIGHT * dx + UP * dy)
        bag_label = T("주머니", 28, MUTED).next_to(bag, DOWN, buff=0.25)
        self.play(FadeIn(title), FadeIn(bag), FadeIn(neck), FadeIn(bag_label),
                  LaggedStart(*[GrowFromCenter(b) for b in balls], lag_ratio=0.1))

        out_pos = [LEFT * 1.6 + UP * 0.3, LEFT * 0.6 + UP * 0.3]
        trials = [(0, 3), (1, 2), (3, 4)]   # 흰+검 / 흰+흰 / 검+검
        for a, b in trials:
            pa, pb = balls[a].get_center(), balls[b].get_center()
            x = sum(1 for i in (a, b) if i < 3)
            res = T(f"X = {x}", 40, A4, True).move_to(LEFT * 1.1 + DOWN * 1.0)
            self.play(balls[a].animate.move_to(out_pos[0]), balls[b].animate.move_to(out_pos[1]), run_time=0.8)
            self.play(FadeIn(res, scale=1.2), run_time=0.4)
            self.wait(0.5)
            self.play(balls[a].animate.move_to(pa), balls[b].animate.move_to(pb), FadeOut(res), run_time=0.6)

        ax = Axes(x_range=[0, 3.6, 1], y_range=[0, 0.7, 0.1], x_length=4.6, y_length=4.2,
                  axis_config={"color": MUTED, "stroke_width": 2, "include_ticks": False},
                  tips=False).move_to(RIGHT * 3.9 + DOWN * 0.5)
        xl = VGroup(*[T(str(x), 28, MUTED).next_to(ax.c2p(x + 1, 0), DOWN, buff=0.2) for x in range(3)])
        xname = T("흰 공의 개수 X", 26, MUTED).next_to(xl, DOWN, buff=0.2)
        self.play(Create(ax), FadeIn(xl), FadeIn(xname))
        ps, labels, colors = [0.1, 0.6, 0.3], ["1/10", "6/10", "3/10"], [A2, A3, A4]
        bars = VGroup(*[bar(ax, x + 0.7, x + 1.3, p, c) for x, (p, c) in enumerate(zip(ps, colors))])
        tags = VGroup(*[T(s, 30, WHITE, True).next_to(b, UP, buff=0.12) for b, s in zip(bars, labels)])
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.3),
                  LaggedStart(*[FadeIn(t) for t in tags], lag_ratio=0.3), run_time=1.8)
        box = SurroundingRectangle(VGroup(bars[1], bars[2], tags[1], tags[2]), color=A5, buff=0.12,
                                   corner_radius=0.1)
        ge = T("P(X ≥ 1) = 9/10", 34, A5, True).next_to(box, UP, buff=0.2)
        self.play(Create(box), Write(ge))
        self.wait(2)


class DiscreteToContinuous(Scene):
    """막대를 잘게 쪼개면 곡선(확률밀도함수)이 된다"""

    def construct(self):
        title = T("막대를 잘게 쪼개면?", 42, WHITE).to_edge(UP, buff=0.45)
        ax = Axes(x_range=[0, 10, 1], y_range=[0, 0.28, 0.1], x_length=10.5, y_length=5,
                  axis_config={"color": MUTED, "stroke_width": 2, "include_ticks": False},
                  tips=False).move_to(DOWN * 0.5)
        f = lambda x: np.exp(-((x - 5) ** 2) / (2 * 1.6 ** 2)) / (1.6 * np.sqrt(2 * np.pi))

        def hist(n):
            w = 10 / n
            g = VGroup()
            for i in range(n):
                x0 = i * w
                g.add(bar(ax, x0, x0 + w, f(x0 + w / 2), A3, 1, stroke=2 if n < 40 else 1))
            return g

        counts = [5, 10, 20, 50]
        bars = hist(counts[0])
        label = T(f"막대 {counts[0]}개", 34, A4, True).to_corner(UR, buff=0.6).shift(DOWN * 0.9)
        self.play(FadeIn(title), Create(ax))
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.1), FadeIn(label))
        self.wait(0.6)
        for n in counts[1:]:
            nl = T(f"막대 {n}개", 34, A4, True).move_to(label)
            self.play(Transform(bars, hist(n)), FadeTransform(label, nl), run_time=1.3)
            label = nl
            self.wait(0.4)
        curve = ax.plot(f, x_range=[0, 10], color=A5, stroke_width=6)
        self.play(Create(curve), bars.animate.set_fill(opacity=0.45), run_time=1.6)
        nl = T("곡선 = 확률밀도함수", 34, A5, True).move_to(label).align_to(label, RIGHT)
        note = T("확률 = 곡선 아래의 넓이", 32, WHITE).next_to(nl, DOWN, buff=0.25).align_to(nl, RIGHT)
        self.play(FadeTransform(label, nl), FadeIn(note, shift=UP * 0.2))
        self.wait(2)


class UniformArea(Scene):
    """지하철 대기 시간: 넓이가 곧 확률"""

    def construct(self):
        title = T("10분 간격 지하철 · 기다리는 시간 X", 38).to_edge(UP, buff=0.45)
        ax = Axes(x_range=[0, 11, 1], y_range=[0, 0.16, 0.05], x_length=10.5, y_length=4.2,
                  axis_config={"color": MUTED, "stroke_width": 2, "include_ticks": False},
                  tips=False).move_to(DOWN * 0.8 + LEFT * 0.3)
        top = Line(ax.c2p(0, 0.1), ax.c2p(10, 0.1), color=A5, stroke_width=6)
        side = DashedLine(ax.c2p(10, 0.1), ax.c2p(10, 0), color=A5, stroke_width=2)
        ylab = T("1/10", 26, MUTED).next_to(ax.c2p(0, 0.1), LEFT, buff=0.15)
        fx = T("y = f(x)", 28, A5).next_to(ax.c2p(7.5, 0.1), UP, buff=0.15)
        xl = VGroup(*[T(str(v), 26, MUTED).next_to(ax.c2p(v, 0), DOWN, buff=0.18) for v in (0, 3, 10)])
        xname = T("x (분)", 24, MUTED).next_to(ax.c2p(11, 0), DOWN, buff=0.18)
        self.play(FadeIn(title), Create(ax), FadeIn(xl), FadeIn(xname))
        self.play(Create(top), Create(side), FadeIn(ylab), FadeIn(fx))

        b = ValueTracker(0.001)
        area = always_redraw(lambda: bar(ax, 0, b.get_value(), 0.1, A3, 0.85))
        edge = always_redraw(lambda: Line(ax.c2p(b.get_value(), 0), ax.c2p(b.get_value(), 0.1),
                                          color=WHITE, stroke_width=3))

        def readout():
            v = b.get_value()
            return T(f"P(0 ≤ X ≤ {v:.1f}) = {v / 10:.2f}", 38, WHITE, True).move_to(UP * 2.2)

        txt = always_redraw(readout)
        self.add(area, edge, txt)
        self.bring_to_front(top)
        self.play(b.animate.set_value(10), run_time=3.5, rate_func=linear)
        whole = T("전체 넓이 = 1", 34, A5, True).next_to(txt, DOWN, buff=0.25)
        self.play(FadeIn(whole, shift=UP * 0.2))
        self.wait(0.8)
        self.play(FadeOut(whole), b.animate.set_value(3), run_time=2, rate_func=smooth)
        txt.clear_updaters()
        area.clear_updaters()
        edge.clear_updaters()
        final = T("P(0 ≤ X ≤ 3) = 3/10", 42, A4, True).move_to(txt)
        lab = T("3/10", 36, WHITE, True).move_to(area)
        self.play(FadeTransform(txt, final), FadeIn(lab, scale=1.2))
        self.wait(2)

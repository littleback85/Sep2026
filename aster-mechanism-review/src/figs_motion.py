import math, sys
from svglib import *

OUT = sys.argv[1]


# ------------------------------------------------------------------ Fig 1
def fig1():
    s = SVG(960, 730, "图1 草稿的光致运动机理")
    s.text(20, 30, "图1  草稿提出的光致运动机理：自扩散泳（扩散电势）＋“光流体”", 18, bold=True)

    chain = [
        ["光照", "UV 365 nm /", "Vis 450 nm"],
        ["偶氮苯", "顺反异构"],
        ["延伸丝溶解(UV)", "/ 再组装(Vis)"],
        ["释放 / 消耗", "Co²⁺ 与 C4AZO⁻"],
        ["扩散系数差", "→ 自生电场 E"],
        ["负 ζ 星状体", "电泳 → 速度 U"],
        ["水成为“光流体”", "拖动远处被动群落、", "液柱与货物"],
    ]
    bw, gap, x = 124, 10, 16
    for i, c in enumerate(chain):
        s.box(x, 48, bw, 68, c, fill="#f5f3ff" if i < 6 else "#eff6ff", stroke="#a78bfa" if i < 6 else "#60a5fa", size=12)
        if i < len(chain) - 1:
            s.arrow(x + bw + 1, 82, x + bw + gap - 1, 82, "k", 1.6)
        x += bw + gap

    # ---- panel a : UV
    s.rect(16, 136, 456, 330, fill="none", stroke=UV, sw=1.5, dash="6 4")
    s.text(28, 158, "(a) UV：延伸丝溶解、释放离子 →“正趋光”（草稿图4c）", 14, bold=True)
    s.lamp_h(78, 290, UV)
    s.poly([(83, 280), (205, 238), (205, 342), (83, 300)], UV, opacity=0.18)
    s.text(40, 190, "浓盐（近光侧）", 13, color=MUTED)
    s.text(352, 190, "稀盐（远光侧）", 13, color=MUTED)
    s.circle(275, 290, 36, stroke="#16a34a", dash="3 3", sw=1)
    s.aster(275, 290, 0.62)
    s.text(275, 244, "收缩中的星状体", 11, "middle", color=MUTED)
    for (xx, yy, r) in [(120, 230, 10), (150, 262, -20), (175, 318, 30), (205, 250, 0), (228, 330, 15), (140, 330, -5), (190, 212, 25), (320, 250, 10)]:
        s.azo(xx, yy, r)
    for (xx, yy) in [(132, 250), (165, 296), (213, 286), (160, 225), (340, 318), (380, 262), (420, 300), (400, 232), (250, 350)]:
        s.co(xx, yy)
    s.arrow(215, 388, 345, 388, "k", 2.6)
    s.text(215, 380, "E（草稿图4c：由浓侧指向稀侧）", 12)
    s.arrow(345, 420, 115, 420, "b", 3)
    s.text(355, 424, "U：朝向光源", 12, color=BLUE)
    s.text(28, 454, "⚠ 同一草稿图4a 插图中 E 箭头指向光源（←），与图4c 方向相反", 12, color=RED)

    # ---- panel b : Vis
    s.rect(488, 136, 456, 330, fill="none", stroke=VIS, sw=1.5, dash="6 4")
    s.text(500, 158, "(b) Vis：延伸丝生长、消耗离子 →“负趋光”（草稿图4d）", 14, bold=True)
    s.lamp_h(552, 290, VIS)
    s.poly([(557, 280), (660, 240), (660, 340), (557, 300)], VIS, opacity=0.2)
    s.text(512, 190, "稀盐（近光，被消耗）", 13, color=MUTED)
    s.text(836, 190, "浓盐（远光侧）", 13, color=MUTED)
    s.aster(725, 290, 1.05)
    s.text(725, 222, "生长中的星状体", 11, "middle", color=MUTED)
    for (xx, yy, r) in [(835, 240, 10), (870, 280, -20), (900, 322, 30), (840, 330, 0), (905, 236, 15), (618, 240, 20)]:
        s.azo(xx, yy, r)
    for (xx, yy) in [(852, 262), (885, 300), (918, 262), (860, 350), (824, 300), (640, 330)]:
        s.co(xx, yy)
    s.arrow(860, 388, 720, 388, "k", 2.6)
    s.text(610, 380, "E：指向光源（稀侧）", 12)
    s.arrow(620, 420, 900, 420, "b", 3)
    s.text(500, 424, "U：背离光源", 12, color=BLUE)

    # ---- panel c : photofluid
    s.text(20, 498, "(c) “光流体”：少数被照亮的主动星状体带动多数被动星状体（草稿图3f,g、图4a,b 与正文）", 14, bold=True)
    s.rect(16, 512, 928, 128, fill=WATER, stroke="#93c5fd", rx=10)
    s.lamp_h(70, 576, UV)
    s.poly([(75, 566), (175, 536), (175, 616), (75, 586)], UV, opacity=0.2)
    s.circle(205, 576, 44, fill="url(#glow)", stroke="none")
    s.aster(205, 576, 0.72)
    s.text(205, 630, "主动（被照亮）", 11, "middle", color=UV)
    for i, xx in enumerate([340, 470, 600, 730, 860]):
        yy = 552 if i % 2 == 0 else 600
        s.aster(xx, yy, 0.55, opacity=0.5)
        s.path(f"M{xx-34},{yy} Q{xx-66},{(yy+576)/2 + (-14 if i % 2 == 0 else 14)} {xx-96},{576}", stroke=BLUE, sw=2, m="b", opacity=0.8)
    s.text(860, 634, "被动（未照亮）多数", 11, "middle", color=MUTED)
    s.lines(20, 662, [
        "草稿论述：主动个体“诱导水运动”，远处被动群落“服从少数”；显微运动被“放大数个数量级”成宏观流动（液柱 3.8 cm / 34 s）并可输运货物。",
        "草稿给出的佐证：0.5 M KNO₃/NaCl 高盐使运动完全消失；吖啶黄（AFV）荧光在星状体周围形成暗区，被视为“扩散电势”的证据。",
    ], 12)

    # legend
    s.co(30, 716)
    s.text(40, 720, "Co²⁺（草稿：扩散快）", 12)
    s.azo(200, 717)
    s.text(215, 720, "顺式 C4AZO⁻（草稿：扩散慢）", 12)
    s.arrow(420, 716, 460, 716, "k", 2.2)
    s.text(466, 720, "电场 E", 12)
    s.arrow(540, 716, 580, 716, "b", 2.6)
    s.text(586, 720, "星状体速度 U（ζ<0）", 12)
    s.save(f"{OUT}/fig1_motion_draft.svg")


# ------------------------------------------------------------------ Fig 2
def fig2():
    s = SVG(960, 622, "图2 扩散泳方向核对")
    s.text(20, 30, "图2  按草稿自身假设（D(Co²⁺) > D(C4AZO⁻)、星状体 ζ < 0）重新核对扩散泳方向", 18, bold=True)

    # axes
    ox, oy = 80, 290
    s.rect(ox - 26, 66, 16, oy - 66, fill=UV, stroke="none", rx=2, opacity=0.35)
    s.text(ox - 18, 60, "UV 光斑", 12, "middle", color=UV)
    s.arrow(ox, oy, 520, oy, "k", 1.4)
    s.arrow(ox, oy, ox, 70, "k", 1.4)
    s.text(520, oy + 20, "离光斑距离 x", 12, "end")
    s.text(ox + 8, 80, "c", 14, italic=True)
    pts = []
    for i in range(0, 101):
        x = ox + i * 4.3
        y = oy - 190 * math.exp(-(x - ox) / 120) - 10
        pts.append(f"{x:.1f},{y:.1f}")
    s.path("M" + " L".join(pts), stroke=CO, sw=2.5)
    s.text(150, 120, "离子浓度 c(x)：近光侧高", 12, color="#be185d")
    # charge separation
    s.text(128, 262, "− − − −", 18, "middle", bold=True, color="#475569")
    s.text(128, 280, "慢的 C4AZO⁻ 滞后", 11, "middle", color=MUTED)
    s.text(380, 262, "+ + + +", 18, "middle", bold=True, color="#be185d")
    s.text(380, 280, "快的 Co²⁺ 领先", 11, "middle", color=MUTED)
    s.arrow(372, 318, 138, 318, "k", 2.8)
    s.text(255, 340, "E 由 + 指向 −：指向高浓度＝指向光源", 12, "middle", bold=True)

    # aster and velocity components (1 mV = 20 px)
    ax, ay = 300, 440
    s.aster(ax, ay, 0.62)
    s.text(ax + 30, ay + 34, "ζ ≈ −40 mV", 11, color=MUTED)
    s.arrow(ax + 25, ay - 16, ax + 25 + 120, ay - 16, "r", 3)
    s.text(ax + 20, ay - 28, "电泳分量 ∝ β′ζ ≈ −6 mV：背离光源", 12, color=RED)
    s.arrow(ax - 25, ay + 12, ax - 25 - 152, ay + 12, "g", 3)
    s.text(ax - 180, ay + 32, "化学泳分量 ≈ +7.6 mV：朝高浓度", 12, color=GREEN)
    s.arrow(ax, ay + 62, ax - 32, ay + 62, "b", 3.2)
    s.text(ax + 12, ay + 66, "净值 ≈ +1.6 mV（两项几乎抵消）", 12, color=BLUE, bold=True)
    s.text(40, 395, "箭头长度 ∝ 各项贡献（1 mV ≈ 20 px）", 11, color=MUTED)

    # formula panel
    s.rect(580, 58, 364, 452, fill="#f8fafc", stroke="#cbd5e1", rx=10)
    s.lines(596, 86, [
        "零电流条件 ⇒ 扩散电场",
        "  E = (kT/e) · β′ · ∇ln c",
        "  β′ = (D₊ − D₋)/(z₊D₊ + |z₋|D₋)",
        "",
        "D(Co²⁺) ≈ 0.73×10⁻⁹ m²/s",
        "D(C4AZO⁻) ≈ 0.45×10⁻⁹ m²/s（Stokes 估算）",
        "⇒ β′ ≈ +0.15 > 0 ⇒ E 指向高浓度（光源）",
        "",
        "扩散泳速度（Prieve–Anderson，z:z 近似）",
        "  U = (ε/η)(kT/e)[β′ζ − (2kT/e)ln(1−γ²)]∇ln c",
        "  γ = tanh(eζ/4kT)",
        "",
        "第一项（电泳）：β′ζ < 0 → 负电粒子背离光源",
        "第二项（化学泳）：恒 > 0 → 朝高浓度",
        "",
        "量级：净 ≈ 1.6 mV，∇ln c ≈ 1/(10–100 μm)",
        "  ⇒ |U| ≈ 0.1–1 μm/s，符号取决于实测 ζ、β′",
        "注：若 ζ 因吸附 Co²⁺ 而反号，结论再次改变；",
        "若顺式以胶束/寡聚体形式释放，β′ 也会改变。",
    ], 12.5, lh=22)

    # verdict boxes
    s.box(16, 530, 456, 76, [
        "草稿：把 E 画成指向稀侧，且只计电泳项，",
        "得出“负电星状体在 E 作用下朝 UV 运动”",
        "——与其自身假设 D(Co²⁺) > D(C4AZO⁻) 相矛盾",
    ], fill="#fef2f2", stroke="#fca5a5", size=12.5)
    s.box(488, 530, 456, 76, [
        "修正：在该假设下，电泳项让负电星状体“背离” UV；",
        "若确实正趋光，只能是化学泳占优或 ζ 反号，",
        "而且速度仅 ~μm/s，无法解释 mm/s 的宏观运动（见图3、4）",
    ], fill="#ecfdf5", stroke="#6ee7b7", size=12.5)
    s.save(f"{OUT}/fig2_diffusiophoresis_sign_check.svg")


# ------------------------------------------------------------------ Fig 3
def dish(s, x0, color, up):
    """Side view of a dish with free surface; up=False -> converging surface flow (UV)."""
    cx = x0 + 228
    s.rect(x0 + 20, 150, 416, 150, fill=WATER, stroke="#93c5fd", rx=4)
    s.line(x0 + 20, 150, x0 + 436, 150, color="#3b82f6", sw=2)
    s.lamp_v(cx, 104, color)
    s.poly([(cx - 10, 109), (cx + 10, 109), (cx + 26, 150), (cx - 26, 150)], color, opacity=0.28)
    if not up:
        s.arrow(x0 + 45, 162, cx - 34, 162, "b", 2.6)
        s.arrow(x0 + 412, 162, cx + 34, 162, "b", 2.6)
        s.arrow(cx, 172, cx, 268, "lb", 2)
        s.arrow(cx - 16, 286, x0 + 50, 286, "lb", 2)
        s.arrow(cx + 16, 286, x0 + 406, 286, "lb", 2)
        s.arrow(x0 + 34, 272, x0 + 34, 176, "lb", 2)
        s.arrow(x0 + 422, 272, x0 + 422, 176, "lb", 2)
        s.arrow(x0 + 88, 124, x0 + 128, 124, "k", 1.8)
        s.arrow(x0 + 368, 124, x0 + 328, 124, "k", 1.8)
        s.arrow(x0 + 150, 124, x0 + 180, 124, "k", 1.8)
    else:
        s.arrow(cx - 34, 162, x0 + 45, 162, "b", 2.6)
        s.arrow(cx + 34, 162, x0 + 412, 162, "b", 2.6)
        s.arrow(cx, 268, cx, 172, "lb", 2)
        s.arrow(x0 + 50, 286, cx - 16, 286, "lb", 2)
        s.arrow(x0 + 406, 286, cx + 16, 286, "lb", 2)
        s.arrow(x0 + 34, 176, x0 + 34, 272, "lb", 2)
        s.arrow(x0 + 422, 176, x0 + 422, 272, "lb", 2)
        s.arrow(x0 + 88, 124, x0 + 48, 124, "k", 1.8)
        s.arrow(x0 + 368, 124, x0 + 408, 124, "k", 1.8)
        s.arrow(x0 + 150, 124, x0 + 120, 124, "k", 1.8)
    s.aster(x0 + 88, 146, 0.42)
    s.aster(x0 + 368, 146, 0.42)
    s.rect(x0 + 150 - 14, 141, 28, 11, fill="#cbd5e1", stroke="#64748b", rx=5)


def fig3():
    s = SVG(960, 820, "图3 我认为最可能的运动机理")
    s.text(20, 30, "图3  我认为最可能的机理：光致表面张力梯度（光-毛细 / Marangoni 流）主导宏观运动", 18, bold=True)

    s.text(28, 58, "(a) UV：光斑处 γ 升高 → 表面流向光斑汇聚 →“正趋光”", 14, bold=True)
    dish(s, 16, UV, up=False)
    s.text(268, 94, "光斑处 γ↑", 13, color=UV, bold=True)
    s.lines(36, 322, [
        "顺式异构体表面活性弱、界面上的反式组装体被溶解/脱附；",
        "表面流由低 γ 流向高 γ，漂浮的群落和塑料小球被带到光斑。",
    ], 12)

    s.text(500, 58, "(b) Vis/450 nm 激光：光斑处 γ 降低 → 表面流向外发散 →“负趋光”", 14, bold=True)
    dish(s, 488, VIS, up=True)
    s.text(740, 94, "光斑处 γ↓", 13, color=VIS, bold=True)
    s.lines(508, 322, [
        "反式单体表面活性更强，且黄色悬液强吸收 450 nm 光而升温",
        "（dγ/dT ≈ −0.15 mN m⁻¹ K⁻¹），两者同向使 γ 降低。",
    ], 12)

    # ---- panel c : tube
    s.text(20, 378, "(c) 管内液柱（草稿图4c,f）：两端弯月面的毛细压差驱动整体平移", 14, bold=True)

    def tube(y, color, left_label, move_left, note):
        s.line(160, y, 930, y, color="#94a3b8", sw=2)
        s.line(160, y + 36, 930, y + 36, color="#94a3b8", sw=2)
        s.path(f"M420,{y} L640,{y} Q600,{y+18} 640,{y+36} L420,{y+36} Q460,{y+18} 420,{y}", stroke="#ca8a04", sw=1.2, fill="#fde68a")
        s.lamp_h(70, y + 18, color)
        s.arrow(80, y + 18, 150, y + 18, "p" if color == UV else "o", 4)
        s.text(300, y - 8, left_label, 12, color=color, bold=True)
        if move_left:
            s.arrow(600, y + 58, 455, y + 58, "b", 3.2)
            s.text(620, y + 62, note, 12, color=BLUE)
        else:
            s.arrow(460, y + 58, 605, y + 58, "b", 3.2)
            s.text(625, y + 62, note, 12, color=BLUE)

    tube(412, UV, "左端 γ_L↑ ⇒ p_L = p₀ − 2γ_L cosθ/r 更低", True, "液柱朝 UV 移动（草稿图4c：≈2.4 cm / 450 s）")
    tube(510, VIS, "左端 γ_L↓（光热＋反式）⇒ p_L 更高", False, "液柱背离光源（图4f：≈3.3 cm / 34 s）")
    s.lines(20, 604, [
        "估算：ΔP = 2Δγ cosθ / r ≈ 0.1 Pa（Δγ ≈ 0.1 mN/m，r ≈ 1.5 mm）；Poiseuille：U ≈ ΔP r²/(8ηℓ) ≈ 1–2 mm/s（ℓ ≈ 2 cm），与实测同量级。",
        "液柱内部的扩散泳粒子是“无净力”的，无法对液柱整体施加推力；而同一 Δγ 符号恰好同时解释 UV 朝光、Vis 背光两个方向。",
    ], 12)

    # ---- panel d : microscale
    s.text(20, 666, "(d) 微观尺度（≲100 μm）：星状体作为溶质源/汇 → 局部扩散泳与底面扩散渗透（~0.1–数 μm/s）", 14, bold=True)
    s.line(36, 780, 440, 780, color="#64748b", sw=3)
    s.circle(190, 750, 78, fill="url(#haloSrc)", stroke="none")
    s.aster(190, 752, 0.62)
    s.text(190, 690, "UV：溶解 → 源（离子晕）", 11, "middle", color="#be185d")
    s.circle(320, 764, 8, fill="#cbd5e1", stroke="#64748b")
    s.arrow(332, 764, 366, 764, "k", 1.6)
    s.arrow(308, 764, 280, 764, "k", 1.6, dash="3 3")
    s.text(350, 750, "方向取决于 ζ、β′", 11, color=MUTED)
    s.lines(488, 696, [
        "尺度分工（我的判断）：",
        "• mm–cm、~mm/s：界面张力梯度（光化学＋光热）主导群落、液柱、货物；",
        "• μm、~μm/s：溶质梯度泳动决定单个星状体与邻近颗粒的相互作用；",
        "• 同一“γ 对光的响应符号”即可统一解释 4 个宏观现象：",
        "  UV 群落汇聚、UV 液柱朝光；Vis 群落发散、Vis 液柱背光。",
    ], 12, lh=19)
    s.save(f"{OUT}/fig3_motion_proposed.svg")


# ------------------------------------------------------------------ Fig 4
def fig4():
    s = SVG(960, 500, "图4 速度数量级对比")
    s.text(20, 30, "图4  速度数量级：扩散泳估算 vs 草稿实测的宏观运动 vs 界面张力驱动估算", 18, bold=True)
    X0, X1, lo, hi = 330, 930, -8, -1
    px = (X1 - X0) / (hi - lo)

    def X(v):
        return X0 + (math.log10(v) - lo) * px

    top, bot = 60, 392
    labels = {-8: "10 nm/s", -7: "0.1 μm/s", -6: "1 μm/s", -5: "10 μm/s", -4: "0.1 mm/s", -3: "1 mm/s", -2: "1 cm/s", -1: "10 cm/s"}
    for k, lab in labels.items():
        x = X0 + (k - lo) * px
        s.line(x, top, x, bot, color="#e2e8f0", sw=1)
        s.text(x, bot + 18, lab, 11, "middle", color=MUTED)
    s.line(X0, bot, X1, bot, color=INK, sw=1.2)
    # shaded gap
    s.rect(X(5e-6), top, X(4e-5) - X(5e-6), bot - top, fill="#fef3c7", stroke="none", rx=0, opacity=0.7)
    s.text((X(5e-6) + X(4e-5)) / 2, top + 14, "空档", 11, "middle", color="#92400e")

    rows = [
        ("扩散泳理论估算", "|ζ|≈40 mV，∇ln c ≈ 1/(10–100 μm)", (1e-7, 5e-6), BLUE),
        ("草稿图3h 微珠位移", "按图中位移/时间粗估", (8e-8, 3e-7), "#64748b"),
        ("草稿图4c UV 液柱", "2.4 cm / 450 s", (5.3e-5, None), UV),
        ("草稿图4b,e 群落运动", "轨迹长度 / 时间色标粗估", (5e-4, 2e-3), INK),
        ("草稿图4f Vis 液柱", "3.3 cm / 34 s", (9.7e-4, None), VIS),
        ("Marangoni 表面流估算", "Δγ = 0.01–0.1 mN/m，h≈3 mm，L≈1 cm", (8e-4, 8e-3), GREEN),
        ("毛细压差液柱估算", "Δγ = 0.001–0.1 mN/m，r≈1.5 mm，ℓ≈2 cm", (2e-5, 2e-3), GREEN),
    ]
    y = top + 34
    for name, sub, (a, b), c in rows:
        s.text(20, y + 1, name, 13, bold=True, color=c if c != INK else INK)
        s.text(20, y + 17, sub, 11, color=MUTED)
        if b is None:
            s.circle(X(a), y + 4, 7, fill=c, stroke="white", sw=1.5)
        else:
            s.rect(X(a), y - 3, X(b) - X(a), 14, fill=c, stroke="none", rx=7, opacity=0.85)
        y += 46
    s.lines(20, 438, [
        "宏观运动（~mm/s）比扩散泳（~0.1–数 μm/s）快 2–4 个数量级，而界面张力梯度只需 0.01–0.1 mN/m 的差值即可给出正确量级。",
        "离子梯度靠扩散建立的时间 t ≈ L²/2D（D ≈ 0.6×10⁻⁹ m²/s）：L = 100 μm → 8 s；1 mm → 14 min；1 cm → 约 23 h。",
        "远处群落在数秒内即响应，只能由界面应力/流体动力学传递，而不是由离子梯度本身传递。",
    ], 12, lh=19)
    s.save(f"{OUT}/fig4_speed_scales.svg")


fig1(); fig2(); fig3(); fig4()
print("ok")

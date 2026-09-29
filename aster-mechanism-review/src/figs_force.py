import math, sys
from svglib import *

OUT = sys.argv[1]
MT = "#c08a1a"


def radial_arrows(s, x, y, r1, r2, n, m, inward, offset=0.0, sw=2):
    for i in range(n):
        a = 2 * math.pi * i / n + offset
        xa, ya = x + r1 * math.cos(a), y + r1 * math.sin(a)
        xb, yb = x + r2 * math.cos(a), y + r2 * math.sin(a)
        if inward:
            s.arrow(xb, yb, xa, ya, m, sw)
        else:
            s.arrow(xa, ya, xb, yb, m, sw)


# ------------------------------------------------------------------ Fig 5
def fig5():
    s = SVG(960, 650, "图5 草稿的光致产生力机理")
    s.text(20, 30, "图5  草稿中“光致产生力”的机理：以有丝分裂微管星状体为类比", 18, bold=True)

    # (a) biology
    s.rect(16, 46, 456, 300, fill="#fffbeb", stroke="#fcd34d", rx=10)
    s.text(28, 70, "(a) 生物原型：微管的聚合/解聚产生推力与拉力", 14, bold=True)
    L, R, cy = 80, 408, 190
    for i in range(-5, 6):
        a = i * 0.13
        s.line(L, cy, L + 150 * math.cos(a), cy + 150 * math.sin(a), color=MT, sw=1.6, opacity=0.7)
        s.line(R, cy, R - 150 * math.cos(a), cy + 150 * math.sin(a), color=MT, sw=1.6, opacity=0.7)
    for pole in (L, R):
        s.circle(pole, cy, 15, fill="#22c55e", stroke="#15803d")
        s.rect(pole - 6, cy - 4, 12, 8, fill=RED, stroke="none", rx=2)
    # chromosome
    s.path("M234,165 L254,215 M254,165 L234,215", stroke="#7e22ce", sw=7)
    s.circle(236, 190, 4, fill="#0ea5e9", stroke="none")
    s.circle(252, 190, 4, fill="#0ea5e9", stroke="none")
    s.line(244, 110, 244, 270, color="#7e22ce", sw=1, dash="4 4")
    s.text(244, 104, "赤道板", 11, "middle", color="#7e22ce", halo=True)
    s.arrow(180, 150, 226, 160, "r", 2.2)
    s.text(120, 138, "生长→推（极向排斥力）", 11, color=RED, halo=True)
    s.arrow(262, 190, 320, 190, "g", 2.2)
    s.text(270, 240, "收缩→拉", 11, color=GREEN, halo=True)
    s.text(270, 256, "（动粒偶联器保持结合）", 11, color=GREEN, halo=True)
    s.lines(32, 296, [
        "单根微管推力 ~pN（聚合棘轮）；解聚拉力依赖 Ndc80/Dam1 等偶联器。",
        "推/拉平衡使染色体整列于两星状体中间（赤道板）。",
    ], 12)

    # (b) draft analogue
    s.rect(488, 46, 456, 300, fill="#f5f3ff", stroke="#c4b5fd", rx=10)
    s.text(500, 70, "(b) 草稿的人工类比：延伸丝伸缩 = 力", 14, bold=True)
    s.aster(600, 180, 0.55)
    s.circle(600, 180, 40, stroke=RAY, dash="3 3", sw=1)
    radial_arrows(s, 600, 180, 24, 58, 8, "r", inward=True)
    s.text(600, 258, "UV：延伸丝溶解收缩", 12, "middle", color=UV, bold=True)
    s.text(600, 276, "→“向内力（拉）”", 12, "middle", color=RED)
    s.aster(830, 180, 1.0)
    radial_arrows(s, 830, 180, 42, 70, 8, "b", inward=False, offset=0.2)
    s.text(830, 276, "Vis：延伸丝再生长 →“推力”", 12, "middle", color=VIS, bold=True)
    s.lines(502, 306, [
        "⚠ 草稿图3b 在均匀 UV 与均匀 Vis 下都标注 “Radial-Inward Force”，",
        "   与“收缩拉、生长推”的类比本身不一致。",
    ], 12, color=RED)

    # (c) midway alignment
    s.rect(16, 362, 928, 272, fill="#f8fafc", stroke="#cbd5e1", rx=10)
    s.text(28, 386, "(c) 草稿图3e–h：“中间域对齐”，用以模拟染色体整列", 14, bold=True)
    s.aster(130, 500, 0.95)
    s.aster(470, 500, 0.95)
    s.line(300, 420, 300, 590, color="#7e22ce", sw=1.2, dash="5 4")
    s.text(300, 612, "两星状体中线（“赤道”）", 11, "middle", color="#7e22ce")
    s.circle(222, 500, 11, fill="#e2e8f0", stroke="#475569", sw=1.5)
    s.text(222, 530, "微珠 α", 11, "middle")
    s.arrow(236, 500, 290, 500, "r", 2.6)
    s.circle(560, 470, 9, fill="#e2e8f0", stroke="#475569", sw=1.5)
    s.text(560, 450, "微珠 β", 11, "middle")
    s.arrow(572, 470, 612, 470, "g", 2.4)
    s.lines(640, 420, [
        "草稿的论证链：",
        "光能 → 延伸丝生长/收缩 → 机械力 → 货物定位",
        "• 图3g：两星状体周围的矢量场＋热图",
        "  （色标 0–250，单位与测量方法未注明）；",
        "• 图3g 待补：“中间无力区逐渐扩大”；",
        "• 图3h：微珠 α 移至中线并停住，β 被推离；",
        "• 标题称“光能”，摘要却写“化学能 → 机械功”；",
        "• 正文“Traction force …”小节目前只有标题。",
    ], 12, lh=22)
    s.save(f"{OUT}/fig5_force_draft.svg")


# ------------------------------------------------------------------ Fig 6
def fiber(s, x1, x2, y, h1, h2, fill="#86efac", stroke=RAY, dash=None, opacity=None):
    pts = [(x1, y - h1 / 2), (x2, y - h2 / 2), (x2, y + h2 / 2), (x1, y + h1 / 2)]
    p = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' opacity="{opacity}"' if opacity is not None else ""
    s.add(f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="1.2"{d}{o}/>')


def fig6():
    s = SVG(960, 760, "图6 我认为的力的来源（一）")
    s.text(20, 30, "图6  我认为的“力”的来源（一）：光只改变化学势；推力来自接触式生长，收缩不能产生拉力", 18, bold=True)

    s.text(20, 62, "(a) 能量链：光是“充电器”，真正做功的是过饱和反式单体的组装自由能", 14, bold=True)
    chain = [
        (["UV 光子", "≈ 3.4 eV"], "#ede9fe", "#a78bfa"),
        (["trans → cis", "储能 ≈ 0.5 eV/分子", "(≈ 50 kJ/mol)"], "#ede9fe", "#a78bfa"),
        (["cis 可溶", "延伸丝溶解", "（能量存于溶液）"], "#fce7f3", "#f9a8d4"),
        (["Vis 光子 / 热", "cis → trans"], "#ffedd5", "#fdba74"),
        (["反式单体过饱和", "S = c / c_eq"], "#ffedd5", "#fdba74"),
        (["组装自由能", "Δμ = kT ln S", "仅“生长＋接触”时做功"], "#dcfce7", "#86efac"),
    ]
    bw, gap, x = 146, 10, 16
    for i, (ls, f, st) in enumerate(chain):
        s.box(x, 76, bw, 72, ls, fill=f, stroke=st, size=12)
        if i < len(chain) - 1:
            s.arrow(x + bw + 1, 112, x + bw + gap - 1, 112, "k", 1.6)
        x += bw + gap
    s.text(20, 172, "类比：cis 异构体扮演 GTP-微管蛋白中“化学燃料”的角色；光并不直接“推”东西，而是把体系泵到非平衡的化学势。", 12, color=MUTED)

    # (b) contact push
    s.rect(16, 190, 456, 270, fill="#f0fdf4", stroke="#86efac", rx=10)
    s.text(28, 214, "(b) 生长推力：原理上成立（结晶压 / 聚合棘轮）", 14, bold=True)
    fiber(s, 40, 300, 310, 26, 16)
    s.circle(337, 310, 34, fill="#e2e8f0", stroke="#475569", sw=1.5)
    s.rect(300, 300, 4, 20, fill="#bae6fd", stroke="none", rx=1)
    for (xx, yy, r) in [(282, 270, 20), (318, 264, -30), (268, 350, 10), (312, 358, 40)]:
        s.azo(xx, yy, r, 0.8)
    s.arrow(372, 310, 426, 310, "g", 3)
    s.text(398, 298, "F", 14, "middle", bold=True, color=GREEN)
    s.text(302, 386, "尖端与物体间须保持液膜以供料", 11, "middle", color=MUTED)
    s.lines(32, 414, [
        "热力学上限：F ≤ A · (kT/Ω) · ln S （A 为接触面积，Ω 为分子体积）",
        "条件：① Vis 下持续过饱和；② 纤维尖端与物体接触；③ 供料不被堵死。",
    ], 12)
    s.text(446, 236, "✓", 22, "end", bold=True, color=GREEN)

    # (c) shrink pull
    s.rect(488, 190, 456, 270, fill="#fef2f2", stroke="#fca5a5", rx=10)
    s.text(500, 214, "(c) 收缩拉力：缺少偶联器，不成立", 14, bold=True)
    fiber(s, 512, 680, 300, 26, 18)
    fiber(s, 680, 772, 300, 18, 14, fill="none", stroke=RAY, dash="4 3")
    s.circle(808, 300, 34, fill="#e2e8f0", stroke="#475569", sw=1.5)
    for (xx, yy, r) in [(700, 268, 20), (735, 330, -30), (760, 262, 10), (716, 340, 40)]:
        s.azo(xx, yy, r, 0.8)
    s.co(748, 280)
    s.co(700, 322)
    s.arrow(676, 356, 626, 356, "k", 1.8)
    s.text(512, 380, "UV：尖端溶解后退，与物体脱离 → 无拉力", 12, color=RED)
    s.text(918, 236, "✗", 22, "end", bold=True, color=RED)
    # kinetochore inset
    s.rect(512, 396, 416, 54, fill="#ffffff", stroke="#e5e7eb", rx=6)
    s.rect(530, 416, 150, 14, fill="#fde68a", stroke=MT, rx=3)
    s.add(f'<ellipse cx="672" cy="423" rx="7" ry="16" fill="none" stroke="#2563eb" stroke-width="3"/>')
    s.arrow(700, 423, 740, 423, "b", 2)
    s.lines(748, 418, ["生物：Dam1 环 / Ndc80 在解聚端", "偏置扩散 → 仍保持结合并被拉动"], 11, lh=15)

    # (d) thickness-dependent dissolution
    s.rect(16, 476, 928, 270, fill="#f8fafc", stroke="#cbd5e1", rx=10)
    s.text(28, 500, "(d) 表观“从尖端收缩”：由粗细梯度决定的溶解次序，而非微管式端部特异解聚", 14, bold=True)
    s.circle(64, 614, 26, fill=CORE, stroke="#ca8a04")
    rows = [(556, "t₀"), (614, "t₁"), (672, "t₂")]
    lens = [470, 380, 280]
    for (y, lab), Lx in zip(rows, lens):
        full = 470
        h2 = 26 - (26 - 6) * (Lx / full)
        fiber(s, 90, 90 + Lx, y, 26, h2)
        if Lx < full:
            fiber(s, 90 + Lx, 90 + full, y, h2, 6, fill="none", stroke=RAY, dash="4 3", opacity=0.6)
        s.text(80, y + 5, lab, 12, "end", bold=True)
    s.text(96, 530, "根部 ≈ 700 nm 高", 11, color=MUTED)
    s.text(560, 530, "尖端 ≈ 160 nm 高", 11, "end", color=MUTED)
    s.lines(596, 530, [
        "• 草稿 AFM：延伸丝高度由 700 nm 渐减至 160 nm；",
        "  细端比表面积大、曲率溶解度高（Gibbs–Thomson），",
        "  在同样光照下最先溶完 → 看起来像“尖端收缩”。",
        "• 紧密层状堆积中顺反异构受空间限制，",
        "  异构化主要发生在表面与缺陷处，溶解是表面控制的。",
        "• 可检验预测：截断纤维的两端应同时后退；",
        "  收缩速率 ∝ 局部光强 × 比表面积，",
        "  与“哪一端”无关（微管则强烈依赖正/负端）。",
    ], 12, lh=22)
    s.save(f"{OUT}/fig6_force_proposed_contact.svg")


# ------------------------------------------------------------------ Fig 7
def fig7():
    s = SVG(960, 720, "图7 我认为的力的来源（二）")
    s.text(20, 30, "图7  我认为的“力”的来源（二）：星状体是溶质源/汇，经扩散泳定位货物；“向内”流可来自光热对流", 18, bold=True)

    def panel(x0, sink):
        cx1, cx2, ya = x0 + 100, x0 + 356, 290
        s.rect(x0, 46, 456, 330, fill="#fff7ed" if sink else "#f5f3ff", stroke="#fdba74" if sink else "#c4b5fd", rx=10)
        title = "(a) Vis：两个生长中的星状体 = 汇 → 中线浓度极大" if sink else "(b) UV：两个溶解中的星状体 = 源 → 中线浓度极小"
        s.text(x0 + 12, 70, title, 14, bold=True)
        # axes for c(x)
        s.line(x0 + 30, 206, x0 + 430, 206, color="#94a3b8", sw=1)
        s.text(x0 + 30, 96, "c(x)", 12, italic=True)
        pts = []
        for i in range(0, 201):
            x = x0 + 30 + i * 2
            g = math.exp(-abs(x - cx1) / 55) + math.exp(-abs(x - cx2) / 55)
            y = 110 + 80 * g if sink else 196 - 80 * g
            pts.append(f"{x:.1f},{y:.1f}")
        s.path("M" + " L".join(pts), stroke=CO, sw=2.5)
        mid = (cx1 + cx2) / 2
        s.line(mid, 96, mid, 328, color="#7e22ce", sw=1.2, dash="5 4")
        s.text(mid + 6, 104 if sink else 232, "中线：c 极大" if sink else "中线：c 极小", 11, color="#7e22ce", halo=True)
        s.aster(cx1, ya, 0.72 if sink else 0.5)
        s.aster(cx2, ya, 0.72 if sink else 0.5)
        if sink:
            for bx, d in [(mid - 50, 1), (mid + 50, -1)]:
                s.circle(bx, ya, 9, fill="#e2e8f0", stroke="#475569", sw=1.5)
                s.arrow(bx + d * 11, ya, bx + d * 38, ya, "g", 2.4)
            s.text(x0 + 228, 352, "货物（化学泳主导时沿 ∇c 向上）→ 中线为稳定点", 12, "middle", color=GREEN)
            s.text(x0 + 228, 368, "梯度随时间变平 →“中间无力区”扩大", 11, "middle", color=MUTED)
        else:
            for bx, d in [(mid - 30, -1), (mid + 30, 1)]:
                s.circle(bx, ya, 9, fill="#e2e8f0", stroke="#475569", sw=1.5)
                s.arrow(bx + d * 11, ya, bx + d * 42, ya, "r", 2.4)
            s.text(x0 + 228, 352, "同一货物被引向星状体 → 中线变为不稳定点", 12, "middle", color=RED)
            s.text(x0 + 228, 368, "（若货物 ζ 或背景电解质 β′ 反号，两图互换）", 11, "middle", color=MUTED)

    panel(16, True)
    panel(488, False)

    # (c) photothermal convection
    s.rect(16, 392, 928, 314, fill="#f8fafc", stroke="#cbd5e1", rx=10)
    s.text(28, 416, "(c) 为什么草稿图3b 在 UV 与 Vis 下都是“径向向内”：光热自然对流 / 热渗透，与生长或收缩方向无关", 14, bold=True)
    base = 640
    s.rect(40, 450, 480, base - 450, fill=WATER, stroke="none", rx=0)
    s.line(40, base, 520, base, color="#475569", sw=3)
    s.text(46, base + 20, "基底（盖玻片）", 11, color=MUTED)
    s.poly([(262, 440), (298, 440), (318, 600), (242, 600)], UV, opacity=0.12)
    s.poly([(270, 440), (290, 440), (306, 600), (254, 600)], VIS, opacity=0.18)
    s.text(340, 452, "UV 或 Vis 照射", 11, color=MUTED)
    s.circle(280, 612, 60, fill="url(#warm)", stroke="none")
    s.add(f'<ellipse cx="280" cy="628" rx="16" ry="8" fill="{CORE}" stroke="#ca8a04"/>')
    for dx in (-70, -50, -30, 30, 50, 70):
        s.line(280 + dx * 0.25, 630, 280 + dx, 634 + (dx % 3), color=RAY, sw=2)
    s.arrow(280, 590, 280, 470, "r", 3)
    s.text(292, 498, "浮力羽流上升", 11, color=RED)
    s.arrow(60, 624, 200, 624, "b", 2.6)
    s.arrow(500, 624, 360, 624, "b", 2.6)
    s.text(70, 612, "底面附近径向向内的补偿流", 11, color=BLUE, halo=True)
    s.path("M270,470 C200,460 120,480 90,560", stroke="#60a5fa", sw=1.6, m="lb", dash="5 4")
    s.path("M290,470 C360,460 440,480 470,560", stroke="#60a5fa", sw=1.6, m="lb", dash="5 4")
    s.text(280, 676, "吸收的光 → 星状体局部升温 ΔT", 12, "middle", color=RED)

    s.lines(548, 448, [
        "• PIV / 示踪给出的是速度场，不是力；",
        "  换算为力必须给出本构：Stokes 拖曳，",
        "  或（牵引力显微镜）已标定的基底模量。",
        "• 以图3h 为例：a ≈ 1 μm，U ≈ 0.1 μm/s",
        "  ⇒ 6πηaU ≈ 2 fN，比单根微管推力",
        "  （~pN）小约 3 个数量级。",
        "• 预测：向内流强度 ∝ 吸收功率，",
        "  不随 UV/Vis 的生长/收缩方向反号；",
        "  可用温敏荧光（罗丹明 B）测 ΔT，",
        "  或改变液层厚度、倒置样品来检验。",
    ], 12.5, lh=23)
    s.save(f"{OUT}/fig7_force_proposed_fields.svg")


fig5(); fig6(); fig7()
print("ok")

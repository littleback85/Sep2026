"""Build pickering_pmax_report.pdf: figure, legend, focus and logic arc, SI notes.

Run after fig_pmax_integrated.py and key_numbers.py:  python3 build_report.py
"""
import os
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
                                PageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
import matplotlib
import pore_model as pm

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data/fonts/ttf")
for name, fn in [("DV", "DejaVuSans.ttf"), ("DV-B", "DejaVuSans-Bold.ttf"),
                 ("DV-I", "DejaVuSans-Oblique.ttf"), ("DV-BI", "DejaVuSans-BoldOblique.ttf")]:
    pdfmetrics.registerFont(TTFont(name, os.path.join(FONT_DIR, fn)))
addMapping("DV", 0, 0, "DV"); addMapping("DV", 1, 0, "DV-B")
addMapping("DV", 0, 1, "DV-I"); addMapping("DV", 1, 1, "DV-BI")

INK = colors.HexColor("#0b0b0b"); INK2 = colors.HexColor("#52514e"); ACC = colors.HexColor("#0072B2")
body = ParagraphStyle("body", fontName="DV", fontSize=9, leading=12.8, textColor=INK, alignment=TA_JUSTIFY,
                      spaceAfter=5)
legend = ParagraphStyle("legend", parent=body, fontSize=8.2, leading=11.2, spaceAfter=3.5)
eq = ParagraphStyle("eq", parent=body, alignment=TA_CENTER, spaceBefore=2, spaceAfter=6)
cell = ParagraphStyle("cell", parent=body, fontSize=7.6, leading=10, alignment=0, spaceAfter=0)
cellb = ParagraphStyle("cellb", parent=cell, fontName="DV-B")
h1 = ParagraphStyle("h1", fontName="DV-B", fontSize=15, leading=19, textColor=INK, spaceAfter=4)
h2 = ParagraphStyle("h2", fontName="DV-B", fontSize=11.5, leading=15, textColor=INK, spaceBefore=10, spaceAfter=5)
h3 = ParagraphStyle("h3", fontName="DV-B", fontSize=9.4, leading=13, textColor=ACC, spaceBefore=7, spaceAfter=3)
sub = ParagraphStyle("sub", parent=body, fontSize=9, textColor=INK2, spaceAfter=8, alignment=0)
ref = ParagraphStyle("ref", parent=body, fontSize=7.8, leading=10.4, spaceAfter=2, alignment=0)


def P(s, st=body):
    return Paragraph(s, st)


def table(rows, widths, header=True):
    data = [[Paragraph(c, cellb if (header and i == 0) else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * mm for w in widths], hAlign="LEFT", repeatRows=1 if header else 0)
    t.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.8, INK), ("LINEBELOW", (0, 0), (-1, 0), 0.5, INK2),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, INK),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f2ee")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


# ---------------------------------------------------------------- numbers used in the text
th70 = np.radians(70)
mono_hex = pm.phat_bridge(pm.L_HEX, th70)
bil_hex = pm.phat_bilayer(pm.L_HEX, pm.L_HEX, th70)
mono_vac = pm.phat_bridge(2.0, th70)
bil_vac = pm.phat_bilayer(2.0, 2.0, th70)
bil_one = pm.phat_bilayer(2.0, pm.L_HEX, th70)
kPa = lambda phat, R, g=0.030: phat * 2 * g / R / 1e3
fmt = lambda x: f"{x:,.0f}" if x >= 100 else f"{x:.3g}"

story = []
story += [
    P("Maximum capillary pressure of particle-laden emulsion films: monolayers, bilayers and defects", h1),
    P("Pore-scale model of film rupture by capillary penetration through the gaps of a particle layer. "
      "Every curve comes from one closed-form or numerical model with no fitted parameters "
      "(code: <font face='DV-I'>pore_model.py</font>, <font face='DV-I'>fig_pmax_integrated.py</font>). "
      "October 2026.", sub),
]

# ---------------------------------------------------------------- figure
fig_w = 183 * mm
fig_h = fig_w * 160 / 183
story.append(Image(os.path.join(HERE, "fig_pmax_integrated.png"), width=fig_w, height=fig_h))
story.append(Spacer(1, 4))

# ---------------------------------------------------------------- legend
L = []
L.append(P("<b>Fig. 1 | The largest gap in the particle layer, not the close-packed lattice, sets the maximum capillary "
           "pressure of a Pickering emulsion film.</b> "
           "<b>a</b>, Cross-sections at the onset of failure, drawn to scale from the model (θ = 70°). Left: a bridging "
           "monolayer whose central pore is widened to a clear opening <i>h</i> = 0.7<i>R</i> between close-packed neighbours. "
           "At <i>P</i> = <i>P</i><sub>max</sub> the two oil–water menisci (blue) touch on the mid-plane (dotted) and a hole "
           "opens, while the menisci in the close-packed pores have barely sagged. <i>L</i>, distance from the pore axis to "
           "the particle centres; θ, contact angle measured through water. Right: a nested bilayer loaded to 70% of its "
           "failure pressure. Oil 1 must first penetrate its own layer (1); the partner layer then behaves as a bridging "
           "monolayer (2). "
           "<b>b</b>, Top views of the pore geometries used below; the orange circle is the largest particle-free disc "
           "(radius <i>h</i>) in each pore. In iv the vacancy in the upper layer (dark) is covered by the intact lower layer "
           "(light). "
           "<b>c</b>, Dimensionless failure pressure <i>P</i><sub>max</sub><i>R</i>/2γ against contact angle for a close-packed "
           "lattice (solid) and a single vacancy (dashed). The monolayer value vanishes as cos θ; the bilayer does not. "
           "For θ > 90° (grey) a bridging particle dewets and ruptures the film. "
           "<b>d</b>, Failure pressure against clear opening <i>h</i>/<i>R</i> (θ = 70°). Symbols on the monolayer curve mark "
           "the geometries of b (i, close packed; ii, bond gaps <i>s</i> = 0.2<i>R</i> and 0.4<i>R</i>; iii, vacancy). "
           "The monolayer follows the closed form 4γ<i>R</i> cos θ/[<i>h</i>(<i>h</i> + 2<i>R</i>)], which tends to "
           "<i>h</i><sup>−2</sup> for wide gaps. A defect confined to one layer of a bilayer (orange dashed) cannot lower "
           "<i>P</i><sub>max</sub> below the bridging value of the intact partner layer. "
           "<b>e</b>, Failure pressure against centre-to-centre spacing <i>d</i> for a uniformly expanded hexagonal lattice "
           "(top axis: area coverage φ = 0.907(2<i>R</i>/<i>d</i>)<sup>2</sup>) and for one stretched bond in an otherwise "
           "close-packed layer. The axis range matches c and d. "
           "<b>f</b>, Absolute <i>P</i><sub>max</sub> against particle radius for γ = 30 mN m<sup>−1</sup> and θ = 70° "
           "(all curves scale as γ/<i>R</i>). Dotted lines: Laplace pressure 2γ/<i>a</i> of drops of radius <i>a</i>, the "
           "scale of the film capillary pressure in a quiescent cream. "
           "<b>g</b>, Critical clear opening <i>h</i>* at which <i>P</i><sub>max</sub> falls to 2γ/<i>a</i>, against the "
           "drop-to-particle size ratio. γ cancels, so the curves hold for any oil. Films whose largest opening is smaller "
           "than <i>h</i>* hold. "
           "In c–g the bilayer is a nested (hcp) stack with layer spacing 1.63<i>R</i>. No experimental data are plotted; "
           "the reported critical pressures we found are discussed in SI Note 3.", legend))
story += L

# ---------------------------------------------------------------- focus and logic arc
story.append(P("Focus and logic arc", h2))
story.append(P(
    "<b>Focus.</b> A particle layer holds two oils apart because each oil–water meniscus must bulge through the gaps "
    "between particles before the two oils can touch. The figure makes one claim. The pressure a film can withstand is "
    "set by its widest gap, through a single closed-form law, "
    "<i>P</i><sub>max</sub> = 4γ<i>R</i> cos θ / [<i>h</i>(<i>h</i> + 2<i>R</i>)]. A second particle layer changes "
    "the answer qualitatively, because a gap in one layer is covered by the other."))
story.append(P(
    "<b>a → b: mechanism and geometry.</b> Panel a shows the failure event itself rather than an idealized cartoon. "
    "Both sketches are drawn from the model, so the sag of each meniscus is to scale. A widened pore fails while its "
    "close-packed neighbours are still nearly flat, which is why the widest gap matters. Panel b defines the four "
    "geometries used in the plots, each by a single number: the radius <i>h</i> of the largest particle-free disc."))
story.append(P(
    f"<b>c: contact angle separates monolayer from bilayer.</b> For a bridging monolayer the menisci only need to reach "
    f"the mid-plane, and the required curvature goes to zero as cos θ. A bilayer meniscus must instead push past the "
    f"equator of its own particles before it can reach the other oil. That threshold stays finite at θ = 90°. At "
    f"θ = 70° the close-packed bilayer is {bil_hex/mono_hex:.2f}× stronger than the monolayer; at 85° it is "
    f"{pm.phat_bilayer(pm.L_HEX, pm.L_HEX, np.radians(85))/pm.phat_bridge(pm.L_HEX, np.radians(85)):.1f}× stronger. "
    f"This is the contact-angle signature that distinguishes the two structures in an experiment."))
story.append(P(
    f"<b>d: the central panel.</b> One curve covers every defect: P<sub>max</sub> ∝ 1/<i>h</i> for "
    f"narrow gaps and ∝ 1/<i>h</i><sup>2</sup> for wide ones. A single vacancy lowers P<sub>max</sub> of a monolayer "
    f"{mono_hex/mono_vac:.0f}-fold. Stretching one bond by 0.2<i>R</i> already costs 23%, independent of θ and γ. "
    f"In a bilayer, a vacancy in one layer leaves P<sub>max</sub> at the intact partner's bridging value "
    f"({bil_one:.2f} versus {bil_hex:.2f} in units of 2γ/<i>R</i>, about −{100*(1-bil_one/bil_hex):.0f}%). "
    f"Only coincident defects reach the low values ({bil_vac:.2f}). Bilayers are therefore defect tolerant and monolayers are not."))
story.append(P(
    "<b>e: spacing.</b> This panel separates two situations that are often lumped together as 'lower coverage'. "
    "Expanding the whole lattice (for example by electrostatic repulsion between particles) and stretching one "
    "bond lower P<sub>max</sub> by similar amounts at small strain. Uniform expansion keeps lowering it, because every "
    "pore widens at once. Coverage alone therefore does not set P<sub>max</sub>; the size of the largest opening does."))
story.append(P(
    f"<b>f: absolute scale.</b> Converted to kilopascals for γ = 30 mN m<sup>−1</sup>, a defect-free layer of "
    f"0.5 µm particles holds {kPa(mono_hex, 0.5e-6):.0f} kPa (monolayer) or {kPa(bil_hex, 0.5e-6):.0f} kPa (bilayer). "
    f"That is far above the 6 kPa Laplace pressure of a 10 µm drop. A perfect lattice is therefore almost never the "
    f"limiting element. A vacancy ({kPa(mono_vac, 0.5e-6):.0f} kPa) or a gap three particle radii wide "
    f"({kPa(pm.phat_bridge(4.0, th70), 0.5e-6):.1f} kPa) brings P<sub>max</sub> into the range of real loads."))
story.append(P(
    "<b>g: the design rule.</b> Equating P<sub>max</sub> with the drop Laplace pressure gives a critical opening, "
    "<i>h</i>*(<i>h</i>* + 2<i>R</i>) = 2<i>aR</i> cos θ. γ drops out, so this holds for any oil. For "
    "<i>a</i>/<i>R</i> = 20 (0.5 µm particles, 10 µm drops) and θ = 70°, a monolayer tolerates bare patches up to "
    "<i>h</i>* ≈ 2.8<i>R</i>, about three particle diameters across. A bilayer requires two such patches aligned. "
    "In practice, coalescence of particle-coated drops is a question of coverage defects, not of the "
    "close-packed lattice."))
story.append(P("What was left out, and why", h3))
story.append(P(
    "<b>Measured critical pressures</b> (silica/decane ≈ 100 kPa; carbon black 2.2–4.6 kPa) are not plotted. They are "
    "centrifuge onset pressures (osmotic pressure at the base of a cream), not film capillary pressures. No particle "
    "radius was reported, and we could only find them in secondary sources. Placing them on panel f would require an "
    "invented x-coordinate (SI Note 3). "
    "<b>The empirical prefactor band</b> <i>p</i> = 0.1–1 in Kaptay's form 2<i>p</i>γ cos θ/<i>R</i> is not drawn. We "
    "could not check it against Kaptay's tabulated values. The model instead gives "
    "<i>p</i><sub>eff</sub> = 2<i>R</i><sup>2</sup>/[<i>h</i>(<i>h</i> + 2<i>R</i>)] (SI Note 1), so <i>p</i> = 0.1–1 "
    "corresponds to openings of 0.7<i>R</i>–3.6<i>R</i>, which is consistent with the defect picture. "
    "<b>Particle detachment</b> is excluded: in a bridging monolayer both oils press on a particle with the same "
    "pressure, so there is no net normal force. "
    "<b>Water-in-oil emulsions</b> follow from θ → 180° − θ and add nothing new. "
    "<b>Drainage kinetics, disjoining pressure and contact-angle hysteresis</b> change when a film fails, not the "
    "static threshold. They are discussed in SI Note 2."))

# ---------------------------------------------------------------- SI
story.append(PageBreak())
story.append(P("Supplementary Information", h2))

story.append(P("SI Note 1 | Pore model and equations", h3))
story.append(P(
    "Consider the opening between particles in an oil–water film. Each particle is a sphere of radius <i>R</i>. The "
    "pore is replaced by an axisymmetric ring of spheres whose centres lie a distance <i>L</i> from the pore axis, so the "
    "largest particle-free disc in the centre plane has radius <i>h</i> = <i>L</i> − <i>R</i>. For the triangular pore "
    "of a close-packed layer, <i>L</i> = 2<i>R</i>/√3 and <i>h</i> = 0.155<i>R</i> exactly. The oil pressure exceeds "
    "the water pressure by <i>P</i>, so the meniscus in the pore is a spherical cap of radius "
    "<i>R</i><sub>c</sub> = 2γ/<i>P</i> that bulges into the water. It meets each particle at the contact angle θ "
    "(measured through water). If the cap slope at the contact line is ψ, the contact line sits at polar angle "
    "α = θ + ψ on the sphere, and the cap spans a circle of radius ρ = <i>L</i> − <i>R</i> sin(θ + ψ). Laplace's law "
    "then gives"))
story.append(P("<i>P</i><i>R</i>/2γ = sin ψ / [<i>L</i>/<i>R</i> − sin(θ + ψ)].", eq))
story.append(P(
    "As <i>P</i> rises, ψ grows and the cap sags by ρ tan(ψ/2) below its contact line. The film fails at the first of "
    "two events. <i>Meet</i>: the sag reaches the plane where the opposing meniscus lies. <i>Slide</i>: <i>P</i> passes "
    "the maximum of the expression above, so the contact line can no longer stay put and slides down the particle. For "
    "a bridging monolayer the two menisci meet on the centre plane. At that moment the cap sphere touches the centre "
    "plane on the pore axis, so its centre is at height <i>R</i><sub>c</sub>. It also meets each particle sphere at "
    "angle θ. The law of cosines for the two intersecting spheres gives "
    "<i>L</i><sup>2</sup> + <i>R</i><sub>c</sub><sup>2</sup> = <i>R</i><sup>2</sup> + <i>R</i><sub>c</sub><sup>2</sup> "
    "+ 2<i>R</i><i>R</i><sub>c</sub> cos θ, and hence the closed form"))
story.append(P("<b><i>P</i><sub>max</sub> = 4γ<i>R</i> cos θ / (<i>L</i><sup>2</sup> − <i>R</i><sup>2</sup>) "
               "= 4γ<i>R</i> cos θ / [<i>h</i>(<i>h</i> + 2<i>R</i>)]</b>  (bridging monolayer).", eq))
story.append(P(
    "A full numerical solution of the cap equations confirms that the menisci meet before the sliding instability for "
    "every θ from 5° to 85° and every <i>h</i> from 0.155<i>R</i> to 5<i>R</i>. The closed form matches it to within "
    "3 × 10<sup>−4</sup>. Special cases follow directly. A close-packed hexagonal monolayer gives "
    "<i>P</i><sub>max</sub> = 12γ cos θ/<i>R</i>. A uniformly expanded hexagonal lattice with centre spacing <i>d</i> "
    "gives 12γ<i>R</i> cos θ/(<i>d</i><sup>2</sup> − 3<i>R</i><sup>2</sup>). One bond stretched to <i>d</i> = 2<i>R</i> + "
    "<i>s</i> turns the neighbouring pore into a (2<i>R</i>, 2<i>R</i>, <i>d</i>) triangle with circumradius "
    "<i>L</i> = 4<i>R</i><sup>2</sup>/(16<i>R</i><sup>2</sup> − <i>d</i><sup>2</sup>)<sup>1/2</sup>. This gives "
    "<i>P</i><sub>max</sub>(<i>d</i>)/<i>P</i><sub>max</sub>(2<i>R</i>) = (16<i>R</i><sup>2</sup> − "
    "<i>d</i><sup>2</sup>)/(3<i>d</i><sup>2</sup>), valid while <i>d</i> < 2√2<i>R</i>, independent of θ and γ. A "
    "vacancy (<i>h</i> = <i>R</i>) gives 4γ cos θ/3<i>R</i>, one ninth of the close-packed value. A θ < 90° is required: "
    "for θ > 90° the expression changes sign, which is the bridging–dewetting instability of particle antifoams."))
story.append(P(
    "Written in Kaptay's form, <i>P</i><sub>max</sub> = 2<i>p</i>γ cos θ/<i>R</i>, the model gives an effective "
    "prefactor <i>p</i><sub>eff</sub> = 2<i>R</i><sup>2</sup>/[<i>h</i>(<i>h</i> + 2<i>R</i>)]. That is 6 for a "
    "close-packed layer, 0.67 for a vacancy and 0.13 for <i>h</i> = 3<i>R</i>. This model is the more "
    "optimistic member of the family. Replacing three discrete spheres by a continuous ring makes the pore more "
    "confining than it really is, so absolute values for close packing are probably too high by tens of per cent. "
    "Ratios between geometries are less sensitive to this. An earlier version of this figure used an assumed band "
    "<i>p</i> = 0.1–1. In the present picture that band corresponds to films limited by openings of "
    "0.7<i>R</i>–3.6<i>R</i>, not by the ideal lattice."))
story.append(P(
    "<b>Bilayers.</b> Each oil is covered by its own layer, and the layers are stacked in the nested position with "
    "centre planes 1.63<i>R</i> apart. Oil 1 can only reach oil 2 in two steps. First, its meniscus must penetrate its "
    "own layer, which needs pressure <i>P</i><sub>pen</sub>. For close packing this is set by the sliding instability, "
    "because the meniscus cannot reach the mid-plane while still pinned above the particle equator. Second, once "
    "oil 1 has flooded the gap, the partner layer is wetted by oil on both sides. It then fails like a bridging "
    "monolayer, at <i>P</i><sub>br</sub>. Either oil may go first, so"))
story.append(P("<i>P</i><sub>max</sub><sup>bilayer</sup> = min{ max[<i>P</i><sub>pen</sub>(1), <i>P</i><sub>br</sub>(2)], "
               "max[<i>P</i><sub>pen</sub>(2), <i>P</i><sub>br</sub>(1)] }.", eq))
story.append(P(
    f"Because <i>P</i><sub>br</sub> < <i>P</i><sub>pen</sub> for the same lattice, an intact bilayer fails at "
    f"<i>P</i><sub>pen</sub>. That is {bil_hex:.2f} × 2γ/<i>R</i> at θ = 70°, against {mono_hex:.2f} for the bridging "
    f"monolayer. It remains finite at θ = 90° (≈ 1.8 × 2γ/<i>R</i>), which matches the qualitative statement that a "
    f"double layer carries an extra positive term in Kaptay's formula. A defect in one layer only lowers the first "
    f"step. The partner's bridging threshold then sets the failure pressure, so a vacancy in one layer costs "
    f"{100*(1-bil_one/bil_hex):.0f}% at θ = 70°. Two coincident vacancies cost {100*(1-bil_vac/bil_hex):.0f}%."))

rows = [["θ (°)", "Monolayer, close packed", "Bilayer, close packed", "Monolayer, vacancy",
         "Bilayer, coincident vacancies", "Bilayer, vacancy in one layer"]]
for t in [30, 50, 60, 70, 80, 85]:
    th = np.radians(t)
    rows.append([str(t)] + [f"{v:.2f}" for v in [
        pm.phat_bridge(pm.L_HEX, th), pm.phat_bilayer(pm.L_HEX, pm.L_HEX, th), pm.phat_bridge(2.0, th),
        pm.phat_bilayer(2.0, 2.0, th), pm.phat_bilayer(2.0, pm.L_HEX, th)]])
story.append(KeepTogether([P("<b>Table S1 | </b><i>P</i><sub>max</sub><i>R</i>/2γ for the main geometries.", legend),
                           table(rows, [14, 31, 31, 31, 33, 34])]))
story.append(Spacer(1, 6))
rows = [["Particle radius", "Monolayer, close packed", "Bilayer, close packed", "Monolayer, vacancy",
         "Monolayer, h = 3R"]]
for R, lab in [(10e-9, "10 nm"), (100e-9, "100 nm"), (0.5e-6, "0.5 µm"), (1e-6, "1 µm"), (5e-6, "5 µm")]:
    rows.append([lab] + [fmt(kPa(v, R)) for v in [mono_hex, bil_hex, mono_vac, pm.phat_bridge(4.0, th70)]])
story.append(KeepTogether([P("<b>Table S2 | </b>Absolute <i>P</i><sub>max</sub> (kPa) for γ = 30 mN m<sup>−1</sup>, "
                             "θ = 70°. For comparison, the drop Laplace pressure 2γ/<i>a</i> is 60, 6 and 0.6 kPa for "
                             "<i>a</i> = 1, 10 and 100 µm.", legend),
                           table(rows, [30, 36, 36, 36, 36])]))

story.append(P("SI Note 2 | Stability of Pickering emulsions", h3))
story.append(P(
    "Particles stabilize emulsions differently from surfactants. A particle of radius <i>R</i> at an oil–water "
    "interface lowers the free energy by π<i>R</i><sup>2</sup>γ(1 − |cos θ|)<sup>2</sup>. For a 0.5 µm particle at "
    "θ = 70° and γ = 30 mN m<sup>−1</sup> this is about 10<sup>−14</sup> J, or 10<sup>6</sup> <i>kT</i>. Even for "
    "10 nm particles it is of order 10<sup>2</sup>–10<sup>3</sup> <i>kT</i>. Adsorption is therefore effectively "
    "irreversible. The layer does not relax by exchange with the bulk, as a surfactant monolayer does. Instead it "
    "acts as a solid, jammed skin that is fixed once the drop is made. Two consequences follow. Drop size is "
    "fixed by the available particle area through limited coalescence: drops merge during and after emulsification "
    "until their total area is just covered. Dense, nearly close-packed layers are therefore the natural end state, "
    "not a special case. And because the particles cannot leave, Ostwald ripening and deformation are resisted "
    "mechanically, which is why particle-coated drops can stay non-spherical (arrested coalescence)."))
story.append(P(
    "When two coated drops are pressed together, by creaming, by centrifugation or in a concentrated emulsion, the "
    "water between them forms a film. The film can take two structures. In a bilayer each drop keeps its own layer. "
    "In a bridging monolayer a single layer of particles is shared by both drops, each particle protruding into both "
    "oils. Squeezing does not turn a close-packed bilayer into a monolayer. A monolayer holds half as many particles "
    "per area, so half of them would have to leave the interfaces, at a cost of order 10<sup>6</sup> <i>kT</i> each. "
    "Bridging monolayers form instead when the layers are sparse enough to interdigitate (coverage below about half "
    "of close packing), typically during emulsification or with too little particle. They are only stable for "
    "θ < 90° (measured through the continuous phase). For θ > 90° a bridging particle pulls the two menisci together "
    "and ruptures the film, which is the bridging–dewetting mechanism of particle antifoams. Both structures have "
    "been observed in the same emulsion."))
story.append(P(
    "A coated film fails when the oil reaches across it. The particles never have to move: the oil goes through the "
    "gaps between them once the capillary pressure exceeds what the curved menisci in those gaps can hold (SI Note 1). "
    "Three features matter in practice. First, the threshold scales as γ/<i>R</i>, so smaller particles give "
    "stronger films if they can be packed equally well. Second, it falls with contact angle as cos θ for a bridging "
    "monolayer. Particles too close to 90° give weak bridged films, although they adsorb most strongly, while "
    "very hydrophilic particles (θ ≲ 30°) adsorb weakly. This trade-off underlies the often-quoted optimum near "
    "θ ≈ 70° for oil-in-water emulsions. Third, and most important, the threshold is set by the widest opening, "
    "not by the average packing. The film pressure in a quiescent cream is of order the drop Laplace pressure "
    "2γ/<i>a</i>. That is one to three decades below the threshold of an ideal lattice, so the drops that do merge "
    "are those with uncovered patches several particle diameters wide. Such patches come from incomplete "
    "coverage, polydisperse or aggregated particles, grain boundaries in the jammed layer, and particles pushed aside "
    "by lateral capillary forces as the menisci deform."))
story.append(P(
    "This picture explains several observations without extra assumptions. Emulsions near the limited-coalescence "
    "boundary, where coverage is just sufficient, are fragile, while a modest excess of particle makes them very "
    "robust. Raising the particle concentration beyond full coverage improves stability only insofar as it heals "
    "defects or creates bilayers and particle networks in the continuous phase. Salt and pH, which control particle "
    "aggregation and θ, change stability by orders of magnitude, through both the contact angle and the size of the "
    "gaps in the layer. Bilayers, which form naturally between densely covered drops, are far more forgiving than "
    "shared monolayers, because a gap in one layer is covered by the other."))
story.append(P(
    "The model is static and deliberately minimal. It treats the pore as axisymmetric and ignores gravity and line "
    "tension. It assumes the menisci merge as soon as they touch. With surfactant or strong electrostatic repulsion, a "
    "thin water film could survive contact and add a disjoining-pressure barrier, so the meet criterion is a lower "
    "bound in that case. Contact-angle hysteresis matters because the oil advances, so the water-receding angle "
    "applies. It is smaller than the equilibrium angle and raises <i>P</i><sub>max</sub>. Particle rearrangement "
    "under load and drainage kinetics decide <i>when</i> a film reaches its threshold, not the threshold itself. Two "
    "experiments would test the main predictions most directly. A thin-film pressure balance (porous-plate cell) "
    "applies a known capillary pressure to a single coated film. Varying θ there should distinguish the cos θ "
    "dependence of a bridging monolayer from the finite intercept of a bilayer. Deliberately controlled coverage "
    "should show the 1/<i>h</i><sup>2</sup> law of panel d."))

story.append(P("SI Note 3 | Reported critical pressures and why they are not plotted", h3))
rows = [["System", "Reported value", "What was measured", "Status of the number"],
        ["Hydrophobized silica, n-decane/water (Kruglyakov, Nushtaeva and co-workers)",
         "≈ 100 kPa, about 25% of the authors' own calculated maximum (≈ 400 kPa)",
         "Centrifuge onset of coalescence; also thin emulsion layers on a porous plate",
         "Found in secondary literature; the original value was not seen. Particle radius in the test not reported to us"],
        ["Carbon black 0.015 wt%, 0.6 M NaCl", "4.6 kPa", "Centrifuge demulsification pressure",
         "Secondary source; original paper not confirmed"],
        ["Carbon black 0.015 wt%, pH 3.3, no salt", "2.2 kPa", "As above", "As above"]]
story.append(table(rows, [44, 38, 44, 50]))
story.append(Spacer(1, 4))
story.append(P(
    "A centrifuge measures the osmotic pressure at the base of the cream at the moment coalescence starts. Turning that "
    "into a film capillary pressure needs the oil fraction and drop size, which we do not have. With 0.27 µm silica "
    "particles, γ = 50 mN m<sup>−1</sup> and θ ≈ 70°, the model gives about 760 kPa for an ideal bridging monolayer. "
    "That is the same order as the authors' own calculated ≈ 400 kPa. The measured onset is several-fold lower, as "
    "expected if defects control failure. The carbon black values lie below every ideal-lattice prediction for any "
    "plausible particle size, and are consistent with failure at openings of a few particle radii. These are "
    "consistency checks, not tests: the values are too few and too uncertain to place on the figure."))

story.append(P("References", h3))
refs = [
    "Denkov, N. D., Ivanov, I. B., Kralchevsky, P. A. &amp; Wasan, D. T. A possible mechanism of stabilization of "
    "emulsions by solid particles. <i>J. Colloid Interface Sci.</i> <b>150</b>, 589–593 (1992). Journal, volume and page checked; title from memory.",
    "Kaptay, G. On the equation of the maximum capillary pressure induced by solid particles to stabilize emulsions "
    "and foams and on the emulsion stability diagrams. <i>Colloids Surf. A</i> <b>282–283</b>, 387–401 (2006).",
    "Kruglyakov, P. M., Nushtaeva, A. V. &amp; Vilkova, N. G. Experimental investigation of capillary pressure "
    "influence on breaking of emulsions stabilized by solid particles. <i>J. Colloid Interface Sci.</i> <b>276</b>, "
    "465–474 (2004). †",
    "Horozov, T. S. &amp; Binks, B. P. Particle-stabilized emulsions: a bilayer or a bridging monolayer? "
    "<i>Angew. Chem. Int. Ed.</i> <b>45</b>, 773–776 (2006). †",
    "Tcholakova, S., Denkov, N. D. &amp; Lips, A. Comparison of solid particles, globular proteins and surfactants "
    "as emulsifiers. <i>Phys. Chem. Chem. Phys.</i> <b>10</b>, 1608–1627 (2008). †",
    "Pieranski, P. Two-dimensional interfacial colloidal crystals. <i>Phys. Rev. Lett.</i> <b>45</b>, 569 (1980). †",
    "Arditty, S., Whitby, C. P., Binks, B. P., Schmitt, V. &amp; Leal-Calderon, F. Some general features of limited "
    "coalescence in solid-stabilized emulsions. <i>Eur. Phys. J. E</i> <b>11</b>, 273–281 (2003). †",
    "Binks, B. P. Particles as surfactants: similarities and differences. <i>Curr. Opin. Colloid Interface Sci.</i> "
    "<b>7</b>, 21–41 (2002). †",
]
for i, r in enumerate(refs, 1):
    story.append(P(f"{i}. {r}", ref))
story.append(P("† Cited from memory; details could not be checked from this environment and should be verified "
               "before use. Kaptay (ref. 2) was checked by title and volume only; its tabulated p values could not be read.", ref))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("DV", 7.5); canvas.setFillColor(INK2)
    canvas.drawRightString(A4[0] - 13.5 * mm, 9 * mm, f"{doc.page}")
    canvas.drawString(13.5 * mm, 9 * mm, "Pickering films: maximum capillary pressure")
    canvas.restoreState()


doc = SimpleDocTemplate(os.path.join(HERE, "pickering_pmax_report.pdf"), pagesize=A4,
                        leftMargin=13.5 * mm, rightMargin=13.5 * mm, topMargin=13 * mm, bottomMargin=15 * mm,
                        title="Maximum capillary pressure of particle-laden emulsion films",
                        author="littleback85")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("pdf written")

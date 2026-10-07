"""Build the PDF report: Figure 1 + legend + focus/logic arc, SI note on the fit, Figure S1 + Table S1.

Run after analysis.py:  python3 build_pdf.py  -> coacervate_osmotic_modulus_report.pdf
"""
import json
import os

import numpy as np
import matplotlib
from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak,
                                KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results.json")))

FONT_DIR = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data/fonts/ttf")
for name, fn in [("DV", "DejaVuSans.ttf"), ("DV-B", "DejaVuSans-Bold.ttf"),
                 ("DV-I", "DejaVuSans-Oblique.ttf"), ("DV-BI", "DejaVuSans-BoldOblique.ttf")]:
    pdfmetrics.registerFont(TTFont(name, os.path.join(FONT_DIR, fn)))
addMapping("DV", 0, 0, "DV"); addMapping("DV", 1, 0, "DV-B")
addMapping("DV", 0, 1, "DV-I"); addMapping("DV", 1, 1, "DV-BI")

INK = colors.HexColor("#0b0b0b"); INK2 = colors.HexColor("#52514e"); ACC = colors.HexColor("#4a3aa7")
body = ParagraphStyle("body", fontName="DV", fontSize=9, leading=12.6, textColor=INK, alignment=TA_JUSTIFY,
                      spaceAfter=5)
small = ParagraphStyle("small", parent=body, fontSize=7.8, leading=10.4, spaceAfter=3)
cell = ParagraphStyle("cell", parent=body, fontSize=7.4, leading=10, alignment=0, spaceAfter=0)
cellb = ParagraphStyle("cellb", parent=cell, fontName="DV-B")
h1 = ParagraphStyle("h1", fontName="DV-B", fontSize=15, leading=19, textColor=INK, spaceAfter=4)
h2 = ParagraphStyle("h2", fontName="DV-B", fontSize=11.5, leading=15, textColor=INK, spaceBefore=9, spaceAfter=5)
h3 = ParagraphStyle("h3", fontName="DV-B", fontSize=9.5, leading=13, textColor=ACC, spaceBefore=6, spaceAfter=3)
sub = ParagraphStyle("sub", parent=body, fontSize=9, textColor=INK2, spaceAfter=8)

# ---------------------------------------------------------------- numbers used in the text
k0, a = R["k0"], R["alpha"]
f2 = lambda v: f"{v:.2f}"
f1 = lambda v: f"{v:.1f}"
K0s = f"K<sub>0</sub> = {f2(k0)} MPa (95 % CI {f2(R['ci_k0'][0])}–{f2(R['ci_k0'][1])})"
As = f"α = {f1(a)} ({f1(R['ci_alpha'][0])}–{f1(R['ci_alpha'][1])})"
K15 = f"{f1(R['K_15'])} MPa ({f1(R['ci_K_15'][0])}–{f1(R['ci_K_15'][1])})"
K1 = f"{f1(R['K_1MPa'])} MPa ({f1(R['ci_K_1MPa'][0])}–{f1(R['ci_K_1MPa'][1])})"
E1 = f"ε = {f2(R['eps_1MPa'])} ({f2(R['ci_eps_1MPa'][0])}–{f2(R['ci_eps_1MPa'][1])})"
H1 = f"h/h<sub>0</sub> = {f2(R['h_1MPa'])} ({f2(R['h_1MPa_ci'][0])}–{f2(R['h_1MPa_ci'][1])})"
eps_at = lambda pi_mpa: float(np.log1p(a * pi_mpa / k0) / a)
pct = lambda pi_mpa: f"{100 * (1 - np.exp(-eps_at(pi_mpa))):.1f} %"
step = ", ".join(f2(s) for s in R["step_K"])

TITLE = "Osmotic equation of state of a PDDA/BSA coacervate layer under PEG compression"
SUBTITLE = ("Heights at 80 h, 0–15 % PEG (n = 3 per group) · nominal PEG osmotic pressures · stiffening fit "
            "extrapolated to Π = 1 MPa · 20 % PEG shown in the SI only")

LEGEND = (
    "<b>Figure 1 | The PDDA/BSA coacervate stiffens as it is dehydrated: its osmotic modulus rises from about "
    f"{f1(k0)} MPa toward {f1(R['K_15'])} MPa over the measured range, and is projected to reach about "
    f"{f1(R['K_1MPa'])} MPa at 1 MPa.</b> "
    "<b>(a)</b> PEG osmotic pressure Π against log height strain ε = −ln(h/h<sub>0</sub>) of the laterally confined "
    "coacervate layer after 80 h, for 0 % (grey), 5 % (blue), 10 % (orange) and 15 % (green) PEG. Top axis: the same "
    "strain as relative height h/h<sub>0</sub>. Open circles: individual samples. Squares: group mean ± SD (n = 3). "
    "Solid black line: stiffening equation of state K = dΠ/dε = K<sub>0</sub> + αΠ, i.e. "
    "Π(ε) = (K<sub>0</sub>/α)(e<super>αε</super> − 1), fitted to all 12 samples with strain regressed on Π "
    f"({K0s}; {As}). Dashed line: the same curve extrapolated from 0.41 MPa (15 % PEG) to Π = 1 MPa; the shaded "
    "strip above 0.41 MPa marks the region with no 0–15 % data. Grey band: 95 % bootstrap interval of the curve "
    "(4000 resamples within groups). Open diamond: the extrapolated state at 1 MPa, "
    f"{E1}, {H1}, local modulus K = {K1}. The 20 % PEG samples (Π ≈ 0.77 MPa) are not used and are not shown "
    "(Fig. S1e). "
    "<b>(b)</b> The coacervate modulus compared with benchmarks from soft matter, log scale. Coacervate (black): "
    "filled circle = K<sub>0</sub>, thick bar = K over the measured range (up to 15 % PEG), dashed bar and open "
    "diamond = extrapolation to 1 MPa. The dark grey band (K<sub>0</sub> to K at 15 % PEG) and the light band "
    "(up to K at 1 MPa) are carried across the panel. Filled circles: osmotic or confined-compression moduli "
    "K = c ∂Π/∂c. The PEG baths are computed from a Rand-type fit log<sub>10</sub>Π = a + b·w<super>0.21</super> "
    "through the nominal 5–15 % values, in the colours of (a). BSA: Carnahan–Starling hard spheres "
    "(M = 66.4 kDa; bar v<sub>eff</sub> = 1.2–1.5 mL g<super>−1</super>, dot 1.35). 150 mM NaCl: ideal van ’t Hoff, "
    "K = Π. Cell: Boyle–van ’t Hoff osmometer at 290 mOsm with an osmotically inactive fraction of 0.2–0.4. "
    "Articular cartilage: equilibrium aggregate modulus in confined compression (range over depth; dot = full "
    "thickness, Schinagl et al. 1997). Synthetic gels: typical osmotic moduli of swollen gels. Open diamonds (grey): "
    "shear moduli, for scale only — PEGDA gels are this lab's G′ (1.5–15 kPa), complex coacervates typical "
    "plateau G′ (Spruijt et al. 2013)."
)

FOCUS = (
    "<b>Focus.</b> PEG osmotic stress fixes the water activity outside the coacervate layer; the layer loses water "
    "until its own osmotic pressure matches Π, and its height reports the volume this took. The figure asks: "
    "<b>how hard is it to squeeze water out of this coacervate, and does that resistance grow as the coacervate "
    "becomes denser?</b> The answer is a stiffening equation of state. The small-strain osmotic modulus is "
    f"K<sub>0</sub> ≈ {f1(k0)} MPa, and the modulus rises with pressure at a rate α ≈ {f1(a)}, so it is "
    f"≈ {f1(R['K_15'])} MPa at 15 % PEG and is projected to ≈ {f1(R['K_1MPa'])} MPa at 1 MPa. Even at 1 MPa the "
    f"layer is predicted to keep about {100 * R['h_1MPa']:.0f} % of its height. That puts the coacervate among very "
    "crowded protein fluids and living cells, far above gels and above its own shear response."
)

ARC = [
    ("a · Measure the equation of state and its curvature.",
     "With lateral confinement, height is volume and −ln(h/h<sub>0</sub>) is the natural compression variable, "
     "so the local slope dΠ/dε is the thermodynamic osmotic modulus K = c ∂Π/∂c. The data are not a straight "
     f"line: the step moduli between group means are {step} MPa, i.e. the layer gets harder to compress the "
     "more it is compressed. The one-parameter-extra stiffening law K = K<sub>0</sub> + αΠ captures this with two "
     "physically readable numbers — the modulus of the uncompressed coacervate and how fast it stiffens. "
     "Integrating it and extending to 1 MPa shows where the layer is heading: compression slows down rather than "
     "running away. The extrapolation is drawn dashed, with its bootstrap band, because it goes 2.4× beyond the "
     "highest pressure used in the fit."),
    ("b · Calibrate the number.",
     "A modulus means little without a scale. On one log axis the coacervate range (K<sub>0</sub> to K at 15 % "
     "PEG) overlaps 300–400 g/L BSA, a cell under osmotic load, physiological saline and the stiff end of "
     "cartilage, and the extrapolated 1 MPa value goes beyond all of them. It is 2–4 orders of magnitude above "
     "swollen gels and above any shear modulus a coacervate shows. The contrast with shear is the physical point: a "
     "coacervate flows, yet it holds onto its water as tightly as a dense protein phase — and holds it more "
     "tightly the drier it gets."),
]

TAKEHOME = (
    f"<b>Take-home.</b> K<sub>osm</sub> = {f2(k0)} + {f1(a)}·Π MPa from 0–15 % PEG. The coacervate dehydrates "
    "reversibly and smoothly under osmotic stress and stiffens as it does, like a concentrated protein or "
    "polyelectrolyte fluid. A coacervate film is therefore hard to thin by dehydration, which is the property that "
    "matters when it separates two oil droplets (SI Note 1). 20 % PEG gives a collapse that this equation of state "
    "does not predict, with wall climbing; it is reported in the SI but not used."
)

# ---------------------------------------------------------------- SI Note 1
SI_NOTE = [
    ("h2", "SI Note 1 | The stiffening fit: why this form, why the coacervate stiffens, and what it means for "
           "coacervate-stabilised oil droplets"),
    ("h3", "1. What was fitted and how"),
    ("p", "The layer is laterally confined, so V/V<sub>0</sub> = h/h<sub>0</sub>. At equilibrium the PEG pressure Π "
          "equals the coacervate's own osmotic pressure, so Π against ε = −ln(h/h<sub>0</sub>) is the coacervate "
          "equation of state, and its local slope is the osmotic modulus K = c ∂Π/∂c = dΠ/dε. We take the modulus to "
          "rise linearly with the pressure it carries,"),
    ("eq", "K(Π) = K<sub>0</sub> + αΠ   ⇒   Π(ε) = (K<sub>0</sub>/α)·(e<super>αε</super> − 1),   "
           "ε(Π) = (1/α)·ln(1 + αΠ/K<sub>0</sub>)"),
    ("p", "Π is the variable the experiment sets and ε is the one that scatters, so ε(Π) was fitted to the 12 "
          f"individual 80 h heights (0, 5, 10, 15 % PEG) by least squares. Result: {K0s}, {As}; 95 % intervals "
          "from 4000 bootstrap resamples within each PEG group. The curve passes through Π = 0 at ε = 0 by "
          "construction, which is correct for a coacervate in equilibrium with its own dilute phase."),
    ("h3", "2. Why this form, and not a straight line"),
    ("p", f"<b>The data curve.</b> The step moduli between group means are {step} MPa: the last step is roughly "
          "twice the first two. A constant K cannot describe that; the stiffening law follows it with one extra "
          "parameter."),
    ("p", "<b>The parameters mean something.</b> K<sub>0</sub> is the modulus of the uncompressed coacervate, and α "
          "= dK/dΠ is its dimensionless pressure derivative. This is the Murnaghan equation of state used for "
          "liquids and solids under pressure, so α can be compared directly with other condensed phases "
          f"(liquid water α ≈ 6; most liquids and soft solids 4–10). The fitted α ≈ {f1(a)} says the coacervate "
          "stiffens under dehydration about as strongly as an ordinary dense liquid stiffens under hydrostatic "
          "pressure."),
    ("p", "<b>It integrates in closed form and extrapolates safely.</b> Π(ε) is analytic, monotonic and convex, "
          "and dΠ/dε never decreases. Extrapolated beyond the data it cannot predict a negative modulus, a "
          "maximum or a spurious collapse, unlike a quadratic or higher polynomial in ε."),
    ("p", f"<b>Statistics.</b> Against a single-parameter constant-K fit (K = {f2(R['k_lin'])} MPa) the "
          f"stiffening law gives ΔAICc = {R['d_aicc']:+.1f}. A difference this small is not decisive with n = 12 on "
          "its own; the case for the stiffening form is that it follows the step moduli, has interpretable "
          "parameters and matches the physics below. It is reported as the equation of state, and the constant-K "
          "number is not used."),
    ("p", "<b>The extrapolation to 1 MPa is a projection, not a measurement.</b> It goes 2.4× past the highest "
          f"fitted pressure. It gives {E1}, {H1}, K = {K1}. The 20 % PEG samples (Π ≈ 0.77 MPa, itself "
          "extrapolated) are a warning: two of three collapsed to "
          f"ε ≈ {np.mean(R['eps_20_obs']):.2f} where the fit predicts ε ≈ {R['eps_20_pred']:.2f}, while the layer "
          "climbed the wall, so height no longer tracked volume. Whether that is an artefact of the geometry or a "
          "real dehydration-induced transition somewhere between 0.41 and 0.77 MPa is not settled by these data. "
          "The curve above 0.41 MPa should be read as what the coacervate does <i>if</i> it stays a single "
          "homogeneous phase."),
    ("h3", "3. Why the coacervate stiffens"),
    ("p", "<b>The osmotic modulus of any concentrated fluid rises with concentration.</b> K = c ∂Π/∂c. Removing "
          "water raises the polymer and protein concentration c, and Π(c) is steeper than linear in a crowded "
          "phase. For a semidilute polymer in good solvent Π ∝ c<super>9/4</super>; for crowded globular proteins "
          "the Carnahan–Starling pressure diverges as the volume fraction approaches packing (Fig. 1b, BSA "
          "200 → 400 g/L raises K about 20-fold). A PDDA/BSA coacervate is both: a dense polyelectrolyte network "
          "of ion-paired chains with BSA packed into it."),
    ("p", "<b>The easy water leaves first.</b> The first water removed is bulk-like water between chains and "
          "proteins. What remains is increasingly hydration water on charged groups and protein surfaces and "
          "water associated with counter-ions held in the coacervate, which is more expensive to remove. Each "
          "further increment of dehydration costs more pressure."),
    ("p", "<b>Excluded volume and electrostatics both grow as the phase densifies.</b> Chain–chain and "
          "protein–protein contacts increase, the free volume available to water falls, and ion pairs and "
          "residual charges are pushed closer together. All of these terms raise ∂Π/∂c, and they do so "
          "progressively — which is what a positive α encodes."),
    ("h3", "4. Implication: the coacervate film between two oil droplets"),
    ("p", "When two coacervate-coated oil droplets are pressed together, the two coacervate coatings form a film "
          "in the gap. The droplets can only coalesce if that film thins to a molecular thickness and ruptures. The "
          "film can thin in two ways: (i) the coacervate itself flows sideways out of the gap, and (ii) water is "
          "squeezed out of the coacervate, densifying and thinning it in place. The osmotic modulus governs route "
          "(ii) directly, and the film pressure that drives it is set by the droplets: in a pressed film it "
          "equals the capillary (Laplace) pressure P<sub>c</sub> ≈ 2γ/R of the drops, or, in a creamed or "
          "centrifuged emulsion, the compressive stress on the drop pack."),
    ("p", "<b>Realistic film pressures barely dehydrate the film.</b> Taking an oil–coacervate interfacial "
          "tension γ = 1–10 mN m<super>−1</super> (typical of low-tension coacervate interfaces; not measured "
          "here), a 1 µm droplet gives P<sub>c</sub> ≈ 2–20 kPa and a 10 µm droplet 0.2–2 kPa. The fitted "
          f"equation of state says 20 kPa thins the film by only {pct(0.02)} through dehydration, and 2 kPa by "
          f"{pct(0.002)}. Strong centrifugation of a cream layer (Δρ ≈ 100 kg m<super>−3</super>, 10 000 g, 1 cm "
          f"of cream) loads films with about 0.1 MPa, which still thins them by only {pct(0.1)}. To reach the "
          f"1 MPa end of Fig. 1a, which still only thins the film by {100 * (1 - R['h_1MPa']):.0f} %, needs "
          "droplets of R = 2γ/Π ≈ 2–20 nm — far smaller than any emulsion droplet. Dehydration alone cannot bring "
          "the two oil surfaces into contact."),
    ("p", "<b>Stiffening makes the film self-limiting.</b> Because K rises with Π, each increment of squeezing "
          "makes the next increment harder; a stiffening film approaches a finite thickness under any finite load "
          "rather than thinning without bound. A softening equation of state (dK/dΠ &lt; 0) would be the "
          "dangerous case: past a threshold pressure the film would collapse in one step, as a gas film does. The "
          "data show no sign of it up to 0.41 MPa, roughly 20–200× the capillary pressure of micron droplets: the "
          "step moduli rise, and the best-fit α ≈ "
          f"{f1(a)} is positive (its bootstrap interval reaches down to ≈ 0, i.e. a constant modulus, but not "
          "below). Transient pressure spikes in collisions or shear are met with a stiffer film than the "
          "resting value suggests."),
    ("p", "<b>A hydrated film keeps the oil surfaces apart.</b> Because water is held so tightly, the film stays "
          "a hydrated, polymer- and protein-rich layer rather than a dry, glassy skin. Its thickness under load is "
          "set by its equation of state, so the droplets remain separated by a condensed phase of finite "
          "thickness, not by a draining water film that can reach zero. Coalescence then requires removing the "
          "coacervate itself by lateral flow (route i), which is resisted by the coacervate viscosity (orders of "
          "magnitude above water) and is a separate, rheological question."),
    ("p", "<b>Limits of the argument.</b> (1) The test compresses a laterally confined layer against one PEG "
          "reservoir; a droplet film can also flow sideways, so the osmotic modulus bounds dehydration-driven "
          "thinning, not total thinning. (2) γ and droplet size were not measured; the numbers above are "
          "order-of-magnitude. (3) The 20 % PEG collapse suggests the coacervate may have a dehydration limit "
          "between 0.41 and 0.77 MPa; this matters only for nanometre droplets or very harsh compaction. "
          "(4) The PEG pressures are nominal; PEG uptake or salt redistribution would lower the effective Π and "
          "with it K<sub>0</sub>. (5) Heights are digitised from images (reading error ≈ 0.005 in h/h<sub>0</sub>)."),
]


def si_table():
    head = ["PEG", "Sample"] + [f"{t} h" for t in R["times"]]
    rows = [head]
    for g in (0, 5, 10, 15):                     # 20 % PEG is not tabulated (Fig. S1e only)
        for s in (1, 2, 3):
            rows.append([f"{g}%", str(s)] + [f"{v:.3f}" for v in R["table"][f"{g},{s}"]])
    data = [[Paragraph(c, cellb if i == 0 else cell) for c in r] for i, r in enumerate(rows)]
    width = 174 * mm
    widths = [width * 0.08, width * 0.1] + [width * 0.82 / 9] * 9
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.8, INK), ("LINEBELOW", (0, 0), (-1, 0), 0.5, INK2),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, INK),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f2ee")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


FIGS1_LEGEND = (
    "<b>Figure S1 | Relative height h/h<sub>0</sub> of every coacervate layer over 80 h of PEG osmotic stress. "
    "(a–e)</b> Individual samples at 0, 5, 10, 15 and 20 % PEG (sample 1 blue circles, sample 2 orange triangles, "
    "sample 3 green diamonds). Panel titles give the nominal PEG osmotic pressure. For 20 % it is extrapolated (*) "
    "from a Rand-type fit log<sub>10</sub>Π = a + b·w<super>0.21</super> through the 5–15 % values. At 20 % PEG "
    "sample 2 (open triangles, dotted) stalls at h/h<sub>0</sub> ≈ 0.88, less compressed than any 15 % sample, "
    "while samples 1 and 3 collapse to h/h<sub>0</sub> ≈ 0.38 as the layer climbs the wall, so height no longer "
    "reports volume. The 20 % group is therefore not used for the equation of state. <b>(f)</b> Mean ± SD (n = 3) "
    "for 0–15 % PEG. The 80 h values are the inputs to Figure 1a. Data were digitised from the original per-sample "
    "plots (reading error ≈ 0.005). Values hidden by overlapping markers were solved from the plotted group means."
)


def img(path, width):
    w, h = PILImage.open(path).size
    return Image(path, width=width, height=width * h / w)


def build(path):
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=15 * mm, bottomMargin=15 * mm, title=TITLE,
                            author="PDDA/BSA coacervate osmotic modulus analysis")
    story = [Paragraph(TITLE, h1), Paragraph(SUBTITLE, sub),
             img(os.path.join(HERE, "fig1_osmotic_modulus.png"), 160 * mm), Spacer(1, 4),
             Paragraph(LEGEND, small), PageBreak(),
             Paragraph("What the figure shows, and how the panels build the argument", h2),
             Paragraph(FOCUS, body), Paragraph("Logic arc through the panels", h3)]
    for head, txt in ARC:
        story.append(Paragraph(f"<b>{head}</b> {txt}", body))
    story += [Spacer(1, 3), Paragraph(TAKEHOME, body), PageBreak(),
              Paragraph("Supplementary Information", h1)]
    eq = ParagraphStyle("eq", parent=body, alignment=1, fontSize=9.2, spaceBefore=2, spaceAfter=7)
    for kind, txt in SI_NOTE:
        story.append(Paragraph(txt, {"h2": h2, "h3": h3, "p": body, "eq": eq}[kind]))
    story += [PageBreak(), img(os.path.join(HERE, "figS1_relative_height.png"), 174 * mm), Spacer(1, 4),
              Paragraph(FIGS1_LEGEND, small), Spacer(1, 8),
              KeepTogether([Paragraph("Table S1 | Digitised h/h<sub>0</sub> for every sample and time point, "
                                      "0–15 % PEG", h3), si_table()])]

    def footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont("DV", 7); canvas.setFillColor(INK2)
        canvas.drawRightString(A4[0] - 18 * mm, 9 * mm, f"{doc_.page}")
        canvas.drawString(18 * mm, 9 * mm, "PDDA/BSA coacervate · osmotic equation of state")
        canvas.restoreState()
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    out = os.path.join(HERE, "coacervate_osmotic_modulus_report.pdf")
    build(out)
    print("wrote", out)

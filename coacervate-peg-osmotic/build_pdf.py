"""Build the PDF report: figure + legend + focus/logic arc + README notes + SI figure.

Run after analysis.py:  python3 build_pdf.py  -> coacervate_osmotic_modulus_report.pdf
"""
import csv
import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
                                PageBreak, ListFlowable, ListItem)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
import matplotlib
from PIL import Image as PILImage

import analysis as A

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data/fonts/ttf")
for name, fn in [("DV", "DejaVuSans.ttf"), ("DV-B", "DejaVuSans-Bold.ttf"),
                 ("DV-I", "DejaVuSans-Oblique.ttf"), ("DV-BI", "DejaVuSans-BoldOblique.ttf"),
                 ("DVM", "DejaVuSansMono.ttf")]:
    pdfmetrics.registerFont(TTFont(name, os.path.join(FONT_DIR, fn)))
addMapping("DV", 0, 0, "DV"); addMapping("DV", 1, 0, "DV-B")
addMapping("DV", 0, 1, "DV-I"); addMapping("DV", 1, 1, "DV-BI")

INK = colors.HexColor("#0b0b0b"); INK2 = colors.HexColor("#52514e"); ACC = colors.HexColor("#4a3aa7")
body = ParagraphStyle("body", fontName="DV", fontSize=9, leading=12.6, textColor=INK, alignment=TA_JUSTIFY,
                      spaceAfter=5)
small = ParagraphStyle("small", parent=body, fontSize=7.8, leading=10.4, spaceAfter=3)
cell = ParagraphStyle("cell", parent=body, fontSize=7.4, leading=10.8, alignment=0, spaceAfter=0)
cellb = ParagraphStyle("cellb", parent=cell, fontName="DV-B")
h1 = ParagraphStyle("h1", fontName="DV-B", fontSize=15, leading=19, textColor=INK, spaceAfter=4)
h2 = ParagraphStyle("h2", fontName="DV-B", fontSize=11.5, leading=15, textColor=INK, spaceBefore=9, spaceAfter=5)
h3 = ParagraphStyle("h3", fontName="DV-B", fontSize=9.5, leading=13, textColor=ACC, spaceBefore=6, spaceAfter=3)
sub = ParagraphStyle("sub", parent=body, fontSize=9, textColor=INK2, spaceAfter=8)


# ---------------------------------------------------------------- inline markup
def inline(s):
    """Minimal markdown -> reportlab markup (code, bold, italic, sub/superscripts)."""
    codes = []
    def keep(m):
        codes.append(m.group(1)); return f"\x00{len(codes)-1}\x00"
    s = re.sub(r"`([^`]+)`", keep, s)
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = re.sub(r"(?<!\*)\*([^*\s][^*]*?)\*\*\*", r"<i>\1</i>**", s)   # "*x***" = italic end + bold end
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", s)
    s = re.sub(r"\^\{([^}]*)\}", r"<super>\1</super>", s)
    s = re.sub(r"\^(-?[0-9.]+)", r"<super>\1</super>", s)
    s = re.sub(r"(?<=[A-Za-zνξσωφλρ′])_\{([^}]*)\}", r"<sub>\1</sub>", s)
    s = re.sub(r"(?<=[A-Za-zνξσωφλρΠ′])_(affine|c,eff|c,aff|e,dry|eff|aff|phantom|FLICK|mix|[A-Za-z0-9]{1,2})(?![A-Za-z0-9])",
               r"<sub>\1</sub>", s)
    s = re.sub(r"\x00(\d+)\x00", lambda m: f'<font name="DVM" size="8">{codes[int(m.group(1))]}</font>', s)
    return s


def md_table(rows, first_col_frac=0.34, width=174 * mm):
    parsed = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    parsed = [parsed[0]] + parsed[2:]            # drop the --- separator
    n = len(parsed[0])
    data = [[Paragraph(inline(c), cellb if i == 0 else cell) for c in r] for i, r in enumerate(parsed)]
    w0 = width * first_col_frac
    widths = [w0] + [(width - w0) / (n - 1)] * (n - 1)
    if n == 3:                                   # equations table: give the equation column room
        widths = [width * 0.27, width * 0.47, width * 0.26]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.8, INK), ("LINEBELOW", (0, 0), (-1, 0), 0.5, INK2),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, INK),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f2ee")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def md_to_flowables(text):
    """Convert the README markdown (headings, paragraphs, lists, tables) to flowables."""
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip() or ln.startswith("!["):
            i += 1; continue
        if ln.startswith("# "):
            out.append(Paragraph(inline(ln[2:]), h2)); i += 1; continue
        if ln.startswith("## "):
            out.append(Paragraph(inline(ln[3:]), h2)); i += 1; continue
        if ln.startswith("### "):
            out.append(Paragraph(inline(ln[4:]), h3)); i += 1; continue
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i]); i += 1
            out += [Spacer(1, 2), md_table(rows), Spacer(1, 6)]; continue
        if re.match(r"^\s*(- |\d+\. )", ln):
            ordered = bool(re.match(r"^\s*\d+\. ", ln))
            items = []
            while i < len(lines) and (re.match(r"^\s*(- |\d+\. )", lines[i]) or
                                      (lines[i].startswith("   ") and lines[i].strip())):
                cur = lines[i]
                if re.match(r"^\s*(- |\d+\. )", cur):
                    items.append(re.sub(r"^\s*(- |\d+\. )", "", cur))
                else:
                    items[-1] += " " + cur.strip()
                i += 1
            lf = ListFlowable([ListItem(Paragraph(inline(t), body), leftIndent=12) for t in items],
                              bulletType="1" if ordered else "bullet", start="1" if ordered else "•",
                              bulletFontName="DV", bulletFontSize=8.5, leftIndent=14)
            out += [lf, Spacer(1, 4)]; continue
        para = [ln.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\||\s*- |\s*\d+\. |!\[)", lines[i]):
            para.append(lines[i].strip()); i += 1
        # a line that is only bold (e.g. "**1. ...**") becomes a sub-heading
        if len(para) == 1 and re.fullmatch(r"\*\*.+\*\*:?", para[0]):
            out.append(Paragraph(inline(para[0].strip("*:")), h3))
        elif re.fullmatch(r"\*\*.+?\*\*", para[0]) and len(para) > 1:
            out.append(Paragraph(inline(para[0].strip("*")), h3))
            out.append(Paragraph(inline(" ".join(para[1:])), body))
        else:
            out.append(Paragraph(inline(" ".join(para)), body))
    return out


# ---------------------------------------------------------------- text
L, E, S = A.LIN, A.ENGF, A.STIFF
TITLE = "Osmotic modulus of a PDDA/BSA coacervate layer from PEG osmotic compression"
SUBTITLE = ("Heights at 80 h, 0–15% PEG (n = 3 per group) · nominal PEG osmotic pressures · "
            "20% PEG reported in the SI only")

LEGEND = (
    "<b>Figure 1 | The PDDA/BSA coacervate resists osmotic dehydration with a modulus of about 1.4 MPa, "
    "like a very crowded protein fluid.</b> "
    "<b>(a)</b> PEG osmotic pressure Π against log height strain ε = −ln(h/h<sub>0</sub>) of the coacervate layer "
    "after 80 h, for 0% (grey), 5% (blue), 10% (orange) and 15% (green) PEG. Open circles: individual samples. "
    "Squares: group mean ± SD (n = 3). Because the layer is laterally confined, V/V<sub>0</sub> = h/h<sub>0</sub> and the slope "
    "is the osmotic modulus K = c∂Π/∂c. Dashed line: linear fit to all 12 samples, strain regressed on Π, "
    f"K = {L['K']:.2f} ± {L['sK']:.2f} MPa (95% CI {L['K']-L['ci']:.2f}–{L['K']+L['ci']:.2f}). Grey curve: "
    f"stiffening equation of state K = K<sub>0</sub> + αΠ (K<sub>0</sub> = {S['K0']:.2f} MPa, α = {S['al']:.1f}; "
    f"ΔAICc = {S['dAICc']:+.1f} against the linear fit, so the two are statistically indistinguishable). "
    "<b>(b)</b> The same data against plain relative height h/h<sub>0</sub>. The axis is reversed so compression runs "
    "to the right, as in (a). Dashed: the panel-a fit mapped onto h/h<sub>0</sub>. Dotted: linear fit in engineering "
    f"strain 1 − h/h<sub>0</sub>, K = {E['K']:.2f} ± {E['sK']:.2f} MPa. "
    "<b>(c)</b> The coacervate modulus (black; bar = 95% CI, grey band carried across the panel) compared with "
    "benchmarks from soft matter, log scale. Filled circles: osmotic or confined-compression moduli. The PEG baths "
    "used here are computed from the same Π(w) curve, in the colours of (a). BSA is a Carnahan–Starling hard-sphere "
    "estimate (M = 66.4 kDa; bar spans v<sub>eff</sub> = 1.2–1.5 mL g<sup>−1</sup>). 150 mM NaCl is ideal van ’t Hoff with "
    "K = Π. The cell is treated as a Boyle–van ’t Hoff osmometer at 290 mOsm with an osmotically inactive fraction of "
    "0.2–0.4. Articular cartilage is the equilibrium aggregate modulus in confined compression (range over depth; dot = "
    "full thickness, Schinagl et al. 1997). Synthetic gels: typical osmotic moduli of swollen gels. Open diamonds: "
    "shear moduli, shown for scale only. PEGDA gels are this lab's G′ data (1.5–15 kPa). Complex coacervates are "
    "typical plateau G′ values (Spruijt et al. 2013)."
)

FOCUS = (
    "<b>Focus.</b> Pressing a coacervate layer with PEG is an osmotic-stress experiment. The PEG sets the water "
    "activity, the layer gives up water until its own osmotic pressure matches, and the height change reports how much "
    "volume that took. The figure asks one question: <b>how hard is it to squeeze water out of this coacervate, and is "
    "that hard compared with other soft materials?</b> The answer is K ≈ 1.4 MPa. That is about 1500× softer than liquid "
    "water, so the coacervate is not incompressible. It is nonetheless as stiff as a ~400 g/L protein solution or a "
    "living cell, and 2–4 orders of magnitude stiffer than gels or the coacervate's own shear response."
)

ARC = [
    ("a · Measure the equation of state.",
     "With lateral confinement, height is volume, and −ln(h/h<sub>0</sub>) is the natural compression variable. Its slope "
     "against Π is the thermodynamic osmotic modulus with no geometric correction. Over 0–15% PEG the response is "
     "close to linear (K = 1.44 MPa). The step modulus doubles between 10% and 15%. A stiffening equation of state "
     "fits equally well, so the data are honestly described as a small-strain modulus over a 1.3-fold concentration "
     "window, possibly stiffening toward its end."),
    ("b · Show the result is not an artefact of the log transform.",
     "Plotted against plain h/h<sub>0</sub>, the same points give 1.65 MPa with an engineering-strain fit. The two strain "
     "measures differ by at most 0.04 here, so the choice of axis changes K by about 15%, not its order of magnitude. "
     "Panel b is also the form most readers will check against the raw images."),
    ("c · Calibrate the number.",
     "A modulus means little without a scale. On one log axis the coacervate sits with crowded liquids: about 400 g/L "
     "BSA, a cell under osmotic load, physiological saline, and the stiff end of cartilage. It sits far above swollen "
     "gels and above any shear modulus a coacervate liquid shows. The contrast with shear is the physical point: a "
     "coacervate flows, yet it holds onto its water as tightly as a dense protein phase."),
]
TAKEHOME = (
    "<b>Take-home.</b> K<sub>osm</sub> ≈ 1.4 MPa (1.1–1.8, 95% CI) from 0–15% PEG. The coacervate dehydrates "
    "reversibly and smoothly under osmotic stress, with a compressibility typical of a very concentrated protein or "
    "polyelectrolyte fluid. 20% PEG gives a collapse that this equation of state does not predict, together with wall "
    "climbing. It is reported in the SI but not used for the modulus."
)

SI_LEGEND = (
    "<b>Figure S1 | Relative height h/h<sub>0</sub> of every coacervate layer over 80 h of PEG osmotic stress.</b> "
    "<b>(a–e)</b> Individual samples at 0, 5, 10, 15 and 20% PEG (sample 1 blue circles, sample 2 orange triangles, sample "
    "3 green diamonds). The panel titles give the nominal PEG osmotic pressure. For 20% it is extrapolated (*) from "
    "a Rand-type fit log<sub>10</sub>Π = a + b·w<super>0.21</super> through the 5–15% values. At 20% PEG sample 2 (open "
    "triangles, dotted) stalls at h/h<sub>0</sub> ≈ 0.88, less compressed than any 15% sample, and is excluded. Samples 1 and "
    "3 collapse to h/h<sub>0</sub> ≈ 0.38 while the layer climbs the wall, so height no longer reports volume. "
    "The 20% group is therefore not used for the modulus. <b>(f)</b> Mean ± SD (n = 3) for 0–15% PEG. The 80 h values "
    "are the inputs to Figure 1. Data were digitised from the original per-sample plots (reading error ≈ 0.005). "
    "Values hidden by overlapping markers were solved from the plotted group means."
)


def si_table():
    rows = list(csv.reader(open(os.path.join(HERE, "digitised_trajectories.csv"))))
    head = ["PEG", "Sample"] + [c[1:-1] + " h" for c in rows[0][2:]]
    data = [[Paragraph(h, cellb) for h in head]]
    for r in rows[1:]:
        lab = r[1].replace("S", "")
        if r[0] == "20" and r[1] == "S2":
            lab += " (excl.)"
        data.append([Paragraph(f"{r[0]}%", cell), Paragraph(lab, cell)] +
                    [Paragraph(f"{float(v):.3f}", cell) for v in r[2:]])
    W = 174 * mm
    widths = [13 * mm, 17 * mm] + [(W - 30 * mm) / 9] * 9
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.8, INK), ("LINEBELOW", (0, 0), (-1, 0), 0.5, INK2),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, INK),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f2ee")]),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def img(path, width):
    w, h = PILImage.open(path).size
    return Image(path, width=width, height=width * h / w)


def build(path):
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=15 * mm, bottomMargin=15 * mm, title=TITLE,
                            author="Coacervate osmotic modulus analysis")
    story = [Paragraph(TITLE, h1), Paragraph(SUBTITLE, sub)]
    story.append(img(os.path.join(HERE, "coacervate_osmotic_modulus.png"), 160 * mm))
    story.append(Spacer(1, 4))
    story.append(Paragraph(LEGEND, small))
    story.append(PageBreak())
    story.append(Paragraph("What the figure shows, and how the panels build the argument", h2))
    story.append(Paragraph(FOCUS, body))
    story.append(Paragraph("Logic arc through the panels", h3))
    for head, txt in ARC:
        story.append(Paragraph(f"<b>{head}</b> {txt}", body))
    story.append(Spacer(1, 3))
    story.append(Paragraph(TAKEHOME, body))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Supporting notes: method, fits, linearity, benchmarks and caveats", h2))
    readme = open(os.path.join(HERE, "README.md"), encoding="utf-8").read()
    readme = readme.split("\n", 1)[1]
    readme = readme.split("## Method", 1)[1]          # drop the file/run instructions
    story += md_to_flowables("## Method" + readme)
    story.append(PageBreak())
    story.append(Paragraph("Supplementary Information", h1))
    story.append(img(os.path.join(HERE, "SI_raw_trajectories.png"), 170 * mm))
    story.append(Spacer(1, 4))
    story.append(Paragraph(SI_LEGEND, small))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Table S1 | Digitised h/h<sub>0</sub> for every sample and time point", h3))
    story.append(si_table())

    def footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont("DV", 7); canvas.setFillColor(INK2)
        canvas.drawRightString(A4[0] - 18 * mm, 9 * mm, f"{doc_.page}")
        canvas.drawString(18 * mm, 9 * mm, "PDDA/BSA coacervate · osmotic modulus")
        canvas.restoreState()
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    out = os.path.join(HERE, "coacervate_osmotic_modulus_report.pdf")
    build(out)
    print("wrote", out)

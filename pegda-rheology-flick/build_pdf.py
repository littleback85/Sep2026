"""Build the PDF report: figure + figure legend + focus/logic arc + README notes.

Run after analysis.py:  python3 build_pdf.py  -> pegda_rheology_vs_flick_report.pdf
"""
import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
                                PageBreak, KeepTogether, ListFlowable, ListItem)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
import matplotlib

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


# ---------------------------------------------------------------- page 1-2 text
TITLE = "PEGDA hydrogels: load-bearing strands from rheology, compared with FLICK junction fluctuations"
SUBTITLE = "PEGDA 5K / 10K / 20K · G′ digitised from the Origin G′–Q plots · ρ = 1.12 g cm⁻³, T = 298 K"

LEGEND = [
    "<b>Figure 1 | Rheology and FLICK read the same load-bearing strand, but through different averages.</b> ",
    "<b>(a)</b> Storage modulus G′ against swelling ratio Q for PEGDA 5K (blue squares), 10K (orange circles) and "
    "20K (green triangles), log–log. Solid lines: least-squares fits of G′ = a/Q (exponent fixed at −1) over the "
    "measured range. Dashed lines: extrapolation of those fits to Q = 1. Open symbols: the extrapolated "
    "dry-network modulus a = G′(Q = 1), labelled in kPa. The legend gives the exponent b of an unconstrained fit "
    "G′ = aQ<super>b</super>. "
    "<b>(b)</b> Effective strand mass relative to the precursor, M<sub>c,eff</sub>/M<sub>n</sub> = ρRT/(a·M<sub>n</sub>). "
    "Filled symbols: affine model (f → ∞). Open symbols: phantom model with f = 4. The shaded bar spans the two. "
    "Small dots: the same quantity for each individual sample, ρRT/(G′·Q·M<sub>n</sub>). "
    "ω = M<sub>n</sub>/M<sub>c,eff</sub> is the fraction of PEG chains that carry load (affine). The dashed line marks the "
    "ideal network in which every PEG chain is one load-bearing strand. "
    "<b>(c)</b> All length scales against M<sub>n</sub>, log–log. Violet filled circles: FLICK σ, read as a per-axis "
    "junction displacement. Violet open circles: σ/√3, the value if FLICK σ is a 3-D rms. Diamonds: "
    "unperturbed size R<sub>0</sub> of the effective strand from M<sub>c,eff</sub> (θ statistics, affine). The band around them runs "
    "from phantom-θ to affine-in-water. Grey band: precursor PEG end-to-end distance R<sub>e</sub> (θ to water). "
    "Black bars: rubber-elastic mesh size ξ = (kT/G′)<super>1/3</super>, showing the range across each Q series (tick = median). "
    "Open circles with dashed line: per-axis junction fluctuation that a phantom network (f = 4, θ) predicts from "
    "the same G′. The hatched band runs from f = 10 (θ) to f = 3 (in water), which is the largest the model allows. "
    "<b>(d)</b> FLICK variance σ² against the rheological M<sub>c,eff</sub> (affine). Horizontal bars show the fit standard "
    "error. Violet line: σ² = σ<sub>0</sub>² + α·M<sub>c,eff</sub>. Dotted line: the strand-independent floor σ<sub>0</sub>². "
    "Grey lines: phantom predictions through the origin (solid f = 3, dashed f = 4). "
    "H = (σ<sub>FLICK</sub>/σ<sub>phantom, f=4</sub>)² is given as a range from water to θ strand statistics.",
]

FOCUS = (
    "<b>Focus.</b> PEGDA networks have no controlled junction functionality f and contain loops, dangling chains "
    "and dense poly(acrylate) clusters. So the question is not the ‘true’ strand length. It is whether a macroscopic "
    "measurement (G′) and a microscopic one (FLICK junction fluctuation) describe the same <i>effective, load-bearing</i> "
    "strand, and what their disagreement means. The figure argues that <b>both report the same effective strand and "
    "agree on how it changes with M<sub>n</sub>, but differ 3–4× in magnitude</b>. That difference is expected when "
    "one method averages stiffness and the other averages compliance, so it measures network heterogeneity."
)

ARC = [
    ("a · Establish the input.",
     "Within each molecular weight G′ falls roughly as 1/Q. Extrapolating to Q = 1 gives a dry-network modulus a "
     "for each gel. The panel is honest about the leverage: the extrapolation reaches 10–30× beyond the data. It also "
     "shows that the 20K series is the weakest (R² = 0.63)."),
    ("b · Turn the modulus into network meaning.",
     "a converts to an effective strand mass. The load-bearing strand is 1–3.5 PEG chains long, so only about "
     "30–50 % (affine) to 60–95 % (phantom) of PEG chains carry load. The network is least defective at 20K. The "
     "affine–phantom bar is the unavoidable model bracket when f is unknown. Every later number inherits it."),
    ("c · Put every length on one axis and expose the mismatch.",
     "Once the precursor size, effective strand size, mesh size, predicted junction fluctuation and FLICK σ "
     "share one axis, the key fact is visible. The phantom model, fed the same G′, predicts junction fluctuations "
     "of 3–7 nm. FLICK measures 12.6–16 nm, which is 2.5–4.3× larger even at the model's upper limit. The Mn "
     "scaling is informative too. FLICK (Mn<super>0.18</super>) follows the mesh size (Mn<super>0.22</super>), not the "
     "precursor chain (Mn<super>0.5–0.58</super>)."),
    ("d · Resolve the mismatch.",
     "Plotted against the rheological M<sub>c,eff</sub>, FLICK σ² falls on a straight line (R² = 0.993; 0.92 against "
     "M<sub>n</sub>). So FLICK responds to the same effective strand that G′ counts: the two agree on the trend. The "
     "line has two parts. A strand-independent floor σ<sub>0</sub> ≈ 9.5 nm, and a slope about 7× the phantom value: "
     "the two disagree on magnitude. A modulus is a stiffness average ⟨k⟩ dominated by the percolating backbone. A "
     "fluctuation is a compliance average ⟨1/k⟩ dominated by loosely tethered junctions. Since ⟨k⟩⟨1/k⟩ ≥ 1 for any "
     "heterogeneous network, H = (σ<sub>FLICK</sub>/σ<sub>phantom</sub>)² works as a heterogeneity index "
     "(5K 10–18, 10K 8–14, 20K 6–12). The Mn trend in H depends on what σ<sub>0</sub> is. Measuring the FLICK "
     "localisation floor on an immobilised reference settles it."),
]
TAKEHOME = (
    "<b>Take-home.</b> Rheology: the average load-bearing strand is 1–3.5 PEG chains. FLICK: junctions move as if held "
    "by strands roughly 3–9× longer, so most tracked junctions sit in softer-than-average surroundings. The gap "
    "between the two methods is a measure of network heterogeneity, not a contradiction."
)


def build(path):
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=15 * mm, bottomMargin=15 * mm, title=TITLE,
                            author="PEGDA rheology vs FLICK analysis")
    story = [Paragraph(TITLE, h1), Paragraph(SUBTITLE, sub)]
    img = os.path.join(HERE, "pegda_rheology_vs_flick.png")
    w = 162 * mm
    story.append(Image(img, width=w, height=w * 2190 / 2220))
    story.append(Spacer(1, 4))
    story.append(Paragraph("".join(LEGEND), small))
    story.append(PageBreak())
    story.append(Paragraph("What the figure shows, and how the panels build the argument", h2))
    story.append(Paragraph(FOCUS, body))
    story.append(Paragraph("Logic arc through the panels", h3))
    for head, txt in ARC:
        story.append(Paragraph(f"<b>{head}</b> {txt}", body))
    story.append(Spacer(1, 3))
    story.append(Paragraph(TAKEHOME, body))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Supporting notes: equations, results, caveats and next steps", h2))
    readme = open(os.path.join(HERE, "README.md"), encoding="utf-8").read()
    readme = readme.split("\n", 1)[1]            # drop the README's H1 title (already on page 1)
    story += md_to_flowables(readme)

    def footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont("DV", 7); canvas.setFillColor(INK2)
        canvas.drawRightString(A4[0] - 18 * mm, 9 * mm, f"{doc_.page}")
        canvas.drawString(18 * mm, 9 * mm, "PEGDA rheology vs FLICK")
        canvas.restoreState()
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    out = os.path.join(HERE, "pegda_rheology_vs_flick_report.pdf")
    build(out)
    print("wrote", out)

"""Build the single-file PDF report: assessment, key message and logic arc, both figures (embedded as
vector pages), captions, panel-by-panel guides, models, field design, plan, journal fit and references."""
import os

from fontTools.ttLib import TTFont as FTFont
from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (CondPageBreak, Flowable, KeepTogether, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
REPORT = os.path.join(OUT, "ice_microplastics_nature_water_report.pdf")
DRAFT = os.path.join(OUT, "_report_text_only.pdf")
FIGS = {"fig1": os.path.join(OUT, "fig1_current_spine.pdf"), "fig2": os.path.join(OUT, "fig2_roadmap.pdf")}

LIB = "/usr/share/fonts/truetype/liberation/LiberationSans-{}.ttf"
pdfmetrics.registerFont(TTFont("Sans", LIB.format("Regular")))
pdfmetrics.registerFont(TTFont("Sans-Bold", LIB.format("Bold")))
pdfmetrics.registerFont(TTFont("Sans-Italic", LIB.format("Italic")))
pdfmetrics.registerFont(TTFont("Sans-BoldItalic", LIB.format("BoldItalic")))
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-Bold", italic="Sans-Italic",
                              boldItalic="Sans-BoldItalic")
pdfmetrics.registerFont(TTFont("CJK", "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", subfontIndex=0))

BLUE = colors.HexColor("#0072B2")
NAVY = colors.HexColor("#1B2A41")
GREY = colors.HexColor("#666666")
RULE = colors.HexColor("#BFBFBF")
TINT = colors.HexColor("#EEF5FB")
HEAD = colors.HexColor("#E8EDF2")
WARN = colors.HexColor("#FBEFE6")

PAGE_W, PAGE_H = A4
LM = RM = 18 * mm
TM, BM = 17 * mm, 17 * mm
TEXT_W = PAGE_W - LM - RM

S = {
    "title": ParagraphStyle("title", fontName="Sans-Bold", fontSize=17, leading=21, textColor=NAVY,
                            spaceAfter=4),
    "sub": ParagraphStyle("sub", fontName="Sans", fontSize=10, leading=13.5, textColor=GREY, spaceAfter=10),
    "h1": ParagraphStyle("h1", fontName="Sans-Bold", fontSize=13, leading=16, textColor=NAVY, spaceBefore=10,
                         spaceAfter=5),
    "h2": ParagraphStyle("h2", fontName="Sans-Bold", fontSize=10.5, leading=13.5, textColor=BLUE,
                         spaceBefore=8, spaceAfter=3),
    "body": ParagraphStyle("body", fontName="Sans", fontSize=9.3, leading=12.8, spaceAfter=5, alignment=TA_LEFT),
    "bullet": ParagraphStyle("bullet", fontName="Sans", fontSize=9.3, leading=12.6, leftIndent=11,
                             bulletIndent=2, spaceAfter=2.5),
    "cell": ParagraphStyle("cell", fontName="Sans", fontSize=7.9, leading=10.0),
    "cellb": ParagraphStyle("cellb", fontName="Sans-Bold", fontSize=7.9, leading=10.0),
    "cap": ParagraphStyle("cap", fontName="Sans", fontSize=8.2, leading=10.9, spaceAfter=3.5),
    "small": ParagraphStyle("small", fontName="Sans", fontSize=7.8, leading=10.2, textColor=GREY, spaceAfter=3),
    "box": ParagraphStyle("box", fontName="Sans", fontSize=9.3, leading=12.8, spaceAfter=3),
    "ref": ParagraphStyle("ref", fontName="Sans", fontSize=7.9, leading=10.3, leftIndent=12, firstLineIndent=-12,
                          spaceAfter=2),
}
ALL_TEXT = []   # for the glyph-coverage check


def P(text, style="body"):
    ALL_TEXT.append(text)
    return Paragraph(text, S[style])


def bullets(items, style="bullet"):
    ALL_TEXT.extend(items)
    return [Paragraph(t, S[style], bulletText="•") for t in items]


def box(flowables, bg=TINT, edge=BLUE):
    t = Table([[flowables]], colWidths=[TEXT_W])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg), ("BOX", (0, 0), (-1, -1), 0.6, edge),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return t


def table(rows, widths_mm, header=True, zebra=False, first_col_bold=True):
    data = []
    for i, r in enumerate(rows):
        out = []
        for j, cval in enumerate(r):
            ALL_TEXT.append(cval)
            st = "cellb" if (header and i == 0) or (first_col_bold and j == 0) else "cell"
            out.append(Paragraph(cval, S[st]))
        data.append(out)
    t = Table(data, colWidths=[w * mm for w in widths_mm], repeatRows=1 if header else 0)
    style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.35, RULE),
             ("LEFTPADDING", (0, 0), (-1, -1), 3.5), ("RIGHTPADDING", (0, 0), (-1, -1), 3.5),
             ("TOPPADDING", (0, 0), (-1, -1), 2.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6)]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), HEAD), ("LINEBELOW", (0, 0), (-1, 0), 0.6, NAVY)]
    t.setStyle(TableStyle(style))
    return t


class FigSlot(Flowable):
    """Reserves space for a vector figure page; records where it lands so pypdf can overlay it."""
    slots = []

    def __init__(self, key, width, height):
        super().__init__()
        self.key, self.width, self.height = key, width, height

    def wrap(self, aw, ah):
        return self.width, self.height

    def draw(self):
        x, y = self.canv.absolutePosition(0, 0)
        FigSlot.slots.append((self.canv.getPageNumber(), self.key, x, y, self.width, self.height))


def fig_slot(key):
    w_pt, h_pt = [float(v) for v in PdfReader(FIGS[key]).pages[0].mediabox[2:]]
    w = TEXT_W
    return FigSlot(key, w, w * h_pt / w_pt)


def footer(canv, doc):
    canv.saveState()
    canv.setFont("Sans", 7.5)
    canv.setFillColor(GREY)
    canv.drawString(LM, 10 * mm, "Ice-driven microplastic oxidation · editorial assessment and figure plan")
    canv.drawRightString(PAGE_W - RM, 10 * mm, f"{doc.page}")
    canv.restoreState()


sup = lambda s: f"<super>{s}</super>"
sub = lambda s: f"<sub>{s}</sub>"
O2s = f"{sup('1')}O{sub('2')}"          # singlet oxygen
O2 = f"O{sub('2')}"
story = []

# =====================================================================================================
story += [
    P("Ice-driven microplastic oxidation", "title"),
    P("Editorial assessment, key message, logic arc and a two-figure plan toward <i>Nature Water</i><br/>"
      "Source: 5-page figure deck dated 23 October 2026 · prepared 28 October 2026", "sub"),
]
story.append(box([
    P("<b>Bottom line</b>", "box"),
    *bullets([
        "One idea in the deck is genuinely new and Nature-family material: <b>the plastic reshapes the ice "
        "that oxidizes it</b>. Oxidized microplastics (MPs) refine the ice grain structure, and the finer "
        "structure is proposed to speed up further oxidation.",
        "As it stands the deck would not clear a picky <i>Nature Water</i> editor. The oxidant source "
        f"(freeze-made nanobubbles → {O2s}) is the weakest link. The \"positive feedback\" is shown only by "
        "correlation, and the deck's own decelerating kinetics argue against it. Relevance to natural ice "
        "and water is absent.",
        "What changes that: (i) a discrimination package that rules out four rival ROS sources "
        "(Fig. 2a–c); (ii) a causal, bounded test of the feedback (Fig. 2d–f); (iii) a "
        f"{sup('13')}C carbon budget (Fig. 2g); (iv) a controlled field deployment with meltwater sampling "
        "(Fig. 2h–j).",
        "Realistic targets today: <i>Angew. Chem.</i> or <i>Nat. Commun.</i> after (i)–(ii). <i>Nature "
        "Water</i> only with (iii)–(iv). A presubmission enquiry built around the feedback concept costs "
        "little and tests editorial interest.",
    ]),
]))
story.append(Spacer(1, 4))
story.append(P("How to read this report. <b>Fig. 1</b> replots the deck's own data, digitized from the PDF "
               "(reading error ±2–5%). <b>Fig. 2</b> shows the <b>expected</b> outcomes of experiments not "
               "yet done; every curve comes from a stated model (Section 5.3). Those panels are predictions "
               "to design against, not results, and must never be presented as data.", "small"))

# ----------------------------------------------------------------------------------------------------- 1
story.append(P("1  Key message and logic arc", "h1"))
story.append(P("1.1  Key message (as the paper should read)", "h2"))
story.append(box([
    P("Freezing turns ice grain boundaries into self-reinforcing oxidation reactors for microplastics. Gas "
      "expelled by growing ice nucleates nanobubbles on hydrophobic plastic surfaces, where they deliver "
      "reactive oxygen. The oxidized, now hydrophilic plastics inhibit ice recrystallization, so each refreeze "
      "gives finer ice with more boundary and more bubbles. Freeze–thaw cycling therefore ratchets "
      "microplastics toward chain scission, and spring melt flushes the products into surface waters.", "box"),
    Paragraph('<font name="CJK">冰晶界是微塑料的“自增强氧化反应器”：结冰排出的气体在疏水塑料表面形成纳米气泡并输送活性氧；'
              '氧化后变亲水的微塑料抑制冰重结晶，使再结冰的晶粒更细、晶界与气泡更多；冻融循环由此以棘轮方式推动'
              '微塑料断链降解，融雪再把产物带入地表水。</font>', S["box"]),
]))
story.append(P("Framing by journal: for <i>Nature Water</i> lead with the water-systems consequence (what "
               "seasonal ice does to plastics, and what meltwater delivers). For <i>Nat. Commun.</i>, "
               "<i>JACS</i> or <i>Angew.</i> lead with the mechanism (ice microstructure ↔ interfacial "
               "chemistry coupling)."))

story.append(P("1.2  Logic spine, with evidence status today", "h2"))
story.append(table([
    ["Step", "Claim", "Deck evidence", "Status", "Closes the gap"],
    ["S1", "Ice, not water, oxidizes C–H polymers; PTFE inert", "p1B: XPS O/C, 9 polymers",
     "Supported for PE, PP, PS, PVC; O-containing polymers ambiguous",
     "ΔO/C vs pristine, C1s fitting, FTIR carbonyl index; drop PVA"],
    ["S2", "Freezing exsolves gas into nanobubbles that generate ROS", "p2: NTA, DCFH, TEMP–EPR, imaging",
     "<b>Unproven</b>: bubble identity and ROS species", "Fig. 2a, 2b, 2c"],
    ["S3", "Bubbles meet MPs at grain boundaries; only touching bubbles act", "p3: Raman, confocal, size series",
     "Partial: co-location is expected from freeze exclusion", f"Fig. 2c; cryo-SEM, NanoSIMS {sup('18')}O"],
    ["S4", "Oxidized MPs refine ice → more bubbles → faster oxidation", "p1C, p4",
     "Correlational; kinetics decelerate", "Fig. 2d, 2e, 2f"],
    ["S5", "Chain scission to small molecules", "p5: GPC, 13C NMR, GC-MS", "Partial: PS only; no mass balance",
     "Fig. 2g"],
    ["S6", "Operates in natural ice and reaches water", "—", "<b>Missing</b>", "Fig. 2h, 2i, 2j"],
], [10, 44, 33, 45, 42]))

story.append(P("1.3  How the two planning figures map onto an eventual five-figure manuscript", "h2"))
story.append(table([
    ["Main figure", "Purpose", "Built from"],
    ["1  Phenomenon and concept", "Ice oxidizes C–H polymers, water does not; the ratchet idea",
     "Fig. 1a, 1c (cleaned O/C), 1h"],
    ["2  The oxidant", "What makes the ROS, and is it really a bubble", "Fig. 2a–c plus species probes"],
    ["3  The feedback", "Causal test, ratchet signature, bound at realistic loadings", "Fig. 1f–g, 2d–f"],
    ["4  Fate", f"Chain scission, products, {sup('13')}C budget, nanoplastic release", "Fig. 1i, 2g"],
    ["5  Natural ice and water", "Field dose–response and meltwater first flush", "Fig. 2h–j"],
], [42, 82, 50]))

# ----------------------------------------------------------------------------------------------------- 2
story.append(P("2  True novelty and physics insight", "h1"))
story.append(P("2.1  Not new (reviewers will know these)", "h2"))
story += bullets([
    "Ice accelerates oxidation of PS particles at −20 °C, assigned to " + O2s + " in the liquid layer "
    "between ice crystals: Tian et al., <i>Angew. Chem.</i> 2022.",
    "Freezing generates bulk nanobubbles; size and number depend on cooling rate and dissolved gas: "
    "Qi et al., <i>Langmuir</i> 2023.",
    f"Freeze–thaw cycles oxidize MPs in cold soils via {O2s} and H{sub('2')}O{sub('2')}; in the field only "
    "aromatic polymers oxidized, with no " + O2s + " for PE or PA: <i>ES&amp;T</i> 2025.",
    "Freeze-concentration accelerates reactions in ice (e.g., nitrite oxidation, Takenaka et al., "
    "<i>Nature</i> 1992).",
])
story.append(P("2.2  New", "h2"))
story += bullets([
    "<b>Two-way coupling between pollutant chemistry and ice microstructure.</b> Oxidized MPs act like "
    "ice-recrystallization inhibitors. This parallels graphene oxide, whose IRI activity depends on its "
    "oxidation degree, and it builds on the group's own IRI expertise (He et al., <i>Acc. Chem. Res.</i> "
    "2018). This is the contribution to lead with.",
    "<b>A polymer-independent ROS source.</b> If ROS appear in ice with no plastic present (deck p2D/E "
    "suggests so), the Angew mechanism, where the excited polymer is the sensitizer, is falsified. This is the "
    "cleanest differentiator. Show it with data; do not assert that the Angew EPR was wrong.",
    "<b>Molecular-level degradation evidence</b> (Mw drop, products). This goes beyond Qian et al. "
    "(<i>Nature</i> 2026: ROS and biological effects, not polymer breakdown). It does not exceed Gao et al. "
    "(<i>Nature</i> 2026: quantified diacid yields from molten plastic–water microdroplets).",
])
story.append(P("2.3  Physics the paper should make explicit", "h2"))
story += bullets([
    "<b>Gas exsolution and heterogeneous nucleation.</b> Ice rejects dissolved gas, so veins become "
    "supersaturated, and hydrophobic MPs lower the bubble-nucleation barrier. This gives a physical reason "
    "for bubble–MP contact beyond co-exclusion. Note that the measured size trend (O/C rising from 100 nm to "
    "10 µm) is the opposite of ice-front engulfment theory and needs explaining.",
    f"<b>Nanobubbles are reaction sites, not O{sub('2')} reservoirs.</b> Inside a 130 nm bubble the pressure "
    f"is ≈23 bar, so local O{sub('2')} is ≈0.2 M. But 3×10{sup('8')} bubbles mL{sup('−1')} hold only "
    f"≈10{sup('−7')} M O{sub('2')} in total, about 10{sup('−4')} of the dissolved O{sub('2')}. The paper must "
    f"say what turns the bubbles over and what supplies the 0.98 eV needed to make {O2s}.",
    f"<b>The light problem.</b> The schematic says \"light\" converts {sup('3')}O{sub('2')} to {O2s}, but a "
    "−20 °C freezer is dark and ground-state O" + sub("2") + " barely absorbs (spin-forbidden). Run dark and "
    "defined-light controls. If light is required, this becomes ice photochemistry, which has a large prior "
    "literature on sensitizers concentrated in liquid-like regions.",
    f"<b>{O2s} chemistry.</b> {O2s} reacts by ene, [4+2] and heteroatom oxidation. It does not abstract H "
    "from saturated C–H at meaningful rates, so PE/PP oxidation needs •OH or radical chemistry. "
    "The Fig. 5A mechanism in the deck has this problem.",
    f"<b>Diffusion length.</b> {O2s} lives ≈3.5 µs in water and travels ≈150 nm, a quantitative reason why "
    "only touching bubbles matter (Fig. 1a).",
    "<b>Hidden negative feedback.</b> Oxidation hydrophilizes the surface, which should reduce bubble "
    "nucleation and plastic–water interfacial ROS (Qian et al. show these scale with hydrophobicity). This can "
    "explain the levelling-off kinetics (Fig. 1h) and is one of the three outcomes tested in Fig. 2e.",
    "<b>Zener bound.</b> Particle pinning limits grain size to d = 4r/3f. Holding 20–200 µm grains needs MP "
    "volume fractions of 10" + sup("−3") + "–10" + sup("−2") + "; natural ice is ≤10" + sup("−7") +
    " (Fig. 2f). Any field-relevant feedback must therefore act through something more potent, such as "
    "dissolved oxidized oligomers acting like PVA.",
    "<b>Where bubbles live.</b> Boundary area scales as d" + sup("−1") + " and triple-junction length as d" +
    sup("−2") + "; the deck's data scale as d" + sup("−0.6") + " with a step near 100 µm (Fig. 1g).",
    "<b>Liquid fraction at −20 °C is set by solutes.</b> In near-pure water the veins are nanometre-scale "
    "premelted films that cannot host 130 nm bubbles or 10 µm particles. State the composition and compute "
    "the liquid fraction from the phase diagram.",
])

# ----------------------------------------------------------------------------------------------------- 3
story.append(P("3  Where the work stands in the field", "h1"))
story.append(P("The work sits where two literatures meet. One is interfacial ROS chemistry, which is hot "
               "and contested: plastic–water (Qian, <i>Nature</i> 2026), oil–water (Gao, <i>Nature</i> 2026; "
               "<i>JACS</i> 2026) and air–water. At the air–water interface spontaneous H" + sub("2") + "O" +
               sub("2") + " is disputed, bulk nanobubbles themselves are contested, and whether they make "
               "•OH at all is doubtful. The other is freeze-accelerated chemistry, which is mature, alongside "
               "a crowded microplastic-fate field. Because the proposed mechanism takes on the controversy "
               "from both sides, the bar for proof is high."))
story.append(P("3.1  Rival ROS sources the paper must rule out", "h2"))
story.append(table([
    ["", "Hypothesis", "What makes the ROS", "Discriminating test (Fig. 2a)"],
    ["H1", "Polymer photosensitizer (Tian, <i>Angew.</i> 2022)", "Excited polymer + O" + sub("2"),
     "ROS in ice with no plastic; PE vs PS rates; dark"],
    ["H2", "Freezing (Workman–Reynolds) potential (Song, <i>ES&amp;T</i> 2024)", "Ice–liquid interface field",
     "Salt identity and concentration series"],
    ["H3", "Plastic–water interface •OH, freeze-concentrated (Qian, <i>Nature</i> 2026)",
     "Hydrophobic plastic surface", "•OH probes; TBA; no plastic"],
    ["H4", "Freeze-exsolved nanobubbles (this deck)", "Gas–water interface",
     "O" + sub("2") + " only, no N" + sub("2") + " (fewer bubbles, same pO" + sub("2") + "); pressure; D" +
     sub("2") + "O"],
    ["H5", "Contact electrification (PFA freeze–thaw H" + sub("2") + "O" + sub("2") + ", 2026)",
     "Vial or particle contact", "Glass vs PFA vs PP vials; TBA"],
], [9, 62, 40, 63]))
story.append(P("3.2  Performance against peers", "h2"))
story.append(table([
    ["Work", "Conditions", "Headline result", "Depth of evidence"],
    ["This deck", "−20 °C, ~350 h, 9 polymers",
     "PS O/C 0.015 → ~0.2; PS Mw −52%; PE/PP/PVC Mw −7 to −18%; ~85% of products are 2-carbon",
     "XPS, GPC, 13C NMR, GC-MS; no mass balance"],
    ["Tian, <i>Angew.</i> 2022", "−20 °C ice, PS", "\"Competitive with most artificial technologies\"; "
     "reviews cite ~12 d (one review 48 d) for 500 nm PS", "Abstract only checked"],
    ["Fe(II)/frozen, <i>Env. Sci. Nano</i> 2023", "Anoxic Fe(II), frozen", "14.6× faster than water; Fe(IV), •OH",
     "Mechanistic"],
    ["<i>ES&amp;T</i> 2025, cold soils", "122-day field + lab", "Only aromatic MPs oxidized", "Field validation"],
    ["Qian, <i>Nature</i> 2026", "Dark, room temperature", "•OH ≥0.1–1 nM min" + sup("−1") +
     "; methyl orange ~90% in 10 d", "ROS + biology; no polymer breakdown"],
    ["Gao, <i>Nature</i> 2026", "Molten plastic in water", "~69% diacid yield from PE/PP", "Quantified yields"],
], [36, 34, 62, 42]))
story.append(P("Verdict: no rate advantage over Angew 2022 (weeks at −20 °C). The deck wins on breadth and "
               "molecular evidence, but its \"all C–H polymers\" claim conflicts with the field result for "
               "PE. As a treatment technology it is far behind. Sell the mechanism and the feedback, not the "
               "performance.", "small"))

# ----------------------------------------------------------------------------------------------------- 4
story.append(PageBreak())
story.append(P("4  Figure 1 | The story as it stands", "h1"))
story.append(P("<b>Logic arc.</b> State the mechanism (a). List the five claims it rests on and rate the "
               "evidence for each (b). Give one panel of the deck's own data per claim (c–i), so a reader sees "
               "exactly where the chain is strong and where it breaks. S-tags and Harvey balls in each panel "
               "repeat the spine.", "small"))
story.append(fig_slot("fig1"))
story.append(Spacer(1, 3))
cap1 = [
    "<b>Figure 1 | The story as it stands (deck data, digitized).</b> <b>a</b>, Proposed mechanism. Left: "
    "coarse ice with pristine MPs and a few nanobubbles at grain boundaries (S2). Centre: close-up of one "
    "liquid vein. Bubbles touching an MP deliver ROS and oxidize its surface (–OH, C=O). A bubble further away "
    f"than the {O2s} diffusion length (≈150 nm) cannot reach it (S3). Chain scission releases small molecules "
    "(S5). Right: oxidized MPs inhibit recrystallization, giving finer ice (S4). Blue arrow: the proposed "
    "feedback. <b>b</b>, Logic spine. Harvey balls: full = supported, half = partial or correlational, "
    "empty = unproven or missing. Arrows point to the panel that carries each step.",
    "<b>c</b>, S1: XPS O/C after incubation in water (20 °C) or ice (−20 °C); black bars, stoichiometric O/C "
    "of the repeat unit. †PVA is water-soluble and a known ice-recrystallization inhibitor. <b>d</b>, S2: "
    "nanobubble count (NTA) through three freeze–melt cycles; shading = frozen. <b>e</b>, S3: O/C against "
    "PS diameter. <b>f</b>, S4, first link: ice grain size against O/C of embedded PS. <b>g</b>, S4, second "
    "link: bubble density against grain size; grey lines, d" + sup("−1") + " (boundary area) and d" +
    sup("−2") + " (triple junctions); blue, log–log fit. <b>h</b>, S4 kinetics: PS O/C at −20 °C with "
    "melt–refreeze at 72 h and 217 h (dotted lines). <b>i</b>, S5: change in Mw; grey band ±10% (assumed "
    "typical GPC run-to-run reproducibility). Values digitized from the deck (±2–5%); error bars as drawn in "
    "the deck.",
]
story += [P(t, "cap") for t in cap1]

story.append(CondPageBreak(60 * mm))
story.append(P("4.1  What each panel means and how it serves the arc", "h2"))
story.append(table([
    ["Panel", "What it shows", "Role in the arc", "Editor's reading"],
    ["a", "Mechanism schematic: coarse ice → close-up of one vein → finer ice, with the feedback arrow",
     "The key message in one picture; defines S2–S5", "Shows the claim, not the evidence; the light-driven "
     + O2s + " step is drawn but undemonstrated"],
    ["b", "Logic spine S1–S6 with Harvey balls", "Tells the reader which links hold", "Only S1 is solid; S2 and "
     "S6 are empty"],
    ["c", "O/C in water vs ice for 9 polymers, with stoichiometric O/C", "S1, the phenomenon",
     "PE, PP, PS, PVC show real oxidation. For PA, PMMA and PET the ice values equal the formula O/C, so the "
     "\"increase\" may be loss of adventitious carbon; PVA should be dropped"],
    ["d", "Bubble count reversibly high when frozen, ~0 after melting", "S2, that bubbles form",
     "Reproducible, but NTA cannot tell bubbles from nanoplastic fragments; nothing here shows ROS"],
    ["e", "O/C rises with PS size and saturates above 1 µm", "S3, that contact matters",
     "Counter to engulfment theory and far shallower than a per-particle nucleation model; needs physics"],
    ["f", "Grain size falls from ~65 to ~20 µm as O/C rises to 0.21", "S4, first link (oxidation → ice)",
     "Cleanest panel for the new idea; still needs causality (Fig. 2d)"],
    ["g", "Bubble density vs grain size, log–log, with geometric scalings", "S4, second link (ice → bubbles)",
     "Follows neither scaling (slope −0.6, step near 100 µm): location of bubbles unresolved"],
    ["h", "Oxidation kinetics with two melt–refreezes", "S4, third link (bubbles → rate)",
     "Every curve slows and levels off; refreeze bumps fit re-oxygenation as well as feedback"],
    ["i", "Mw change for PS, PE, PP, PVC", "S5, degradation", "Only PS (−52%) exceeds plausible GPC error; "
     "surface-limited O/C vs bulk Mw halving must be reconciled"],
], [11, 50, 40, 73]))
story.append(P("<b>Left out of Fig. 1, on purpose:</b> fluorescence ROS images (DCF and Rh-6G both "
               "freeze-concentrate into veins, so co-localization is expected whatever the mechanism); the "
               "TEMP–EPR trace (non-specific without D" + sub("2") + "O and azide controls); SEM images; the "
               "3-point O/C vs bubble plot (2.9–3.1×10" + sup("8") + " mL" + sup("−1") + ", within NTA "
               "precision). Their replacements are in Fig. 2.", "small"))

# ----------------------------------------------------------------------------------------------------- 5
story.append(PageBreak())
story.append(P("5  Figure 2 | What would make it a <i>Nature Water</i> paper", "h1"))
story.append(P("<b>Logic arc.</b> (1) Pin down the oxidant: a–c. (2) Prove the feedback and bound it: d–f. "
               "(3) Follow the carbon: g. (4) Show it in natural ice and meltwater: h–j. Every data panel is a "
               "<b>simulated expectation</b>; each one states the result that supports the story and the "
               "result that would falsify it.", "small"))
story.append(fig_slot("fig2"))
story.append(Spacer(1, 3))
cap2 = [
    "<b>Figure 2 | Decisive experiments and their expected outcomes (simulated).</b> <b>a</b>, "
    "Discrimination matrix: five candidate ROS sources against seven manipulations; readout, ROS-probe yield "
    "and PS oxidation rate at −20 °C. Each column has a unique signature. H4 is drawn as in the deck "
    "(light-driven); if it runs in the dark, the \"Dark\" cell becomes ○. <b>b</b>, Resonant-mass "
    "(Archimedes) test: an air bubble has negative buoyant mass (130 nm, −1.15 fg), an oxidized PS "
    "fragment positive (300 nm, +1.1 fg); a pressure pulse removes bubbles only. <b>c</b>, Oxidation rate "
    "against bubble density at fixed pO" + sub("2") + " (1 MPa freezing; O" + sub("2") + " only, no N" +
    sub("2") + "; air; O" + sub("2") + " + Ar); grey band, the deck's 7% range; n = 3, mean ± s.d.",
    "<b>d</b>, Initial oxidation rate of fresh h-PS against grain-boundary density S" + sub("v") +
    " = 2/d, with grain size set by annealing or by pre-oxidized, hydroperoxide-reduced PS-d8 spectators. "
    "Collapse on one curve means the feedback is set by the ice; spectators above the curve point to ROOH "
    "chemistry. <b>e</b>, Ratchet test: per-cycle rate constant normalized to remaining sites, k" + sub("n") +
    "/k" + sub("1") + ", over 10 freeze–thaw cycles at fixed O" + sub("2") + ", with three outcomes. "
    "<b>f</b>, Zener-limited grain size d = 4r/3f against MP volume fraction; bands: natural ice/snow "
    "(dark), typical lab dosing (light), deck grain sizes (blue). <b>g</b>, " + sup("13") + "C budget "
    "(illustrative magnitudes): nanoplastics, " + sup("13") + "C-DOC and " + sup("13") + "CO" + sub("2") +
    " against freeze–thaw cycles; dashed, water control.",
    "<b>h</b>, Field design: elevation transect bracketing freeze–thaw exposure; a cassette trio of reference "
    "MPs at each station (exposed, dark, unfrozen +2 °C); loggers; a snow/firn pit; a lysimeter; a lab twin "
    "that replays the logged record. Red ×: why one summit sample measured over time is not enough. "
    "<b>i</b>, Expected ΔO/C of dark cassettes against cumulative field freeze–thaw cycles; markers = station. "
    "<b>j</b>, Meltwater first flush: concentration factor against fraction of snowpack melted. Model "
    "details in Section 5.3; scripts in <font name=\"Sans-Italic\">simulate_expectations.py</font>.",
]
story += [P(t, "cap") for t in cap2]

story.append(CondPageBreak(60 * mm))
story.append(P("5.1  What each panel means and how it serves the arc", "h2"))
story.append(table([
    ["Panel", "Experiment", "Supports the story if…", "Falsifies or reframes if…"],
    ["a", "Seven manipulations × five ROS sources", "The response pattern matches column H4",
     "Another column fits; rewrite the mechanism around it (H3 is still a publishable story)"],
    ["b", "Buoyant-mass sign of the frozen-then-melted population", "Negative-mass population that a pressure "
     "pulse removes", "Mostly positive mass: the \"bubbles\" are particles or nanoplastics"],
    ["c", "Bubble number varied 15× at fixed dissolved O" + sub("2"), "Rate rises in proportion to bubbles",
     "Flat rate: drop nanobubbles as the oxidant"],
    ["d", "Grain size set without changing the chemistry", "Both series collapse on one curve, rate ~ S" + sub("v") +
     sup("0.61"), "Spectators sit above the curve: ROOH autocatalysis, not ice structure"],
    ["e", "10 cycles, fixed O" + sub("2") + ", fixed period", "k" + sub("n") + "/k" + sub("1") + " rises "
     "(≈2× by cycle 6)", "Flat: re-oxygenation ratchet. Falling: self-passivation. Retitle away from "
     "\"positive feedback\""],
    ["f", "Calculation, plus refreeze of particle-free filtrate", "Refinement persists at ≤10" + sup("−5") +
     " via dissolved oligomers", "Refinement needs ≥10" + sup("−3") + ": restrict the feedback claim to "
     "high-loading hotspots"],
    ["g", sup("13") + "C-PS mass balance", "Fragments and DOC dominate, mineralization <0.5%: "
     "\"transformation\" framing", "Negligible mobile carbon: the degradation claim weakens to surface aging"],
    ["h", "Controlled field deployment", "—", "—"],
    ["i", "Dark-cassette ΔO/C vs field freeze–thaw count", "All stations on one curve; unfrozen controls flat; "
     "PE above zero", "Station-specific curves: elevation or UV, not freeze–thaw, controls it"],
    ["j", "Lysimeter or snow-column melt fractions", "Products track the chloride ionic pulse",
     "No early enrichment: products are not grain-boundary-held"],
], [11, 47, 56, 60]))

story.append(P("5.2  Why these panels and not others", "h2"))
story += bullets([
    "Each Fig. 2 panel answers one of the referee's foreseeable objections to Fig. 1 (Section 9), in the "
    "order a referee would raise them: is it a bubble, is it the oxidant, is the loop real, does it survive "
    "real loadings, where does the carbon go, does it happen outdoors.",
    "Species probes (FFA, terephthalate, coumarin, DMPO, " + sup("18") + "O" + sub("2") + ") are folded "
    "into the matrix rather than given their own panels. " + sup("18") + "O labelling alone does not "
    "separate the routes, because both deliver most carbonyl oxygen from O" + sub("2") + " via autoxidation.",
    "Temperature (−2 to −20 °C) and matrix (brine, snowmelt, DOM) series belong in the SI. They are "
    "essential, but their outcome cannot be predicted well enough to plot honestly.",
    "Ice-binding proteins and PVA are excluded as grain-size controls because they quench ROS.",
])

story.append(P("5.3  Models and parameters behind the simulated panels", "h2"))
story.append(table([
    ["Panel", "Model", "Parameters (anchors)"],
    ["b", "Lognormal size distributions → buoyant mass m = (ρ − ρ" + sub("w") + ")πD" + sup("3") + "/6",
     "Bubbles 130 nm (σ" + sub("ln d") + " 0.25), 3.0×10" + sup("8") + " mL" + sup("−1") + " (deck p2B); "
     "fragments 300 nm, ρ 1080 kg m" + sup("−3") + ", 0.5×10" + sup("8") + " mL" + sup("−1") +
     "; pulse removes 97% of bubbles"],
    ["c", "H4: rate = R" + sub("air") + "·N/N" + sub("air") + "; rivals: rate = R" + sub("air"),
     "R" + sub("air") + " = 0.28 ΔO/C per 100 h (deck p3D initial slope); N = 0.3, 0.8, 3.0, 4.5; noise 10% (x), "
     "8% (y); n = 3"],
    ["d", "rate = R" + sub("air") + "(S" + sub("v") + "/S" + sub("ref") + ")" + sup("0.61"),
     "S" + sub("ref") + " = 2/65 µm (deck p4D); exponent from deck p4E fit; ROOH alternative 1.5×"],
    ["e", "dθ/dt = k·N(θ)(1 − θ/θ" + sub("max") + ")e" + sup("−t/τ") + ", pool reset at refreeze",
     "k = 0.0016 h" + sup("−1") + ", τ = 100 h, θ" + sub("max") + " = 0.25, 72 h frozen per cycle (reproduce "
     "deck p4G: 0.065 at 72 h, plateau 0.118); N = (d" + sub("0") + "/d(θ))" + sup("0.61") + ", d(θ) = 5.0 + "
     "61.1e" + sup("−θ/0.145") + " µm; passivation N = 1 − 0.75θ/θ" + sub("max")],
    ["f", "Zener: d = 4r/3f", "r = 0.25 and 5 µm; natural ≤10" + sup("−7") + " (Arctic sea ice ≈1.2×10" +
     sup("4") + " particles L" + sup("−1") + " of ~20 µm ≈ 5×10" + sup("−8") + "); lab 10–1000 mg L" +
     sup("−1") + " ≈ 10" + sup("−5") + "–10" + sup("−3")],
    ["g", "Saturating release pools (illustrative)", "NP 4.0(1 − e" + sup("−n/60") + ")%, DOC 1.5(1 − e" +
     sup("−n/80") + ")%, CO" + sub("2") + " 0.002n%, water 0.05%"],
    ["i", "ΔO/C = a(1 − e" + sup("−n/n0") + ")", "PS a 0.20, n0 50; PE a 0.05, n0 70; unfrozen 0.005; season "
     "totals 25/110/40 cycles; noise σ 0.006"],
    ["j", "Preferential elution C/C" + sub("mean") + " = e" + sup("−F/τ") + "/[τ(1 − e" + sup("−1/τ") + ")]",
     "τ: chloride 0.30, products 0.33, nanoplastics 0.60; intact MPs 3F" + sup("2") +
     " (snowpack filtration, late release)"],
], [11, 68, 95]))

# ----------------------------------------------------------------------------------------------------- 6
story.append(P("6  Field study design (and why a single summit sample is not enough)", "h1"))
story.append(box([
    P("<b>Should we just sample mountain-top ice and track microplastic degradation over time?</b> Not on "
      "its own. Summit MPs arrive after atmospheric transport under strong UV, so their starting state is "
      "unknown and any aging may predate deposition. Summit ice sees few freeze–thaw cycles, which is the "
      "variable the mechanism depends on. There is no counterfactual, counts are tens to hundreds per litre, "
      "and contamination dominates. A referee can attribute any trend to UV, deposition history or handling.",
      "box"),
], bg=WARN, edge=colors.HexColor("#D55E00")))
story.append(Spacer(1, 4))
story.append(table([
    ["Element", "Specification", "Why"],
    ["Sites", "Three stations on one elevation transect (few / most / few freeze–thaw cycles), optionally a "
     "seasonally frozen soil or lake-ice site", "Freeze–thaw count becomes the dose variable; elevation and UV "
     "are decoupled from it"],
    ["Reference MPs", sup("13") + "C-PS (500 nm, 10 µm), PE, PET; fully characterized at t" + sub("0"),
     "Known starting state; " + sup("13") + "C traces fate against background plastic"],
    ["Containment", "Sealed borosilicate cells filled with site snow or meltwater, vented through stainless "
     "frits; no fluoropolymer or PP parts", "Nanoparticles must not escape; avoids H5 artefacts and "
     "contamination"],
    ["Treatments", "Exposed / dark / unfrozen (+2 °C, thermostatted); n ≥ 3 per treatment per retrieval",
     "Separates photo-oxidation and freezing; the unfrozen cell is the counterfactual"],
    ["Retrievals", "1/3, 2/3 and end of season", "Gives a dose–response, not a single endpoint"],
    ["Loggers", "Temperature in each cell (±0.1 °C, 10 min); UV-A/B and PAR", "Count cycles with a −1/+1 °C "
     "hysteresis band, so sensor noise is not counted"],
    ["Native archive", "Snow/firn pit at the high station; fresh layer = atmospheric baseline", "Secondary "
     "evidence on real MPs; never the primary test"],
    ["Meltwater", "Lysimeter on unseeded snow for native material; lab snow columns with natural snow for " +
     sup("13") + "C-PS", "Do not seed open snowpack with plastics; permits and full recovery otherwise"],
    ["Lab twin", "Climate chamber replays each station's logged T(t) and light", "Separates climate from site "
     "factors (deposition, biology)"],
    ["QA", "Field, travel and procedural blanks; glass and metal tools; cotton clothing", "MP studies fail on "
     "contamination"],
    ["Readouts", "ΔO/C, C1s fitting, FTIR carbonyl index, GPC, nanoplastic counts, " + sup("13") + "C-DOC, " +
     sup("13") + "CO" + sub("2"), "Same metrics as the lab, so field and lab plot on one axis"],
], [24, 84, 66]))
story.append(P("One winter season (November–May) with the lab twin running in parallel is enough to produce "
               "Fig. 2i and 2j.", "small"))

# ----------------------------------------------------------------------------------------------------- 7
story.append(P("7  Prioritized plan with decision gates", "h1"))
story.append(table([
    ["#", "Experiment", "Time", "Decision gate"],
    ["P1", "Bubble identity (2b) and dose–response at fixed O" + sub("2") + " (2c)", "2–3 wk",
     "If oxidation does not track bubble number, drop H4 and reframe as ice-confined interfacial ROS (H2/H3)"],
    ["P2", "Discrimination matrix (2a) with species probes, D" + sub("2") + "O, azide, TBA, dark/light, "
     "vial material", "3–4 wk", "Species identity sets the mechanism language; if •OH, remove " + O2s +
     " from the schematic"],
    ["P3", "Feedback causality (2d) and ratchet (2e)", "4–6 wk", "If flat or falling, retitle: "
     "\"re-oxygenation ratchet\" or \"self-limiting\" instead of \"positive feedback\""],
    ["P4", "Realistic loadings and matrices (2f; brine, snowmelt, DOM; −2 to −20 °C)", "3 wk",
     "If refinement vanishes at ≤10" + sup("−5") + ", confine the feedback claim to hotspots"],
    ["P5", sup("13") + "C budget (2g); quantified products with standards; nanoplastic release", "6–8 wk",
     "Decides between \"degradation\" and \"surface aging\" language"],
    ["P6", "Field season, lab twin, meltwater (2h–j)", "One winter", "Required for <i>Nature Water</i>"],
], [10, 78, 18, 68]))
story.append(P("P1–P3 (plus partial P5) are enough for <i>Nat. Commun.</i>, <i>JACS</i> or <i>Angew.</i> "
               "<i>Nature Water</i> needs P1–P6.", "small"))

# ----------------------------------------------------------------------------------------------------- 8
story.append(P("8  Journal fit and likelihood (subjective editorial estimates)", "h1"))
story.append(table([
    ["Journal", "As the deck stands", "With the decisive package", "Comment"],
    ["<i>Nature Water</i>", "~5% (likely desk reject)", "15–25%", "Needs the water-systems \"so what\": field "
     "plus meltwater"],
    ["<i>Nature Sustainability</i>", "<3%", "~5%", "Poor fit either way: weeks at −20 °C is not a sustainable "
     "treatment"],
    ["<i>Nature Communications</i>", "15–20%", "35–45%", "Most realistic Nature-family home"],
    ["<i>JACS</i>", "10–15%", "30–40%", "Mechanism must be nailed: isotopes, kinetics, species"],
    ["<i>Angew. Chem.</i>", "25–30%", "45–55%", "Published Tian 2022, so a mechanistic correction fits"],
    ["<i>PNAS</i> / <i>Sci. Adv.</i>", "10–20%", "25–35%", ""],
    ["<i>ES&amp;T</i>", "40–50%", "65–75%", "Safe home for the environmental-fate version"],
], [38, 34, 38, 64]))
story.append(P("Strategy: send <i>Nature Water</i> a presubmission enquiry built around the feedback concept "
               "and the Zener sanity check (Fig. 2f). If interest is lukewarm, target <i>Nat. Commun.</i> "
               "after P1–P3.", "small"))

# ----------------------------------------------------------------------------------------------------- 9
story.append(P("9  Referee checklist (what a picky reviewer will ask)", "h1"))
story += bullets([
    "<b>Nanobubble identity:</b> NTA counts nanoplastics too; the Rh-6G \"nanobubble\" channel is a "
    "continuous vein network (freeze-concentrated dye). Needed: resonant mass, degassed/Ar controls, pressure "
    "collapse, cryo-EM.",
    "<b>ROS identity:</b> TEMP→TEMPO and DCFH are non-specific; DCFH photo-oxidizes under the imaging laser. "
    "Needed: D" + sub("2") + "O enhancement, azide/FFA quenching, 1270 nm emission, •OH probes and TBA.",
    "<b>Light:</b> state the light conditions of every experiment; freezers are dark.",
    "<b>O/C metric:</b> report ΔO/C against pristine, fitted C1s components and FTIR carbonyl index; PS O/C "
    "under nominally the same condition reads 0.10 (p1B), 0.12 (p4G) and 0.19–0.21 (p3D/E). Specify size "
    "and time.",
    "<b>Surface vs bulk:</b> XPS probes ~5–10 nm, but PS Mw halves across 0.5–1 µm particles. Show depth "
    "profiles and GPC mass recovery.",
    "<b>Products:</b> m/z 105/77/51 is a generic benzoyl pattern. Identify with authentic standards, "
    "quantify yields, close the mass balance.",
    "<b>Feedback:</b> correlation is not causation; the plateau contradicts autocatalysis; melt–refreeze "
    "confounds re-oxygenation.",
    "<b>Relevance:</b> loading, solution composition and liquid fraction, temperature range, container "
    "material (PFA), natural matrices, field data.",
    "<b>Tone:</b> demonstrate rather than assert that prior work (Angew 2022 EPR) was wrong; its authors may "
    "review.",
])

# ----------------------------------------------------------------------------------------------------- 10
story.append(P("10  Provenance and caveats", "h1"))
story += bullets([
    "Fig. 1 values are digitized from the deck's figures (±2–5%). PE, PP and PVC Mw are read off a log axis.",
    "Fig. 2 data panels are simulated from the models in Section 5.3 and are labelled \"Simulated\", "
    "\"Calculated\" or \"Illustrative\". Fig. 2g magnitudes are guesses; only the shape carries meaning.",
    "Competitor details come from abstracts, indexes and press coverage. Publisher full texts (nature.com, "
    "Wiley) could not be opened from the analysis environment, so verify numbers before citing them.",
    "Journal likelihoods are subjective editorial estimates, not statistics.",
    "Figures were rendered in Liberation Sans (metric-compatible with Arial); the scripts use Arial "
    "automatically where it is installed.",
])

story.append(P("References", "h1"))
refs = [
    "Qian, N. et al. Intrinsic physicochemical activity at microplastic–water interfaces. <i>Nature</i> 658, "
    "650–657 (2026). https://www.nature.com/articles/s41586-026-11141-y",
    "Gao, R. et al. Catalyst-free, microdroplet-mediated waste plastic conversion to diacids. <i>Nature</i> "
    "(2026). https://www.nature.com/articles/s41586-026-10746-7",
    "Tian, C. et al. Accelerated degradation of microplastics at the liquid interface of ice crystals in "
    "frozen aqueous solutions. <i>Angew. Chem. Int. Ed.</i> 61, e202206947 (2022). "
    "https://pubmed.ncbi.nlm.nih.gov/35642755/",
    "Freezing-induced microplastic degradation in an anoxic Fe(II)-containing solution: the key role of "
    "Fe(IV) and •OH. <i>Environ. Sci.: Nano</i> 10, 2744 (2023).",
    "The overlooked driver of microplastic chemical oxidation in cold soils: reactive oxygen species "
    "generation mediated by freeze–thaw cycles. <i>Environ. Sci. Technol.</i> (2025). "
    "https://pubs.acs.org/doi/10.1021/acs.est.5c07624",
    "Song, J. et al. Spontaneous production of H" + sub("2") + "O" + sub("2") + " at the liquid–ice "
    "interface. <i>Environ. Sci. Technol.</i> 58, 22691 (2024). https://pmc.ncbi.nlm.nih.gov/articles/PMC11673118/",
    "Freezing–thawing-induced hydrogen peroxide formation in PFA containers (2026). "
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC13488436/",
    "Qi, et al. Evolution of bulk nanobubbles under different freezing conditions. <i>Langmuir</i> 39, "
    "16873 (2023). https://pubmed.ncbi.nlm.nih.gov/37966887/",
    "Nirmalkar, N., Pacek, A. W. &amp; Barigou, M. On the existence and stability of bulk nanobubbles. "
    "<i>Langmuir</i> (2018).",
    "Nanobubble reactivity: evaluating hydroxyl radical generation (or lack thereof) under ambient "
    "conditions. <i>ACS ES&amp;T Eng.</i> (2023). https://pubs.acs.org/doi/10.1021/acsestengg.3c00124",
    "Busting the myth of spontaneous formation of H" + sub("2") + "O" + sub("2") + " at the air–water "
    "interface. <i>Chem. Sci.</i> (2024). https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10901496/",
    "Harnessing oil–water microinterfaces for the catalyst-free oxidative degradation of toxic organic "
    "pollutants. <i>J. Am. Chem. Soc.</i> 148 (2026).",
    "He, Z., Liu, K. &amp; Wang, J. Bioinspired materials for controlling ice nucleation, growth, and "
    "recrystallization. <i>Acc. Chem. Res.</i> (2018). https://pubmed.ncbi.nlm.nih.gov/29664599/",
    "Takenaka, N. et al. Acceleration of the rate of nitrite oxidation by freezing in aqueous solution. "
    "<i>Nature</i> 358, 736 (1992).",
    "Fletcher, N. H. Size effect in heterogeneous nucleation. <i>J. Chem. Phys.</i> 29, 572 (1958).",
    "Smith, C. S. Grains, phases, and interfaces (Zener pinning). <i>Trans. AIME</i> 175, 15 (1948).",
    "Johannessen, M. &amp; Henriksen, A. Chemistry of snow meltwater: changes in concentration during "
    "melting. <i>Water Resour. Res.</i> 14, 615 (1978).",
    "Peeken, I. et al. Arctic sea ice is an important temporal sink and means of transport for microplastic. "
    "<i>Nat. Commun.</i> 9, 1505 (2018).",
]
for i, r in enumerate(refs, 1):
    story.append(P(f"{i}.  {r}", "ref"))

story.append(P("Appendix  Files and reproduction", "h1"))
story.append(table([
    ["File", "Content"],
    ["fig1_current_spine.py / fig2_roadmap.py", "One script per figure; vector PDF + SVG + PNG to out/"],
    ["simulate_expectations.py", "All Fig. 2 models; writes data/simulated/*.csv"],
    ["data/deck/*.csv", "Digitized deck values with source page and panel in each header"],
    ["common.py", "Nature-style preset, mm-grid helpers, schematic primitives"],
    ["build_report.py", "This report"],
], [62, 112], first_col_bold=False))


# =====================================================================================================
def check_glyphs():
    import re
    cmap = FTFont(LIB.format("Regular")).getBestCmap()
    chars = set()
    for t in ALL_TEXT:
        plain = re.sub(r"<[^>]+>", "", t)
        plain = re.sub(r"&[a-z]+;", "", plain)
        chars |= set(plain)
    missing = sorted(ch for ch in chars if ord(ch) > 127 and ord(ch) not in cmap)
    print("missing glyphs:", missing or "none")


def keep_headings(flow):
    """Never strand a heading at a page foot."""
    out = []
    for f in flow:
        if isinstance(f, Paragraph) and f.style.name in ("h1", "h2"):
            out.append(CondPageBreak((48 if f.style.name == "h1" else 34) * mm))
        out.append(f)
    return out


def build():
    check_glyphs()
    doc = SimpleDocTemplate(DRAFT, pagesize=A4, leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
                            title="Ice-driven microplastic oxidation: editorial assessment and figure plan",
                            author="Editorial assessment", subject="Nature Water figure plan")
    doc.build(keep_headings(story), onFirstPage=footer, onLaterPages=footer)
    base = PdfReader(DRAFT)
    w = PdfWriter(clone_from=base)
    for page_no, key, x, y, sw, sh in FigSlot.slots:
        fig = PdfReader(FIGS[key]).pages[0]
        fw = float(fig.mediabox.width)
        s = sw / fw
        w.pages[page_no - 1].merge_transformed_page(fig, Transformation().scale(s, s).translate(x, y))
    w.add_metadata({"/Title": "Ice-driven microplastic oxidation: editorial assessment and figure plan"})
    with open(REPORT, "wb") as fh:
        w.write(fh)
    os.remove(DRAFT)
    print("wrote", REPORT, "pages:", len(w.pages), "figure slots:", [(p, k) for p, k, *_ in FigSlot.slots])


if __name__ == "__main__":
    build()

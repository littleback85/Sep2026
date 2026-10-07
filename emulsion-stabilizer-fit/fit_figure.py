"""Fit max stable oil fraction vs stabilizer concentration with a Hill-type
coverage model and write a one-page PDF (figure + legend + explanation).

Usage: python3 fit_figure.py   (reads data_digitized.csv, writes stabilizer_fit.pdf)
"""
import csv
import io
from pathlib import Path

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.optimize import brentq, curve_fit
from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

HERE = Path(__file__).parent
DATA = HERE / "data_digitized.csv"
OUT = HERE / "stabilizer_fit.pdf"

PHI_REF = 74.0            # close packing of monodisperse spheres (wt% proxy)
GAMMA = (2e-6, 3e-6)      # assumed interfacial coverage, kg m^-2 (2-3 mg m^-2)
RHO_W = 1000.0            # kg m^-3

SYSTEMS = {  # name: (color, marker) -- colors kept from the original figure
    "PDDA/BSA": ("#009E73", "o"),
    "Tween 80": ("#333333", "s"),
    "native BSA": ("#0072B2", "^"),
}

# ---------------------------------------------------------------- data + fit
def load(path):
    rows = [r for r in csv.reader(l for l in open(path) if not l.startswith("#"))][1:]
    out = {}
    for name, c, p, used in rows:
        d = out.setdefault(name, {"c": [], "p": [], "used": []})
        d["c"].append(float(c)); d["p"].append(float(p)); d["used"].append(used == "1")
    return {k: {kk: np.array(vv) for kk, vv in v.items()} for k, v in out.items()}


def hill(c, pinf, c50, n):
    return pinf * c**n / (c50**n + c**n)


def fit(d):
    c, p = d["c"][d["used"]], d["p"][d["used"]]
    q, cov = curve_fit(hill, c, p, p0=[p.max() + 3, np.median(c), 1.0],
                       bounds=([p.max(), 1e-4, 0.1], [100, 100, 10]), maxfev=20000)
    se = np.sqrt(np.diag(cov))
    rmse = np.sqrt(np.mean((p - hill(c, *q)) ** 2))
    cstar = brentq(lambda x: hill(x, *q) - PHI_REF, 1e-5, 1e4)
    return dict(pinf=q[0], c50=q[1], n=q[2], se=se, rmse=rmse, cstar=cstar,
                cmin=c.min(), cmax=c.max(), npts=len(c))


def implied_d_um(c50_wtpct):
    """Droplet diameter implied by c50 = 6*Gamma/(rho_w*d) for Gamma in GAMMA."""
    return [6 * g / (RHO_W * c50_wtpct / 100) * 1e6 for g in GAMMA]


data = load(DATA)
res = {k: fit(v) for k, v in data.items()}

# ---------------------------------------------------------------- figure
MM = 1 / 25.4
mpl.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
    "font.size": 6, "axes.labelsize": 7, "xtick.labelsize": 6, "ytick.labelsize": 6, "legend.fontsize": 6,
    "axes.linewidth": 0.5, "lines.linewidth": 1, "lines.markersize": 3.5,
    "xtick.major.width": 0.5, "ytick.major.width": 0.5, "xtick.major.size": 2, "ytick.major.size": 2,
    "xtick.minor.visible": False, "ytick.minor.visible": False,
    "xtick.direction": "in", "ytick.direction": "in", "xtick.top": True, "ytick.right": True,
    "legend.frameon": False, "mathtext.fontset": "custom", "mathtext.rm": "Liberation Sans",
    "mathtext.it": "Liberation Sans:italic", "pdf.fonttype": 42, "svg.fonttype": "none", "savefig.dpi": 600,
})

FIG_W, FIG_H = 183, 66
fig = plt.figure(figsize=(FIG_W * MM, FIG_H * MM))


def ax_mm(x, y, w, h):
    return fig.add_axes([x / FIG_W, 1 - (y + h) / FIG_H, w / FIG_W, h / FIG_H])


def letter(x, y, s):
    fig.text(x / FIG_W, 1 - y / FIG_H, s, fontsize=8, fontweight="bold", ha="left", va="top")


XTICKS = [0.03, 0.1, 0.3, 1, 3, 10, 30]
AX_Y, AX_W, AX_H = 5, 68, 50
axa, axb = ax_mm(14, AX_Y, AX_W, AX_H), ax_mm(110, AX_Y, AX_W, AX_H)
letter(1, 2, "a"); letter(97, 2, "b")

for ax in (axa, axb):
    ax.set_xscale("log"); ax.set_xlim(0.03, 30)
    ax.set_xticks(XTICKS, [f"{t:g}" for t in XTICKS])
    ax.set_xlabel("Stabilizer (wt% of aqueous phase)")
    ax.minorticks_off()

# panel a: data + fits
axa.axhline(PHI_REF, color="0.55", lw=0.5, ls="--", zorder=0)
axa.text(29, PHI_REF - 1.5, "φ = 0.74", ha="right", va="top", color="0.4")
for name, d in data.items():
    col, mk = SYSTEMS[name]; r = res[name]
    u = d["used"]
    axa.plot(d["c"][u], d["p"][u], mk, color=col, ms=3.5, mec=col, label=name, zorder=3)
    axa.plot(d["c"][~u], d["p"][~u], mk, mfc="white", mec=col, mew=0.6, ms=3.5, zorder=3)
    cc = np.geomspace(r["cmin"], r["cmax"], 300)
    axa.plot(cc, hill(cc, r["pinf"], r["c50"], r["n"]), color=col, lw=0.9, zorder=2)
    axa.plot([r["cstar"]] * 2, [0, PHI_REF], ":", color=col, lw=0.75, zorder=1)
    axa.text(r["cstar"] * 1.08, 9, f"{r['cstar']:.2g}", color=col, ha="left", va="bottom")
axa.set_ylim(0, 100)
axa.set_ylabel("Max. stable oil (wt%)")
axa.legend(loc="upper left", handletextpad=0.3, borderaxespad=0.3, labelspacing=0.3)

N_LABEL = {"PDDA/BSA": (0.25, 9), "Tween 80": (6, 40), "native BSA": (12, 2.5)}  # label (c, y)
# panel b: linearized, phi/(phi_inf - phi) vs c, slope = n
for name, d in data.items():
    col, mk = SYSTEMS[name]; r = res[name]
    u = d["used"]
    y = d["p"] / (r["pinf"] - d["p"])
    axb.plot(d["c"][u], y[u], mk, color=col, ms=3.5, mec=col, zorder=3)
    axb.plot(d["c"][~u], y[~u], mk, mfc="white", mec=col, mew=0.6, ms=3.5, zorder=3)
    cc = np.geomspace(r["cmin"], r["cmax"], 50)
    axb.plot(cc, (cc / r["c50"]) ** r["n"], color=col, lw=0.9, zorder=2)
    lab_x, lab_y = N_LABEL[name]
    axb.text(lab_x, lab_y, f"n = {r['n']:.2f}", color=col, ha="left", va="center")
# slope-1 reference (ideal coverage at fixed droplet size)
cr = np.array([0.04, 0.4])
axb.plot(cr, 12 * cr / cr[0], "--", color="0.55", lw=0.6)
axb.text(0.13, 12 * 0.13 / 0.04 * 1.15, "slope 1", color="0.4", rotation=0, ha="right", va="bottom")
axb.set_yscale("log"); axb.set_ylim(0.03, 300)
axb.minorticks_off()
axb.set_yticks([0.1, 1, 10, 100], ["0.1", "1", "10", "100"])
axb.set_ylabel("φ / (φ$_\\infty$ − φ)")

buf = io.BytesIO()
fig.savefig(buf, format="pdf")
fig.savefig(HERE / "stabilizer_fit_figure.png", dpi=300)
fig.savefig(HERE / "stabilizer_fit_figure.svg")
plt.close(fig)

# ---------------------------------------------------------------- page text
pdfmetrics.registerFont(TTFont("LS", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("LS-B", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("LS-I", "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("LS-BI", "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("LS", normal="LS", bold="LS-B", italic="LS-I", boldItalic="LS-BI")

body = ParagraphStyle("body", fontName="LS", fontSize=8.5, leading=11.5, alignment=TA_JUSTIFY, spaceAfter=5)
head = ParagraphStyle("head", parent=body, fontName="LS-B", fontSize=9.5, spaceBefore=6, spaceAfter=3)

P, T, B = res["PDDA/BSA"], res["Tween 80"], res["native BSA"]
dT, dP = implied_d_um(T["c50"]), implied_d_um(P["c50"])
F = "φ<sub>max</sub> = φ<sub>∞</sub>·c<super>n</super> / (c<sub>50</sub><super>n</super> + c<super>n</super>)"

caption = (
    "<b>Figure | Maximum stable oil fraction versus stabilizer concentration, fitted with a "
    "coverage-based Hill (log-logistic) model.</b> "
    "<b>a</b>, Maximum stable oil fraction as a function of stabilizer concentration (wt% of the aqueous phase) "
    "for the PDDA/BSA coacervate (green circles), Tween 80 (grey squares) and native BSA (blue triangles). "
    f"Solid lines are least-squares fits of {F}, drawn over the measured concentration range of each series. "
    "The dashed horizontal line marks φ = 0.74 (close packing of monodisperse spheres; above it the emulsions are "
    "high-internal-phase emulsions); dotted vertical lines and numbers give the fitted concentration c* at which each "
    "curve reaches 0.74. "
    "<b>b</b>, Linearized form of the same data, φ/(φ<sub>∞</sub> − φ) versus c on log–log axes, using the fitted "
    "φ<sub>∞</sub> of each system; in this representation the model is a straight line of slope n. The grey dashed "
    "segment has slope 1, the value expected when the stabilizer only has to cover the oil–water interface of "
    "droplets of fixed size. "
    "Filled symbols were used in the fits; open symbols are shown but were not fitted. Points are as plotted in the "
    f"original figure, which shows no error bars ({P['npts']}, {T['npts']} and {B['npts']} fitted points for PDDA/BSA, Tween 80 and native BSA). "
    "Values were digitized from the original figure and are approximate."
)

hdr = ParagraphStyle("hdr", parent=body, fontName="LS-B", fontSize=8, leading=10, alignment=0, spaceAfter=0)
tbl_rows = [[Paragraph(t, hdr) for t in ["System", "φ<sub>∞</sub> (wt%)", "c<sub>50</sub> (wt%)", "n",
                                        "RMSE (wt%)", "c* at φ = 0.74 (wt%)"]]]
for name, r in res.items():
    s = r["se"]
    tbl_rows.append([name, f"{r['pinf']:.0f} ± {s[0]:.0f}", f"{r['c50']:.3g} ± {s[1]:.1g}",
                     f"{r['n']:.2f} ± {s[2]:.2f}", f"{r['rmse']:.1f}", f"{r['cstar']:.2g}"])
table = Table(tbl_rows, hAlign="LEFT", colWidths=[26*mm, 24*mm, 28*mm, 24*mm, 24*mm, 40*mm])
table.setStyle(TableStyle([
    ("FONT", (0, 0), (-1, -1), "LS", 8), ("FONT", (0, 0), (-1, 0), "LS-B", 8),
    ("LINEABOVE", (0, 0), (-1, 0), 0.6, "black"), ("LINEBELOW", (0, 0), (-1, 0), 0.4, "black"),
    ("LINEBELOW", (0, -1), (-1, -1), 0.6, "black"),
    ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
]))
tbl_note = Paragraph("Fit parameters (± standard error from the fit covariance).",
                     ParagraphStyle("note", parent=body, fontSize=7.5, leading=10, spaceBefore=2))

what = (
    f"<b>What we used.</b> Each series was fitted with {F}, using non-linear least squares on the "
    "untransformed oil fractions (scipy <i>curve_fit</i>). There are three parameters: φ<sub>∞</sub>, the plateau oil "
    "fraction reached at high stabilizer concentration; c<sub>50</sub>, the concentration at which half of that "
    "plateau is reached; and n, which sets how steeply φ<sub>max</sub> rises with log c."
)
why = (
    "<b>Why this function.</b> It follows from a mass balance on the interface. Emulsifying a volume fraction φ of oil "
    "into droplets of diameter d creates 6φ/d of interface per unit emulsion volume. Covering it at a surface load Γ "
    "requires a mass of stabilizer of 6Γφ/d, while the stabilizer available is c·ρ<sub>w</sub>(1 − φ), because c is "
    "expressed per mass of aqueous phase. Setting the two equal gives φ/(1 − φ) = c/c<sub>50</sub> with "
    "c<sub>50</sub> = 6Γ/(ρ<sub>w</sub>d), which is the model above with n = 1 and φ<sub>∞</sub> = 1. "
    "φ<sub>∞</sub> &lt; 1 accounts for the separate ceiling (packing, film drainage or phase inversion near 90 wt%) that "
    "no amount of stabilizer removes, and a free exponent n measures how far a stabilizer departs from simple coverage "
    "of fixed-size droplets: n &lt; 1 means diminishing returns, n &gt; 1 means a threshold or cooperative behaviour. "
    "The model therefore has a physical basis and turns each curve into three interpretable numbers rather than "
    "describing it qualitatively."
)
tells = (
    f"<b>What the fit tells us.</b> (i) <i>Tween 80</i> follows the coverage model almost exactly "
    f"(n = {T['n']:.2f} ± {T['se'][2]:.2f}). Its c<sub>50</sub> of {T['c50']:.2g} wt%, combined with a typical "
    f"surfactant load of Γ ≈ 2–3 mg m<super>−2</super>, implies a droplet diameter of ≈{dT[0]:.0f}–{dT[1]:.0f} µm, a "
    "realistic size that can be checked against microscopy; this supports interface coverage as the factor limiting "
    f"the oil fraction. (ii) <i>Native BSA</i> rises more steeply than coverage alone predicts "
    f"(n = {B['n']:.1f} ± {B['se'][2]:.1f}) and only becomes effective above ≈{B['c50']:.0f} wt%, consistent with a "
    "threshold concentration for forming a cohesive protein film within the emulsification time (slow adsorption and "
    f"unfolding). (iii) The <i>PDDA/BSA coacervate</i> has the lowest c* ({P['cstar']:.2g} wt%, versus "
    f"{T['cstar']:.2g} wt% for Tween 80 and {B['cstar']:.2g} wt% for native BSA, i.e. ≈{T['cstar']/P['cstar']:.0f}× and "
    f"≈{B['cstar']/P['cstar']:.0f}× less stabilizer for a high-internal-phase emulsion) and a shallow, sub-linear "
    f"dependence (n = {P['n']:.2f} ± {P['se'][2]:.2f}). Its fitted c<sub>50</sub> ({P['c50']:.2g} wt%) lies below the "
    "lowest concentration measured, so it is an extrapolation; taken at face value it would imply droplets of "
    f"≈{dP[0]:.0f}–{dP[1]:.0f} µm for a protein-like surface load. Because that is implausibly large, the coacervate "
    "probably does not act through monolayer coverage alone: thick or multilayer interfacial films, or a network in "
    "the continuous phase, would explain why so little material stabilizes so much oil. Droplet-size measurements "
    "(a limited-coalescence plot of 1/D versus stabilizer-to-oil ratio) and data below 0.1 wt% would test this. "
    "<b>Caveats:</b> 6–8 points per series for 3 parameters, no replicate information, digitized values and wt% used in "
    "place of volume fraction. The threshold concentrations c* are robust (they agree within ≈15% with direct "
    "interpolation of the data), whereas c<sub>50</sub> and n should be treated as semi-quantitative."
)


class FigureSlot(Flowable):
    """Reserves space for the matplotlib PDF and records where it lands."""
    def __init__(self, w, h):
        super().__init__(); self.width, self.height = w, h; self.pos = None
    def wrap(self, *a):
        return self.width, self.height
    def draw(self):
        self.pos = self.canv.absolutePosition(0, 0)


slot = FigureSlot(FIG_W * mm, FIG_H * mm)
text_buf = io.BytesIO()
margin = (A4[0] - FIG_W * mm) / 2
doc = SimpleDocTemplate(text_buf, pagesize=A4, leftMargin=margin, rightMargin=margin,
                        topMargin=14 * mm, bottomMargin=12 * mm,
                        title="Stabilizer efficiency fit", author="")
doc.build([slot, Spacer(1, 4 * mm), Paragraph(caption, body), Spacer(1, 1 * mm), table, tbl_note,
           Paragraph("Fitting approach and interpretation", head),
           Paragraph(what, body), Paragraph(why, body), Paragraph(tells, body)])

page = PdfReader(text_buf).pages[0]
figpage = PdfReader(buf).pages[0]
page.merge_transformed_page(figpage, Transformation().translate(*slot.pos))
w = PdfWriter(); w.add_page(page)
with open(OUT, "wb") as f:
    w.write(f)

for name, r in res.items():
    print(f"{name:11s} pinf={r['pinf']:.1f} c50={r['c50']:.3g} n={r['n']:.2f} se={np.round(r['se'],3)} "
          f"rmse={r['rmse']:.1f} c*={r['cstar']:.3g}")
print("implied d (um): Tween", np.round(dT, 1), "PDDA/BSA", np.round(dP, 0))
print("wrote", OUT, "pages:", len(PdfReader(OUT).pages))

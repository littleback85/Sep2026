"""
PDDA/BSA coacervate layer compressed by PEG osmotic stress: osmotic modulus.

Run:  python3 analysis.py   -> prints tables, writes results.md, the main figure
                               (coacervate_osmotic_modulus.png/.pdf) and the SI
                               figure (SI_raw_trajectories.png/.pdf)
Then: python3 build_pdf.py  -> coacervate_osmotic_modulus_report.pdf

Physics
-------
The coacervate layer sits in a well and only its height can change, so
V/V0 = h/h0. At equilibrium the coacervate's own osmotic pressure balances the
PEG reservoir, so the PEG pressure maps out the coacervate equation of state.
The osmotic (compression) modulus is

    K_osm = c dPi/dc = -dPi/d ln V = dPi/d eps,   eps = -ln(h/h0).

PEG pressure is the controlled variable and eps is what is measured (and
scatters), so every fit regresses strain on pressure and inverts the slope.
The 20% PEG group is not used for the modulus (persistent wall climbing; sample
2 also excluded); it is shown only in the SI figure.
"""
import csv
import os
import numpy as np
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------
# 1. INPUTS
# ----------------------------------------------------------------------------
# Per-sample h/h0 trajectories digitised from the original per-sample panels
# (marker centroids, axes calibrated on tick marks, ~0.005 reading error).
# Where markers of different samples overlap, the hidden value was solved from
# the group mean plotted in the original panel A. Replace this file with the
# measured numbers when available.
TIMES, H = None, {}
with open(os.path.join(HERE, "digitised_trajectories.csv")) as fh:
    rd = csv.reader(fh)
    head = next(rd)
    TIMES = np.array([float(c[1:-1]) for c in head[2:]])
    for r in rd:
        H.setdefault(int(r[0]), []).append(np.array([float(x) for x in r[2:]]))
T_END = 80.0
IEND = int(np.where(TIMES == T_END)[0][0])
H80 = {g: [tr[IEND] for tr in H[g]] for g in H}

GROUPS = [0, 5, 10, 15]                  # used for the modulus
EXCLUDED_20 = {1}                        # 20% sample 2 (0-based index)

# Nominal PEG osmotic pressure (MPa), read off the original panel B.
PI = {0: 0.0, 5: 0.052, 10: 0.181, 15: 0.412}

T = 298.15
R = 8.314
KB = 1.380649e-23
NA = 6.02214e23
RT = R * T                               # J/mol

COL = {0: "#555555", 5: "#0072B2", 10: "#E69F00", 15: "#009E73", 20: "#CC79A7"}

# ----------------------------------------------------------------------------
# 2. PEG PRESSURE CURVE (for the PEG-bath modulus and the 20% SI annotation)
# ----------------------------------------------------------------------------
w = np.array([5, 10, 15], float)
logPi = np.log10([PI[k] for k in (5, 10, 15)])
A = np.vstack([np.ones(3), w**0.21]).T
(rand_a, rand_b), *_ = np.linalg.lstsq(A, logPi, rcond=None)
def pi_rand(wt):
    return 10 ** (rand_a + rand_b * np.asarray(wt, float) ** 0.21)
def k_peg(wt):
    """PEG solution's own osmotic modulus, K = c dPi/dc ~ w dPi/dw."""
    return float(pi_rand(wt) * np.log(10) * rand_b * 0.21 * np.asarray(wt, float) ** 0.21)
PI_20 = float(pi_rand(20))

# ----------------------------------------------------------------------------
# 3. FITS (0-15% PEG, 80 h, individual samples)
# ----------------------------------------------------------------------------
P = np.array([PI[g] for g in GROUPS for _ in H80[g]])
HH = np.array([h for g in GROUPS for h in H80[g]])
EPS = -np.log(HH)
ENG = 1 - HH
N = len(P)

def ols(x, y):
    X = np.vstack([x, np.ones(len(x))]).T
    (m, b), *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - (m * x + b)
    s2 = r @ r / (len(x) - 2)
    cov = s2 * np.linalg.inv(X.T @ X)
    return m, b, np.sqrt(cov[0, 0]), r @ r, 1 - r @ r / np.sum((y - y.mean()) ** 2)

T975_10 = 2.228                          # Student t, 10 dof, two-sided 95%

def linear_fit(strain):
    m, s0, sm, sse, r2 = ols(P, strain)
    K = 1 / m
    sK = sm / m**2
    return dict(K=K, sK=sK, ci=T975_10 * sK, s0=s0, sse=sse, r2=r2)

LIN = linear_fit(EPS)                    # Pi = K (eps - eps0)
ENGF = linear_fit(ENG)                   # Pi = K (e - e0), e = 1 - h/h0

# Stiffening equation of state: K(Pi) = K0 + alpha*Pi
#   <=> Pi = (K0/alpha) [exp(alpha (eps-eps0)) - 1]
#   <=> eps = eps0 + ln(1 + alpha Pi / K0) / alpha
def eps_stiff(p, e0, K0, al):
    return e0 + np.log1p(al * p / K0) / al
pS, cS = curve_fit(eps_stiff, P, EPS, p0=(-0.015, 1.0, 2.0), maxfev=20000)
sS = np.sqrt(np.diag(cS))
sse_S = np.sum((EPS - eps_stiff(P, *pS)) ** 2)
def aicc(sse, k, n=N):
    return n * np.log(sse / n) + 2 * k + 2 * k * (k + 1) / (n - k - 1)
STIFF = dict(e0=pS[0], K0=pS[1], sK0=sS[1], al=pS[2], sal=sS[2], sse=sse_S,
             K15=pS[1] + pS[2] * PI[15],
             dAICc=aicc(sse_S, 3) - aicc(LIN["sse"], 2))

# Original panel-B method: Pi on eps, group means
GM = {g: np.mean(-np.log(H80[g])) for g in GROUPS}
GSD = {g: np.std(-np.log(H80[g]), ddof=1) for g in GROUPS}
K_MEANS = ols(np.array([GM[g] for g in GROUPS]), np.array([PI[g] for g in GROUPS]))[0]
STEP = [(a, b, (PI[b] - PI[a]) / (GM[b] - GM[a])) for a, b in zip(GROUPS[:-1], GROUPS[1:])]

# How curved can an EOS be over this window and still look linear?
# For K = K0 exp(beta*eps) the secant over [0, eps] is K0 (e^{x}-1)/x, x = beta*eps.
EPS_SPAN = GM[15] - GM[0]

# ----------------------------------------------------------------------------
# 4. BENCHMARKS (MPa)
# ----------------------------------------------------------------------------
BSA_M = 66.4                             # kg/mol
def bsa_K(c, veff):
    phi = c * veff
    n = c / BSA_M * NA
    dphiZ = (1 + 4*phi + 4*phi**2 - 4*phi**3 + phi**4) / (1 - phi) ** 4
    return n * KB * T * dphiZ / 1e6
def bsa_range(c):
    return bsa_K(c, 1.2e-3), bsa_K(c, 1.5e-3)

PI_SALINE = 2 * 150 * RT / 1e6           # 150 mM NaCl, ideal van 't Hoff (MPa)
PI_CELL = 290 * RT / 1e6                 # 290 mOsm/kg cytoplasm
# Benchmarks: (group, label, lo, hi, kind, colour)
#   kind "osm" = osmotic / compressive modulus (filled), "shear" = shear modulus (open)
BENCH = [
    ("This work", "PDDA/BSA coacervate", LIN["K"] - LIN["ci"], LIN["K"] + LIN["ci"], "osm", "#111111"),
    ("PEG bath", "PEG 5%", k_peg(5), k_peg(5), "osm", COL[5]),
    ("PEG bath", "PEG 10%", k_peg(10), k_peg(10), "osm", COL[10]),
    ("PEG bath", "PEG 15%", k_peg(15), k_peg(15), "osm", COL[15]),
    ("Protein", "BSA 200 g/L", *bsa_range(200), "osm", "#8c6d31"),
    ("Protein", "BSA 300 g/L", *bsa_range(300), "osm", "#8c6d31"),
    ("Protein", "BSA 400 g/L", *bsa_range(400), "osm", "#8c6d31"),
    ("Salt", "150 mM NaCl", 0.93 * PI_SALINE, PI_SALINE, "osm", "#6b6b6b"),
    ("Biological", "Cell (osmometer)", PI_CELL / 0.8, PI_CELL / 0.6, "osm", "#6b6b6b"),
    ("Biological", "Articular cartilage", 0.08, 2.1, "osm", "#6b6b6b"),
    ("Gels", "Synthetic gels", 1e-3, 1e-1, "osm", "#6b6b6b"),
    ("Gels", "PEGDA gels G′ (this lab)", 1.496e-3, 1.505e-2, "shear", "#6b6b6b"),
    ("Coacervate", "Complex coacervate G′", 1e-4, 1e-2, "shear", "#6b6b6b"),
]

# ----------------------------------------------------------------------------
# 5. REPORT
# ----------------------------------------------------------------------------
def report():
    L = ["# Osmotic modulus of the PDDA/BSA coacervate under PEG stress\n"]
    L.append("## Inputs (h/h0 at 80 h, digitised; 0–15% PEG)\n")
    L.append("| PEG | Π (MPa) | sample 1 | sample 2 | sample 3 | mean ε = −ln(h/h0) | SD |")
    L.append("|---|---|---|---|---|---|---|")
    for g in GROUPS:
        L.append(f"| {g}% | {PI[g]:.3f} | " + " | ".join(f"{h:.3f}" for h in H80[g]) +
                 f" | {GM[g]:.3f} | {GSD[g]:.3f} |")
    L.append("")
    L.append("## Fits (n = 12 samples, strain regressed on Π)\n")
    L.append("| Model | K (MPa) | 95% CI | R² or note |")
    L.append("|---|---|---|---|")
    L.append(f"| Linear in log strain, Π = K(ε − ε₀) | **{LIN['K']:.2f}** ± {LIN['sK']:.2f} | "
             f"{LIN['K']-LIN['ci']:.2f}–{LIN['K']+LIN['ci']:.2f} | R² {LIN['r2']:.2f} |")
    L.append(f"| Linear in engineering strain, Π = K(1 − h/h₀ − e₀) | {ENGF['K']:.2f} ± {ENGF['sK']:.2f} | "
             f"{ENGF['K']-ENGF['ci']:.2f}–{ENGF['K']+ENGF['ci']:.2f} | R² {ENGF['r2']:.2f} |")
    L.append(f"| Stiffening EOS, K = K₀ + αΠ | K₀ = {STIFF['K0']:.2f} ± {STIFF['sK0']:.2f}, "
             f"α = {STIFF['al']:.1f} ± {STIFF['sal']:.1f} | K(15%) = {STIFF['K15']:.2f} | "
             f"ΔAICc vs linear = {STIFF['dAICc']:+.1f} |")
    L.append(f"| Π on ε, group means (original panel) | {K_MEANS:.2f} | – | – |")
    L.append("")
    L.append("Step moduli between neighbouring group means: " +
             ", ".join(f"{a}→{b}% {k:.2f} MPa" for a, b, k in STEP) + ".\n")
    L.append("## Benchmarks (MPa)\n")
    L.append("| Group | System | K or G (MPa) | Type |")
    L.append("|---|---|---|---|")
    for grp, lab, lo, hi, kind, _ in BENCH:
        v = f"{lo:.3g}" if np.isclose(lo, hi) else f"{lo:.3g}–{hi:.3g}"
        L.append(f"| {grp} | {lab.replace(chr(10), ' ')} | {v} | {'osmotic/compressive' if kind == 'osm' else 'shear'} |")
    L.append("")
    L.append(f"20% PEG (SI only): Π extrapolated to {PI_20:.2f} MPa; h/h0(80 h) = "
             + ", ".join(f"{h:.3f}" for h in H80[20]) + " (sample 2 excluded).")
    return "\n".join(L)

# ----------------------------------------------------------------------------
# 6. FIGURES
# ----------------------------------------------------------------------------
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.linewidth": 0.8, "xtick.major.width": 0.8, "ytick.major.width": 0.8,
                     "legend.handlelength": 2.2})
NOTE = "#555555"

def scatter_groups(ax, xf):
    for g in GROUPS:
        xs = [xf(h) for h in H80[g]]
        ax.scatter(xs, [PI[g]] * 3, s=20, facecolor="white", edgecolor=COL[g], lw=1.1, zorder=3)
        xm = np.mean(xs); xsd = np.std(xs, ddof=1)
        ax.errorbar(xm, PI[g], xerr=xsd, fmt="s", ms=6.5, color=COL[g], mec="white", mew=0.8,
                    capsize=2.5, lw=1.1, zorder=5)

def figure(path):
    fig = plt.figure(figsize=(7.2, 7.0))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.15], hspace=0.38, wspace=0.32,
                          left=0.095, right=0.985, top=0.965, bottom=0.165)
    ax_a, ax_b, ax_c = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, :])
    pp = np.linspace(0, 0.45, 200)

    # (a) Pi vs log strain -------------------------------------------------------
    ax = ax_a
    scatter_groups(ax, lambda h: -np.log(h))
    e_lin = LIN["s0"] + pp / LIN["K"]
    ax.plot(e_lin, pp, "--", color="#111111", lw=1.4, zorder=2)
    ax.plot(eps_stiff(pp, *pS), pp, "-", color="#9a9a9a", lw=1.1, zorder=1)
    for g, (dx, dy) in {0: (-4, 8), 5: (-24, 6), 10: (-28, 5), 15: (-28, 6)}.items():
        ax.annotate(f"{g}%", (GM[g], PI[g]), xytext=(dx, dy), textcoords="offset points",
                    fontsize=8, color="#333333")
    ax.set_xlim(-0.06, 0.36); ax.set_ylim(-0.03, 0.47)
    ax.set_xlabel(r"Log height strain, $\varepsilon = -\ln(h/h_0)$")
    ax.set_ylabel("PEG osmotic pressure, Π (MPa)")
    leg = [Line2D([], [], ls="--", color="#111111", lw=1.4,
                  label=f"Linear: K = {LIN['K']:.2f} ± {LIN['sK']:.2f} MPa"),
           Line2D([], [], ls="-", color="#9a9a9a", lw=1.1,
                  label=f"K = K$_0$ + αΠ: K$_0$ = {STIFF['K0']:.2f}, α = {STIFF['al']:.1f}")]
    ax.legend(handles=leg, loc="lower right", frameon=False, fontsize=7.0)
    ax.set_title("a", loc="left", fontweight="bold", fontsize=11, x=-0.16)

    # (b) Pi vs h/h0 ------------------------------------------------------------
    ax = ax_b
    scatter_groups(ax, lambda h: h)
    ax.plot(np.exp(-e_lin), pp, "--", color="#111111", lw=1.4, zorder=2)
    ax.plot(1 - (ENGF["s0"] + pp / ENGF["K"]), pp, ":", color="#111111", lw=1.4, zorder=2)
    ax.set_xlim(1.06, 0.70); ax.set_ylim(-0.03, 0.47)
    ax.set_xlabel(r"Relative height, $h/h_0$ (80 h)")
    ax.set_ylabel("PEG osmotic pressure, Π (MPa)")
    leg = [Line2D([], [], ls="--", color="#111111", lw=1.4, label="Linear in ε (panel a)"),
           Line2D([], [], ls=":", color="#111111", lw=1.4,
                  label=f"Linear in 1 − h/h$_0$: K = {ENGF['K']:.2f} MPa")]
    ax.legend(handles=leg, loc="upper left", frameon=False, fontsize=7.3)
    ax.text(0.98, 0.03, "axis reversed:\ncompression → right", transform=ax.transAxes, ha="right",
            va="bottom", fontsize=7, color=NOTE)
    ax.set_title("b", loc="left", fontweight="bold", fontsize=11, x=-0.16)

    # (c) benchmarks --------------------------------------------------------------
    ax = ax_c
    xs, x, prev = [], 0.0, None
    for grp, *_ in BENCH:
        if prev is not None and grp != prev:
            x += 0.6
        xs.append(x); x += 1.0; prev = grp
    lo_c, hi_c = BENCH[0][2], BENCH[0][3]
    ax.axhspan(lo_c, hi_c, color="#111111", alpha=0.08, lw=0, zorder=0)
    ax.axhline(LIN["K"], color="#111111", lw=0.7, ls="--", alpha=0.6, zorder=0)
    for xi, (grp, lab, lo, hi, kind, c) in zip(xs, BENCH):
        filled = kind == "osm"
        if hi > lo * 1.001:
            ax.plot([xi, xi], [lo, hi], color=c, lw=7, alpha=0.30 if filled else 0.0,
                    solid_capstyle="butt", zorder=2)
            if not filled:
                ax.plot([xi, xi], [lo, hi], color=c, lw=1.2, zorder=2)
                ax.plot([xi - 0.13, xi + 0.13], [lo, lo], color=c, lw=1.2)
                ax.plot([xi - 0.13, xi + 0.13], [hi, hi], color=c, lw=1.2)
        mid = LIN["K"] if xi == xs[0] else (0.38 if "cartilage" in lab else np.sqrt(lo * hi))
        ax.plot(xi, mid, "o" if filled else "D", ms=7 if xi == xs[0] else 6,
                mfc=c if filled else "white", mec="white" if filled else c, mew=1.2 if not filled else 0.8,
                zorder=4)
    # group labels
    grp_pos = {}
    for xi, (grp, *_r) in zip(xs, BENCH):
        grp_pos.setdefault(grp, []).append(xi)
    for grp, pos in grp_pos.items():
        ax.text(np.mean(pos), 22, grp, ha="center", va="bottom", fontsize=7.2, color="#333333",
                fontweight="bold")
        if len(pos) > 1:
            ax.plot([min(pos) - 0.35, max(pos) + 0.35], [19, 19], color="#999999", lw=0.8)
    ax.set_xticks(xs)
    ax.set_xticklabels([b[1] for b in BENCH], fontsize=7.2, rotation=35, ha="right",
                       rotation_mode="anchor")
    ax.set_yscale("log"); ax.set_ylim(5e-5, 60)
    ax.set_xlim(xs[0] - 1.0, xs[-1] + 0.9)
    ax.set_ylabel("Modulus (MPa)")
    ax.yaxis.grid(True, which="major", color="#e6e6e6", lw=0.6); ax.set_axisbelow(True)
    leg = [Line2D([], [], marker="o", ls="", mfc="#6b6b6b", mec="white", ms=6.5,
                  label="Osmotic / compressive modulus  K = c ∂Π/∂c"),
           Line2D([], [], marker="D", ls="", mfc="white", mec="#6b6b6b", mew=1.2, ms=6,
                  label="Shear modulus G′ (for scale)")]
    ax.legend(handles=leg, loc="lower left", frameon=False, fontsize=7.3)
    ax.text(xs[0] + 0.45, LIN["K"] * 1.25, f"{LIN['K']:.2f} MPa", fontsize=7.4, color="#111111", va="bottom")
    ax.set_title("c", loc="left", fontweight="bold", fontsize=11, x=-0.065)

    fig.savefig(path + ".png", dpi=300)
    fig.savefig(path + ".pdf")
    plt.close(fig)

def si_figure(path):
    fig, axs = plt.subplots(2, 3, figsize=(7.2, 4.9), sharex=True)
    mk = ["o", "^", "D"]
    for ax, g in zip(axs.flat[:5], [0, 5, 10, 15, 20]):
        ax.axhline(1, color="#bbbbbb", lw=0.6, ls="--", zorder=0)
        for i, tr in enumerate(H[g]):
            excl = g == 20 and i in EXCLUDED_20
            ax.plot(TIMES, tr, ls=":" if excl else "-", marker=mk[i], ms=3.6, lw=1.0,
                    color=["#0072B2", "#D55E00", "#009E73"][i], mfc="white" if excl else None,
                    label=f"Sample {i+1}" + (" (excluded)" if excl else ""))
        ax.set_ylim(0.3, 1.12)
        ttl = f"{g}% PEG" + (f"  (Π = {PI[g]:.3f} MPa)" if g in PI else f"  (Π ≈ {PI_20:.2f} MPa*)")
        ax.set_title(ttl, fontsize=8.5)
        if g == 20:
            ax.legend(frameon=False, fontsize=6.6, loc="center right")
            ax.text(0.97, 0.30, "not used for the modulus\n* Π extrapolated", transform=ax.transAxes, ha="right",
                    va="top", fontsize=6.8, color=NOTE)
    ax = axs.flat[5]
    ax.axhline(1, color="#bbbbbb", lw=0.6, ls="--", zorder=0)
    for g in GROUPS:
        arr = np.array(H[g]); m = arr.mean(0); s = arr.std(0, ddof=1)
        ax.fill_between(TIMES, m - s, m + s, color=COL[g], alpha=0.15, lw=0)
        ax.plot(TIMES, m, "-o", ms=3.2, lw=1.2, color=COL[g], label=f"{g}%")
    ax.set_ylim(0.6, 1.08)
    ax.set_title("0–15% PEG, mean ± SD (n = 3)", fontsize=8.5)
    ax.legend(frameon=False, fontsize=6.8, ncol=4, loc="lower right", columnspacing=1.0,
              handlelength=1.6)
    for i, ax in enumerate(axs.flat):
        ax.set_xticks([0, 20, 40, 60, 80])
        ax.text(-0.2, 1.06, "abcdef"[i], transform=ax.transAxes, fontweight="bold", fontsize=10)
        if i % 3 == 0:
            ax.set_ylabel(r"Relative height, $h/h_0$")
        if i >= 3:
            ax.set_xlabel("Time (h)")
    fig.tight_layout(h_pad=1.2, w_pad=1.0)
    fig.savefig(path + ".png", dpi=300)
    fig.savefig(path + ".pdf")
    plt.close(fig)

if __name__ == "__main__":
    txt = report()
    print(txt)
    with open(os.path.join(HERE, "results.md"), "w") as fh:
        fh.write(txt + "\n")
    figure(os.path.join(HERE, "coacervate_osmotic_modulus"))
    si_figure(os.path.join(HERE, "SI_raw_trajectories"))

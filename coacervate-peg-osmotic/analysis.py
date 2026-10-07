"""
PDDA/BSA coacervate layer compressed by PEG osmotic stress: osmotic modulus.

Run:  python3 analysis.py   -> prints tables, writes results.md + figure (png/pdf)
All inputs are at the top of the file; change them and re-run.

Physics
-------
The coacervate layer sits in a well and only its height can change, so
V/V0 = h/h0. At equilibrium the coacervate's own osmotic pressure balances the
PEG reservoir, so the PEG pressure maps out the coacervate equation of state.
The osmotic (compression) modulus is

    K_osm = c dPi/dc = -dPi/d ln V = dPi/d eps,   eps = -ln(h/h0).

K_osm is the slope of Pi against eps. PEG pressure is the controlled variable and
eps is what is measured (and scatters), so the primary fit regresses eps on Pi
and inverts the slope. Regressing Pi on eps instead, as the original panel did,
biases K slightly when eps scatters.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------------
# 1. INPUTS
# ----------------------------------------------------------------------------
# h/h0 at t = 80 h for each sample, digitised from the per-sample trajectory
# panels (marker centroids, axis calibrated on the tick marks, ~0.005 reading
# error). Group means agree with panel A to within 0.002.
H80 = {
    0:  [1.017, 1.010, 1.018],
    5:  [1.005, 0.924, 0.958],
    10: [0.889, 0.831, 0.826],
    15: [0.763, 0.740, 0.780],
    20: [0.367, 0.882, 0.385],   # sample 2 (0.882) excluded, see EXCLUDE
}
EXCLUDE = {(20, 1)}              # (PEG %, sample index 0-based): 20% sample 2

# Nominal PEG osmotic pressure (MPa), read off the original panel B.
PI_NOMINAL = {0: 0.0, 5: 0.052, 10: 0.181, 15: 0.412}

# 20% was not in the original panel, so its pressure is extrapolated with the
# Rand-type empirical form log10 Pi = a + b w^0.21 fitted to 5/10/15%.
# REPLACE with the value from your own PEG calibration if you have it.
PI_20_OVERRIDE = None            # e.g. 0.80 (MPa)

T = 298.15
KB = 1.380649e-23
NA = 6.02214e23
WATER_K = 2.2e3                  # MPa, adiabatic/isothermal bulk modulus of water ~2.2 GPa

# Concentrated BSA reference: Carnahan-Starling hard spheres (M = 66.4 kDa) with
# an effective (hydrated, charge-swollen) specific volume v_eff. 1.2-1.5 mL/g
# brackets the range used to describe BSA osmotic pressure in 0.15 M NaCl near
# neutral pH (Minton's effective-hard-particle analysis of Vilker et al. 1981).
BSA_M = 66.4                     # kg/mol
BSA_VEFF = (1.2e-3, 1.5e-3)      # m^3/kg
BSA_C = [100, 200, 300, 400]     # g/L

COL = {0: "#555555", 5: "#0072B2", 10: "#E69F00", 15: "#009E73", 20: "#CC79A7"}

# ----------------------------------------------------------------------------
# 2. PRESSURES
# ----------------------------------------------------------------------------
w = np.array([5, 10, 15], float)
logPi = np.log10([PI_NOMINAL[k] for k in (5, 10, 15)])
A = np.vstack([np.ones(3), w**0.21]).T
(rand_a, rand_b), *_ = np.linalg.lstsq(A, logPi, rcond=None)
def pi_rand(wt):
    return 10 ** (rand_a + rand_b * np.asarray(wt, float) ** 0.21)
pw_n, pw_lnA = np.polyfit(np.log(w), np.log(10**logPi), 1)
PI_20_RAND = float(pi_rand(20))
PI_20_POW = float(np.exp(pw_lnA) * 20**pw_n)
PI = dict(PI_NOMINAL)
PI[20] = PI_20_OVERRIDE if PI_20_OVERRIDE is not None else PI_20_RAND

# PEG solution's own osmotic modulus, K = c dPi/dc ~ w dPi/dw (Rand form)
def k_peg(wt):
    return pi_rand(wt) * np.log(10) * rand_b * 0.21 * np.asarray(wt, float) ** 0.21

# ----------------------------------------------------------------------------
# 3. FITS
# ----------------------------------------------------------------------------
def points(groups, drop=EXCLUDE):
    P, E, G = [], [], []
    for g in groups:
        for i, h in enumerate(H80[g]):
            if (g, i) in drop:
                continue
            P.append(PI[g]); E.append(-np.log(h)); G.append(g)
    return np.array(P), np.array(E), np.array(G)

def ols(x, y):
    """y = m x + b, with standard errors."""
    n = len(x)
    X = np.vstack([x, np.ones(n)]).T
    (m, b), *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - (m * x + b)
    s2 = r @ r / (n - 2)
    cov = s2 * np.linalg.inv(X.T @ X)
    r2 = 1 - r @ r / np.sum((y - y.mean()) ** 2)
    return m, b, np.sqrt(cov[0, 0]), np.sqrt(cov[1, 1]), r2

T975 = {1: 12.71, 2: 4.30, 10: 2.23, 12: 2.18}   # Student t, two-sided 95%

def fit_set(groups, label):
    P, E, G = points(groups)
    # primary: eps = Pi / K + eps0  ->  K = 1/m
    m, e0, sm, _, r2 = ols(P, E)
    K = 1 / m
    sK = sm / m**2
    dof = len(P) - 2
    ci = T975.get(dof, 2.2) * sK
    # as in the original panel: Pi on eps, group means
    gm = np.array([np.mean([e for e, gg in zip(E, G) if gg == g]) for g in groups])
    Km, _, _, _, r2m = ols(gm, np.array([PI[g] for g in groups]))
    # same thing on individual samples
    Ki, _, _, _, _ = ols(E, P)
    return dict(label=label, groups=groups, n=len(P), K=K, sK=sK, ci=ci, e0=e0,
                r2=r2, K_means=Km, r2_means=r2m, K_indiv_PionEps=Ki, P=P, E=E, G=G)

FITS = [fit_set([0, 5, 10, 15], "0-15% PEG"),
        fit_set([0, 5, 10, 15, 20], "0-20% PEG (20% sample 2 excluded)")]

# group means and step (tangent) moduli between neighbouring concentrations
GROUPS = [0, 5, 10, 15, 20]
def gmean(g):
    return np.mean([-np.log(h) for i, h in enumerate(H80[g]) if (g, i) not in EXCLUDE])
def gsd(g):
    return np.std([-np.log(h) for i, h in enumerate(H80[g]) if (g, i) not in EXCLUDE], ddof=1)
EPS = {g: gmean(g) for g in GROUPS}
STEP = [(a, b, (PI[b] - PI[a]) / (EPS[b] - EPS[a])) for a, b in zip(GROUPS[:-1], GROUPS[1:])]
SECANT = {g: PI[g] / (EPS[g] - EPS[0]) for g in GROUPS[1:]}

# BSA reference
def bsa_K(c_gL, veff):
    c = c_gL                                   # kg/m^3
    phi = c * veff
    n = c / BSA_M * NA
    dphiZ = (1 + 4*phi + 4*phi**2 - 4*phi**3 + phi**4) / (1 - phi) ** 4
    Z = (1 + phi + phi**2 - phi**3) / (1 - phi) ** 3
    return n * KB * T * dphiZ / 1e6, n * KB * T * Z / 1e6, phi   # MPa, MPa
BSA = {c: [bsa_K(c, v) for v in BSA_VEFF] for c in BSA_C}

# ----------------------------------------------------------------------------
# 4. REPORT
# ----------------------------------------------------------------------------
def report():
    L = []
    L.append("# Osmotic modulus of the PDDA/BSA coacervate under PEG stress\n")
    L.append("## Inputs (h/h0 at 80 h, digitised)\n")
    L.append("| PEG | Pi (MPa) | sample 1 | sample 2 | sample 3 | mean eps = -ln(h/h0) | SD |")
    L.append("|---|---|---|---|---|---|---|")
    for g in GROUPS:
        hs = [f"~~{h:.3f}~~ (excluded)" if (g, i) in EXCLUDE else f"{h:.3f}" for i, h in enumerate(H80[g])]
        src = " (extrapolated)" if g == 20 and PI_20_OVERRIDE is None else ""
        L.append(f"| {g}% | {PI[g]:.3f}{src} | " + " | ".join(hs) + f" | {EPS[g]:.3f} | {gsd(g):.3f} |")
    L.append("")
    L.append(f"Pi(20%) extrapolation: Rand form log10 Pi = {rand_a:.2f} + {rand_b:.2f} w^0.21 "
             f"gives {PI_20_RAND:.2f} MPa; a pure power law (Pi ~ w^{pw_n:.2f}) gives {PI_20_POW:.2f} MPa.\n")
    L.append("## Osmotic modulus K = dPi/d(-ln h)\n")
    L.append("| Data set | n | K (MPa), eps-on-Pi fit | 95% CI | R² | K, Pi-on-eps on means (original method) |")
    L.append("|---|---|---|---|---|---|")
    for f in FITS:
        L.append(f"| {f['label']} | {f['n']} | **{f['K']:.2f}** ± {f['sK']:.2f} | "
                 f"{f['K']-f['ci']:.2f} to {f['K']+f['ci']:.2f} | {f['r2']:.2f} | {f['K_means']:.2f} (R² {f['r2_means']:.2f}) |")
    L.append("")
    L.append("## Local (step) moduli between neighbouring concentrations\n")
    L.append("| Step | dPi (MPa) | d eps | K_step (MPa) |")
    L.append("|---|---|---|---|")
    for a, b, k in STEP:
        L.append(f"| {a}% to {b}% | {PI[b]-PI[a]:.3f} | {EPS[b]-EPS[a]:.3f} | {k:.2f} |")
    L.append("")
    L.append("## Reference osmotic moduli (MPa)\n")
    L.append("| System | K_osm (MPa) |")
    L.append("|---|---|")
    for wt in (5, 10, 15, 20):
        L.append(f"| PEG solution {wt}% (from the same Pi(w) curve) | {float(k_peg(wt)):.2f} |")
    for c in BSA_C:
        (k1, p1, f1), (k2, p2, f2) = BSA[c]
        L.append(f"| BSA {c} g/L, hard-sphere (phi_eff {f1:.2f}-{f2:.2f}; Pi {p1:.3f}-{p2:.3f} MPa) | {k1:.2f} to {k2:.2f} |")
    L.append(f"| Liquid water, bulk modulus | {WATER_K:.0f} |")
    return "\n".join(L)

# ----------------------------------------------------------------------------
# 5. FIGURE
# ----------------------------------------------------------------------------
def figure(path):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.linewidth": 0.8})
    fig, axs = plt.subplots(1, 3, figsize=(13.2, 4.3), gridspec_kw=dict(width_ratios=[1.25, 0.9, 1.15]))
    f15, f20 = FITS

    # (a) Pi vs eps -------------------------------------------------------------
    ax = axs[0]
    for g in GROUPS:
        for i, h in enumerate(H80[g]):
            e = -np.log(h)
            if (g, i) in EXCLUDE:
                ax.scatter(e, PI[g], s=36, marker="x", color=COL[g], lw=1.4, zorder=4)
                ax.annotate("20% sample 2\n(excluded)", (e, PI[g]), xytext=(6, -16),
                            textcoords="offset points", fontsize=7.5, color="#555555")
                continue
            ax.scatter(e, PI[g], s=22, facecolor="white", edgecolor=COL[g], lw=1.1, zorder=3)
        ax.errorbar(EPS[g], PI[g], xerr=gsd(g), fmt="s", ms=7, color=COL[g],
                    mec="white", mew=0.8, capsize=3, lw=1.2, zorder=5)
        lab = f"{g}%" + ("*" if g == 20 and PI_20_OVERRIDE is None else "")
        off = {0: (6, -10), 5: (10, 6), 10: (10, 6), 15: (10, 6), 20: (-8, 10)}[g]
        ax.annotate(lab, (EPS[g], PI[g]), xytext=off, textcoords="offset points",
                    color="#333333", fontsize=9)
    xx = np.linspace(-0.05, 1.05, 50)
    for f, ls, c in [(f15, "--", "#222222"), (f20, ":", COL[20])]:
        x = np.linspace(min(f["E"]) - 0.02, max(f["E"]) + 0.02, 50)
        ax.plot(x, f["K"] * (x - f["e0"]), ls, color=c, lw=1.6,
                label=f"{f['label']}: K = {f['K']:.2f} ± {f['sK']:.2f} MPa")
    ax.set_xlabel(r"Logarithmic height strain, $\varepsilon=-\ln(h/h_0)$ at 80 h")
    ax.set_ylabel("PEG osmotic pressure, Π (MPa)")
    ax.set_xlim(-0.06, 1.08); ax.set_ylim(-0.04, 0.95)
    ax.axhline(0, color="#bbbbbb", lw=0.6, zorder=0); ax.axvline(0, color="#bbbbbb", lw=0.6, zorder=0)
    ax.legend(loc="upper left", frameon=False, fontsize=8)
    ax.text(0.99, 0.02, "open circles: single samples\nsquares: mean ± SD (n = 3; 20%: n = 2)\n"
            "* Π(20%) extrapolated", transform=ax.transAxes, ha="right", va="bottom",
            fontsize=7.5, color="#555555")
    ax.set_title("a  Equation of state from osmotic compression", loc="left", fontweight="bold")

    # (b) moduli ----------------------------------------------------------------
    ax = axs[1]
    labels, vals, errs, cols = [], [], [], []
    for f, c in [(f15, "#222222"), (f20, COL[20])]:
        labels.append("Fit 0–15%" if f is f15 else "Fit 0–20%\n(excl. S2)")
        vals.append(f["K"]); errs.append(f["ci"]); cols.append(c)
    for a, b, k in STEP:
        labels.append(f"{a}→{b}%"); vals.append(k); errs.append(0); cols.append(COL[b])
    y = np.arange(len(labels))[::-1]
    for yi, v, e, c in zip(y, vals, errs, cols):
        ax.plot([0, v], [yi, yi], color=c, lw=2, solid_capstyle="round", alpha=0.35)
        ax.errorbar(v, yi, xerr=e if e else None, fmt="o", ms=7, color=c, mec="white", capsize=3)
        ax.text(v + (e if e else 0) + 0.06, yi, f"{v:.2f}", va="center", fontsize=8.5, color="#333333")
    ax.axhline(y[1] - 0.5, color="#cccccc", lw=0.8)
    ax.set_yticks(y); ax.set_yticklabels(labels)
    ax.set_xlim(0, 3.4)
    ax.set_xlabel("Osmotic modulus K = dΠ/dε (MPa)")
    ax.text(0.98, 0.03, "global fits: ±95% CI\nsteps: between group means", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=7.5, color="#555555")
    ax.set_title("b  Modulus, global and local", loc="left", fontweight="bold")

    # (c) comparison --------------------------------------------------------------
    ax = axs[2]
    rows = []
    rows.append(("Liquid water (bulk)", WATER_K, WATER_K, "#999999"))
    for c in BSA_C[::-1]:
        k = [BSA[c][0][0], BSA[c][1][0]]
        rows.append((f"BSA {c} g/L (hard-sphere)", min(k), max(k), "#8c6d31"))
    for wt in (20, 15, 10, 5):
        k = float(k_peg(wt)); rows.append((f"PEG {wt}% solution", k, k, "#7f7f7f"))
    rows.append(("Coacervate, fit 0–20%", f20["K"] - f20["ci"], f20["K"] + f20["ci"], COL[20]))
    rows.append(("Coacervate, fit 0–15%", f15["K"] - f15["ci"], f15["K"] + f15["ci"], "#222222"))
    rows = rows[::-1]
    for i, (lab, lo, hi, c) in enumerate(rows):
        yi = len(rows) - 1 - i
        if hi > lo:
            ax.plot([lo, hi], [yi, yi], color=c, lw=6, solid_capstyle="round", alpha=0.55)
        mid = np.sqrt(lo * hi)
        ax.plot(mid, yi, "o", ms=6, color=c, mec="white")
    ax.set_yticks(range(len(rows))[::-1]); ax.set_yticklabels([r[0] for r in rows])
    ax.set_xscale("log"); ax.set_xlim(3e-3, 1e4)
    ax.axvspan(FITS[0]["K"] - FITS[0]["ci"], FITS[0]["K"] + FITS[0]["ci"], color="#222222", alpha=0.07, lw=0)
    ax.set_xlabel("Osmotic (compression) modulus, K = c ∂Π/∂c (MPa)")
    ax.text(0.60, 0.62, "BSA: Carnahan–Starling\nhard spheres, 66.4 kDa,\nv_eff = 1.2–1.5 mL/g\n(bar = range)\n\nPEG: K from the same\nΠ(w) curve as panel a",
            transform=ax.transAxes, ha="left", va="center", fontsize=7, color="#555555")
    ax.set_title("c  How stiff is ~1 MPa?", loc="left", fontweight="bold")

    fig.tight_layout()
    fig.savefig(path + ".png", dpi=300)
    fig.savefig(path + ".pdf")

if __name__ == "__main__":
    txt = report()
    print(txt)
    with open("results.md", "w") as fh:
        fh.write(txt + "\n")
    figure("coacervate_osmotic_modulus")

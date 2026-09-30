"""
PEGDA 5K / 10K / 20K hydrogels: what can G'(Q) tell us about load-bearing
strands, and how does it compare with FLICK junction fluctuations?

Run:  python3 analysis.py      -> prints tables, writes results.md + figure
All inputs are at the top of the file; change them and re-run.
"""
import numpy as np
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# ----------------------------------------------------------------------------
# 1. INPUTS
# ----------------------------------------------------------------------------
# G' (Pa) vs Q, digitised from the Origin plots (pixel centroids of markers,
# axis calibrated on the tick marks; reading error ~0.02 in Q, ~40 Pa in G').
DATA = {
    5000:  dict(Q=[11.32, 16.39, 18.72, 20.07], G=[15051, 10058, 8779, 5952]),
    10000: dict(Q=[11.32, 17.63, 23.03, 26.39], G=[8707, 5044, 3796, 2930]),
    20000: dict(Q=[11.31, 19.36, 26.50, 37.41], G=[4941, 4549, 3208, 1496]),
}
# FLICK junction fluctuation, sigma (nm). Interpreted as the per-axis (1-D)
# rms displacement of a labelled junction about its mean position.
FLICK_SIGMA = {5000: 12.58, 10000: 14.73, 20000: 16.09}

RHO = 1.12e3          # kg/m^3, PEG density
T = 298.15            # K
R_GAS = 8.314         # J/mol/K
KB = 1.380649e-23     # J/K
NA = 6.02214e23
C_THETA = 0.805e-2    # nm^2 mol/g : <R0^2>/M for PEO, unperturbed (Rubinstein & Colby, Table 2.1)
# PEG in water (good solvent): Rg = 0.0215 M^0.583 nm (Devanand & Selser, Macromolecules 1991)
def re_good(M):
    return np.sqrt(6) * 0.0215 * np.asarray(M, float) ** 0.583
def re_theta(M):
    return np.sqrt(C_THETA * np.asarray(M, float))

MNS = sorted(DATA)
RT = R_GAS * T
RHO_RT = RHO * RT     # Pa * (kg/mol)

# ----------------------------------------------------------------------------
# 2. FITS OF G'(Q)
# ----------------------------------------------------------------------------
def fit_inverse_Q(Q, G):
    """G = a/Q (b fixed at -1), unweighted LSQ, as Origin 'Allometric1, b=-1'."""
    x = 1.0 / Q
    a = np.sum(G * x) / np.sum(x * x)
    res = G - a * x
    se = np.sqrt(np.sum(res**2) / (len(G) - 1) / np.sum(x * x))
    r2 = 1 - np.sum(res**2) / np.sum((G - G.mean()) ** 2)
    return a, se, r2

def fit_free_power(Q, G):
    """G = a Q^b with b free (nonlinear, linear-space residuals)."""
    p, cov = curve_fit(lambda q, a, b: a * q**b, Q, G, p0=(G[0] * Q[0], -1.0), maxfev=20000)
    return p, np.sqrt(np.diag(cov))

R = {}
for Mn in MNS:
    Q = np.array(DATA[Mn]["Q"], float)
    G = np.array(DATA[Mn]["G"], float)
    a, a_se, r2 = fit_inverse_Q(Q, G)
    (a_free, b_free), (_, b_se) = fit_free_power(Q, G)
    R[Mn] = dict(Q=Q, G=G, a=a, a_se=a_se, r2=r2, b_free=b_free, b_se=b_se, a_free=a_free)

# ----------------------------------------------------------------------------
# 3. EFFECTIVE (LOAD-BEARING) STRANDS
# ----------------------------------------------------------------------------
# G = a/Q = a*phi  <=>  G = nu_e RT phi, i.e. every gel in a series has the same
# dry-state density of elastically effective strands nu_e = a/RT, and the
# strands are unstretched in the measured state (your "Q = 1" convention).
# Affine: Mc = rho RT / a.  Phantom: G = (1-2/f) nu_e RT phi -> Mc = (1-2/f) rho RT/a.
# NOTE: Flory's (1 - 2Mc/Mn) end correction is dropped - it describes random
# cross-linking of long primary chains (Mn >> Mc). In PEGDA the PEG chain IS the
# strand (Mc ~ Mn), and that factor goes to zero / negative.
for Mn in MNS:
    r = R[Mn]
    r["nu_dry"] = r["a"] / RT                      # mol/m^3 of dry polymer
    r["Mc_aff"] = RHO_RT / r["a"] * 1e3            # g/mol
    r["Mc_aff_se"] = r["Mc_aff"] * r["a_se"] / r["a"]
    r["Mc_ph4"] = 0.5 * r["Mc_aff"]
    r["Mc_pts"] = RHO_RT / (r["G"] * r["Q"]) * 1e3  # per-sample, same convention
    r["N_series_aff"] = r["Mc_aff"] / Mn           # PEG chains per effective strand
    r["N_series_ph4"] = r["Mc_ph4"] / Mn
    r["omega_aff"] = Mn / r["Mc_aff"]              # fraction of PEG chains load-bearing
    r["omega_ph4"] = Mn / r["Mc_ph4"]

# ----------------------------------------------------------------------------
# 4. LENGTH SCALES
# ----------------------------------------------------------------------------
for Mn in MNS:
    r = R[Mn]
    # (i) model-free rubber-elastic mesh size, per sample: xi = (kT/G)^(1/3)
    r["xi_G"] = (KB * T / r["G"]) ** (1 / 3) * 1e9
    # (ii) effective strand size (unperturbed Gaussian and water-swollen)
    r["R_eff_th_aff"] = float(re_theta(r["Mc_aff"]))
    r["R_eff_th_ph4"] = float(re_theta(r["Mc_ph4"]))
    r["R_eff_gs_aff"] = float(re_good(r["Mc_aff"]))
    # (iii) Canal-Peppas mesh size per sample: xi = Q^(1/3) * R0(Mc)
    r["xi_CP"] = r["Q"] ** (1 / 3) * r["R_eff_th_aff"]
    # precursor
    r["Re_prec_th"] = float(re_theta(Mn))
    r["Re_prec_gs"] = float(re_good(Mn))

# ----------------------------------------------------------------------------
# 5. JUNCTION FLUCTUATIONS (phantom network, tree model)
# ----------------------------------------------------------------------------
# Junction of functionality f, strands with <R0^2>:
#   <dr^2>_junction = (f-1)/(f(f-2)) R0^2       (per axis: divide by 3)
#   <dR^2>_strand   = (2/f) R0^2                 (end-to-end vector fluctuation)
# Fluctuations of Gaussian phantom strands do not depend on deformation/swelling.
# Affine network: junctions pinned, sigma = 0.
# Using the strand mass that the SAME G' implies for that f, Mc(f) = (1-2/f) Mc_aff:
#   sigma_1D^2 = C * Mc_aff * (f-1)/(3 f^2)  -> maximal at f = 3 (for f >= 3).
def sigma_phantom_1D(Mc_aff, f, R2_over_M=C_THETA):
    Mc_f = (1 - 2 / f) * Mc_aff
    return np.sqrt(R2_over_M * Mc_f * (f - 1) / (3 * f * (f - 2)))

for Mn in MNS:
    r = R[Mn]
    gs_boost = r["R_eff_gs_aff"] / r["R_eff_th_aff"]   # water-swollen strand upper bound
    r["sigJ_f3"] = float(sigma_phantom_1D(r["Mc_aff"], 3))
    r["sigJ_f4"] = float(sigma_phantom_1D(r["Mc_aff"], 4))
    r["sigJ_f10"] = float(sigma_phantom_1D(r["Mc_aff"], 10))
    r["sigJ_f3_gs"] = r["sigJ_f3"] * gs_boost
    r["sigJ_f4_gs"] = r["sigJ_f4"] * gs_boost
    s = FLICK_SIGMA[Mn]
    r["flick"] = s
    # heterogeneity index H = (sigma_FLICK / sigma_phantom)^2 = <k><1/k> estimate
    r["H_f4_th"] = (s / r["sigJ_f4"]) ** 2
    r["H_f4_gs"] = (s / r["sigJ_f4_gs"]) ** 2
    r["H_f4_th_3D"] = (s / np.sqrt(3) / r["sigJ_f4"]) ** 2
    # strand mass FLICK would imply in a homogeneous phantom network, f = 4 and f = 3
    r["M_flick_f4"] = s**2 * 3 * 4 * 2 / 3 / C_THETA
    r["M_flick_f3"] = s**2 * 3 * 3 * 1 / 2 / C_THETA

# FLICK variance vs rheological strand mass: sigma^2 = sigma0^2 + alpha * Mc_aff
x = np.array([R[m]["Mc_aff"] for m in MNS])
y = np.array([FLICK_SIGMA[m] ** 2 for m in MNS])
alpha, s0sq = np.polyfit(x, y, 1)
r2_mc = 1 - np.sum((y - (alpha * x + s0sq)) ** 2) / np.sum((y - y.mean()) ** 2)
xm = np.array(MNS, float)
alpha_mn, s0sq_mn = np.polyfit(xm, y, 1)
r2_mn = 1 - np.sum((y - (alpha_mn * xm + s0sq_mn)) ** 2) / np.sum((y - y.mean()) ** 2)
alpha_th = {f: C_THETA * (f - 1) / (3 * f**2) for f in (3, 4, 10)}

def slope_loglog(xs, ys):
    return np.polyfit(np.log(xs), np.log(ys), 1)[0]

EXP = dict(
    Mc=slope_loglog(MNS, [R[m]["Mc_aff"] for m in MNS]),
    flick=slope_loglog(MNS, [FLICK_SIGMA[m] for m in MNS]),
    Reff=slope_loglog(MNS, [R[m]["R_eff_th_aff"] for m in MNS]),
    xiG=slope_loglog(MNS, [np.median(R[m]["xi_G"]) for m in MNS]),
)

# ----------------------------------------------------------------------------
# 6. REPORT
# ----------------------------------------------------------------------------
def fmt(v, n=1):
    return f"{v:,.{n}f}"

lines = []
P = lines.append
P("# PEGDA rheology -> load-bearing strands -> comparison with FLICK\n")
P(f"Constants: rho = {RHO/1e3:.2f} g/cm3, T = {T:.2f} K (rho*RT = {RHO_RT/1e6:.3f} MPa kg/mol), "
  f"<R0^2>/M(PEO, theta) = {C_THETA*100:.3f} A^2 mol/g, PEG/water Rg = 0.0215 M^0.583 nm.\n")
P("## 1. Fits of G'(Q)\n")
P("| Mn | a = G'(Q=1) from G=a/Q (Pa) | R^2 | free exponent b in G=aQ^b |")
P("|---|---|---|---|")
for Mn in MNS:
    r = R[Mn]
    P(f"| {Mn} | {fmt(r['a'],0)} ± {fmt(r['a_se'],0)} | {r['r2']:.3f} | {r['b_free']:.2f} ± {r['b_se']:.2f} |")
P("\n## 2. Effective (load-bearing) strands\n")
P("| Mn | nu_e dry (mol/m3) | Mc,eff affine (g/mol) | Mc,eff phantom f=4 | Mc/Mn affine | Mc/Mn phantom | load-bearing fraction omega (aff / ph4) | per-sample Mc,aff (g/mol) |")
P("|---|---|---|---|---|---|---|---|")
for Mn in MNS:
    r = R[Mn]
    pts = ", ".join(fmt(v, 0) for v in r["Mc_pts"])
    P(f"| {Mn} | {fmt(r['nu_dry'],1)} | {fmt(r['Mc_aff'],0)} ± {fmt(r['Mc_aff_se'],0)} | {fmt(r['Mc_ph4'],0)} | "
      f"{r['N_series_aff']:.2f} | {r['N_series_ph4']:.2f} | {r['omega_aff']:.2f} / {min(r['omega_ph4'],1):.2f} | {pts} |")
P("\n## 3. Length scales (nm)\n")
P("| Mn | precursor Re theta / water | eff. strand R0 theta (aff; ph4) | eff. strand Re water (aff) | mesh xi=(kT/G)^1/3 range | Canal-Peppas xi range |")
P("|---|---|---|---|---|---|")
for Mn in MNS:
    r = R[Mn]
    P(f"| {Mn} | {r['Re_prec_th']:.2f} / {r['Re_prec_gs']:.2f} | {r['R_eff_th_aff']:.2f}; {r['R_eff_th_ph4']:.2f} | "
      f"{r['R_eff_gs_aff']:.2f} | {r['xi_G'].min():.1f}-{r['xi_G'].max():.1f} | {r['xi_CP'].min():.1f}-{r['xi_CP'].max():.1f} |")
P("\n## 4. Junction fluctuations: phantom prediction vs FLICK (per-axis sigma, nm)\n")
P("| Mn | phantom f=3 (theta / water) | phantom f=4 (theta / water) | phantom f=10 | affine | FLICK sigma | H = (sigma_FLICK/sigma_ph4)^2 theta / water / FLICK-as-3D | strand mass FLICK implies, f=3 / f=4 (g/mol) |")
P("|---|---|---|---|---|---|---|---|")
for Mn in MNS:
    r = R[Mn]
    P(f"| {Mn} | {r['sigJ_f3']:.2f} / {r['sigJ_f3_gs']:.2f} | {r['sigJ_f4']:.2f} / {r['sigJ_f4_gs']:.2f} | {r['sigJ_f10']:.2f} | 0 | "
      f"{r['flick']:.2f} | {r['H_f4_th']:.1f} / {r['H_f4_gs']:.1f} / {r['H_f4_th_3D']:.1f} | {fmt(r['M_flick_f3'],0)} / {fmt(r['M_flick_f4'],0)} |")
P(f"\nFLICK variance decomposition: sigma^2 = sigma0^2 + alpha*Mc,eff  ->  sigma0 = {np.sqrt(s0sq):.2f} nm, "
  f"alpha = {alpha*1e3:.2f}e-3 nm^2 mol/g, R^2 = {r2_mc:.4f}  (vs Mn instead: R^2 = {r2_mn:.4f}).")
P("Phantom-theory slopes (theta strands): " + ", ".join(f"f={f}: {v*1e3:.2f}e-3" for f, v in alpha_th.items())
  + f"  -> measured/phantom(f=3) = {alpha/alpha_th[3]:.1f}x (1-D), {alpha/3/alpha_th[3]:.1f}x if sigma is 3-D rms.")
P(f"\nScaling with Mn: Mc,eff ~ Mn^{EXP['Mc']:.2f}; R0(Mc,eff) ~ Mn^{EXP['Reff']:.2f}; "
  f"median xi_G ~ Mn^{EXP['xiG']:.2f}; FLICK sigma ~ Mn^{EXP['flick']:.2f}; precursor Re ~ Mn^0.50 (theta) / Mn^0.58 (water).")
report = "\n".join(lines)
print(report)
with open("results.md", "w") as fh:
    fh.write(report + "\n")

# ----------------------------------------------------------------------------
# 7. FIGURE
# ----------------------------------------------------------------------------
COL = {5000: "#2a78d6", 10000: "#eb6834", 20000: "#1baf7a"}
MK = {5000: "s", 10000: "o", 20000: "^"}
LAB = {5000: "PEGDA 5K", 10000: "PEGDA 10K", 20000: "PEGDA 20K"}
FLICK_C = "#4a3aa7"
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8983", "#e4e3de"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8, "axes.titlesize": 9,
    "axes.labelsize": 8.5, "axes.edgecolor": INK2, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.linewidth": 0.8,
    "legend.frameon": False, "legend.fontsize": 7.2, "savefig.dpi": 300,
})
fig, axs = plt.subplots(2, 2, figsize=(7.4, 7.3))
(axA, axB), (axC, axD) = axs
for ax in axs.flat:
    ax.grid(True, color=GRID, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

def tag(ax, t):
    ax.text(-0.14, 1.04, t, transform=ax.transAxes, fontsize=11, fontweight="bold", color=INK, va="bottom")

# (a) data, 1/Q fits, extrapolation distance to Q = 1
qq = np.logspace(0, np.log10(42), 200)
for Mn in MNS:
    r = R[Mn]
    c = COL[Mn]
    qfit = np.linspace(r["Q"].min(), r["Q"].max(), 50)
    axA.plot(qfit, r["a"] / qfit, color=c, lw=1.6, zorder=3)
    axA.plot(qq[qq <= r["Q"].min()], r["a"] / qq[qq <= r["Q"].min()], color=c, lw=1.0, ls=(0, (3, 2)), zorder=2)
    axA.plot(r["Q"], r["G"], MK[Mn], color=c, ms=6.5, mec="white", mew=1.0, zorder=4,
             label=f"{LAB[Mn]}   free fit b = {r['b_free']:.2f}")
    axA.plot([1], [r["a"]], MK[Mn], ms=6.5, mfc="white", mec=c, mew=1.3, zorder=4)
    axA.text(1.12, r["a"], f"{r['a']/1e3:.0f} kPa", color=INK2, va="center", fontsize=7)
axA.set_xscale("log"); axA.set_yscale("log")
axA.set_xlim(0.9, 45); axA.set_ylim(900, 3e5)
axA.set_xlabel("Swelling ratio Q"); axA.set_ylabel("G′ (Pa)")
axA.set_title("Rheology: G′ ∝ 1/Q, extrapolated 10–30× to Q = 1", loc="left", color=INK)
axA.legend(loc="lower left", handletextpad=0.3)
axA.text(0.97, 0.97, "solid: G′ = a/Q fit\ndashed: extrapolation\nopen: a = G′(Q=1)",
         transform=axA.transAxes, ha="right", va="top", fontsize=6.8, color=INK2)
tag(axA, "a")

# (b) how many PEG chains per load-bearing strand
xpos = np.arange(len(MNS))
for i, Mn in enumerate(MNS):
    r = R[Mn]; c = COL[Mn]
    axB.vlines(i, r["N_series_ph4"], r["N_series_aff"], color=c, lw=6, alpha=0.28, zorder=2)
    axB.plot(i, r["N_series_aff"], MK[Mn], color=c, ms=8, mec="white", mew=1, zorder=4)
    axB.plot(i, r["N_series_ph4"], MK[Mn], ms=8, mfc="white", mec=c, mew=1.4, zorder=4)
    jit = np.linspace(-0.16, 0.16, len(r["Mc_pts"]))
    axB.plot(i + 0.28 + jit * 0.4, r["Mc_pts"] / Mn, ".", color=c, ms=4.5, zorder=3)
    axB.text(i - 0.13, r["N_series_aff"], f"{r['N_series_aff']:.1f}×\nω={r['omega_aff']:.2f}",
             ha="right", va="center", fontsize=7, color=INK)
    axB.text(i - 0.13, r["N_series_ph4"] + 0.12, f"{r['N_series_ph4']:.1f}×", ha="right", va="center", fontsize=7, color=INK2)
axB.axhline(1, color=INK2, lw=1, ls=(0, (4, 2)))
axB.text(-0.7, 0.93, "ideal: every PEG chain is one load-bearing strand", ha="left", va="top", fontsize=6.8, color=INK2)
axB.set_xticks(xpos, [LAB[m].replace("PEGDA ", "") for m in MNS])
axB.set_xlim(-0.75, 2.55); axB.set_ylim(0, 4.9)
axB.set_xlabel("PEGDA Mn")
axB.set_ylabel("Mc,eff / Mn")
nlo = min(R[m]["N_series_ph4"] for m in MNS); nhi = max(R[m]["N_series_aff"] for m in MNS)
axB.set_title(f"Strand = {nlo:.1f}–{nhi:.1f} PEG chains in series", loc="left", color=INK)
axB.legend(handles=[
    Line2D([], [], marker="s", ls="", color=INK2, ms=6, label="affine (f → ∞)"),
    Line2D([], [], marker="s", ls="", mfc="white", mec=INK2, ms=6, label="phantom, f = 4"),
    Line2D([], [], marker=".", ls="", color=INK2, ms=6, label="per sample (affine)")],
    loc="upper right", handletextpad=0.3)
tag(axB, "b")

# (c) length-scale ladder
mn = np.array(MNS, float)
mgrid = np.logspace(np.log10(4600), np.log10(22000), 50)
h_prec = axC.fill_between(mgrid, re_theta(mgrid), re_good(mgrid), color=MUTED, alpha=0.22, lw=0, zorder=1)
reff_lo = np.array([R[m]["R_eff_th_ph4"] for m in MNS]); reff_hi = np.array([R[m]["R_eff_gs_aff"] for m in MNS])
reff = np.array([R[m]["R_eff_th_aff"] for m in MNS])
axC.fill_between(mn, reff_lo, reff_hi, color=INK2, alpha=0.12, lw=0, zorder=1)
h_reff, = axC.plot(mn, reff, "-D", color=INK2, ms=4.5, lw=1.4, zorder=3)
xi_med = np.array([np.median(R[m]["xi_G"]) for m in MNS])
for Mn in MNS:
    axC.vlines(Mn, R[Mn]["xi_G"].min(), R[Mn]["xi_G"].max(), color=INK, lw=2.2, alpha=0.55, zorder=3)
h_xi, = axC.plot(mn, xi_med, "_", color=INK, ms=9, mew=1.6, zorder=4)
sj_lo = np.array([R[m]["sigJ_f10"] for m in MNS]); sj_hi = np.array([R[m]["sigJ_f3_gs"] for m in MNS])
sj4 = np.array([R[m]["sigJ_f4"] for m in MNS])
axC.fill_between(mn, sj_lo, sj_hi, color=INK2, alpha=0.08, hatch="////", edgecolor=MUTED, lw=0, zorder=1)
h_sj, = axC.plot(mn, sj4, "--o", color=INK2, ms=4, mfc="white", lw=1.2, zorder=3)
fl = np.array([FLICK_SIGMA[m] for m in MNS])
axC.plot(mn, fl, "-", color=FLICK_C, lw=2, zorder=5)
h_fl, = axC.plot(mn, fl, "o", color=FLICK_C, ms=7, mec="white", mew=1, zorder=6)
h_fl3, = axC.plot(mn, fl / np.sqrt(3), "o", ms=5, mfc="white", mec=FLICK_C, mew=1.2, zorder=6)
axC.set_xscale("log"); axC.set_yscale("log")
axC.set_xlim(4000, 26000); axC.set_ylim(1.5, 40)
axC.set_xticks(mn, ["5K", "10K", "20K"]); axC.minorticks_off()
axC.set_yticks([2, 5, 10, 20], ["2", "5", "10", "20"])
axC.set_xlabel("PEGDA Mn"); axC.set_ylabel("Length (nm)")
rat = [FLICK_SIGMA[m] / R[m]["sigJ_f4_gs"] for m in MNS] + [FLICK_SIGMA[m] / R[m]["sigJ_f4"] for m in MNS]
axC.set_title(f"FLICK σ is {min(rat):.1f}–{max(rat):.1f}× the phantom prediction", loc="left", color=INK)
axC.legend([h_fl, h_fl3, h_reff, h_prec, h_xi, h_sj],
           ["FLICK σ (measured, 1-D)", "FLICK σ/√3 (if 3-D rms)", "effective strand R (from G′)",
            "precursor PEG Re (θ → water)", "mesh ξ = (kT/G′)$^{1/3}$, range over Q",
            "phantom junction σ, f = 4\n(band: f = 10 … f = 3 in water)"],
           loc="upper left", bbox_to_anchor=(-0.02, -0.17), ncol=2, fontsize=6.4, handlelength=1.8,
           labelspacing=0.6, columnspacing=1.0)
axC.text(0.02, 0.97, f"scaling with Mn:  FLICK σ ~ Mn$^{{{EXP['flick']:.2f}}}$,  ξ ~ Mn$^{{{EXP['xiG']:.2f}}}$,\n"
         f"R_eff ~ Mn$^{{{EXP['Reff']:.2f}}}$,  precursor Re ~ Mn$^{{0.50-0.58}}$",
         transform=axC.transAxes, fontsize=6.4, color=INK2, va="top")
tag(axC, "c")

# (d) FLICK variance vs rheological strand mass
xx = np.linspace(0, 52000, 100)
axD.plot(xx, alpha * xx + s0sq, color=FLICK_C, lw=1.6, zorder=3)
axD.axhline(s0sq, color=FLICK_C, lw=0.8, ls=(0, (2, 2)))
axD.text(51000, s0sq - 5, f"strand-independent floor σ₀ = {np.sqrt(s0sq):.1f} nm", color=FLICK_C, fontsize=7, ha="right", va="top")
for f, ls in ((3, "-"), (4, "--")):
    axD.plot(xx, alpha_th[f] * xx, color=INK2, lw=1.1, ls=ls, zorder=2)
    axD.text(51500, alpha_th[f] * 51500 + (4 if f == 3 else -4), f"phantom f = {f}", color=INK2,
             fontsize=6.8, ha="right", va="bottom" if f == 3 else "top")
for Mn in MNS:
    r = R[Mn]
    axD.errorbar(r["Mc_aff"], r["flick"] ** 2, xerr=r["Mc_aff_se"], fmt=MK[Mn], color=COL[Mn], ms=7,
                 mec="white", mew=1, elinewidth=1, capsize=0, zorder=4)
    axD.text(r["Mc_aff"] + 1200, r["flick"] ** 2 - 14, f"{LAB[Mn].split()[1]}\nH ≈ {r['H_f4_gs']:.0f}–{r['H_f4_th']:.0f}",
             fontsize=6.8, color=INK, va="top")
axD.set_xlim(0, 52000); axD.set_ylim(0, 300)
axD.set_xlabel("Mc,eff from rheology, affine (g/mol)")
axD.set_ylabel("FLICK σ² (nm²)")
axD.set_title("FLICK variance tracks Mc,eff", loc="left", color=INK)
axD.text(0.02, 0.97, f"σ² = σ₀² + α·Mc,eff   (R² = {r2_mc:.3f})\n"
         f"α = {alpha/alpha_th[3]:.1f}× the phantom slope (f = 3)",
         transform=axD.transAxes, fontsize=7, color=INK, va="top")
tag(axD, "d")

fig.tight_layout(w_pad=2.2, h_pad=2.0)
fig.subplots_adjust(right=0.97)
fig.savefig("pegda_rheology_vs_flick.png")
fig.savefig("pegda_rheology_vs_flick.pdf")
print("\nfigure written")

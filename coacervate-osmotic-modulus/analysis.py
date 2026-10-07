"""PDDA/BSA coacervate layer under PEG osmotic stress: stiffening equation of state.

Inputs: digitised h/h0 for every sample and time point (Table S1 of the report).
Outputs: fig1_osmotic_modulus.png (panels a, b), figS1_relative_height.png (panels a-f),
         results.json (fit numbers used in the report text).

Run:  python3 analysis.py
"""
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(1)

# ------------------------------------------------------------------ data
TIMES = np.array([0, 2, 5, 8, 21, 32, 44, 68, 80])
H = {  # (PEG %, sample) -> h/h0 at TIMES
    (0, 1): [1.000, 0.977, 1.011, 1.020, 1.019, 0.990, 1.001, 1.007, 1.012],
    (0, 2): [1.000, 1.028, 1.031, 1.020, 1.019, 1.012, 1.001, 1.007, 1.012],
    (0, 3): [1.000, 0.999, 1.003, 1.000, 1.013, 1.028, 1.013, 1.006, 1.021],
    (5, 1): [1.000, 1.042, 1.046, 1.028, 1.010, 1.010, 1.010, 1.003, 1.003],
    (5, 2): [1.000, 0.997, 1.008, 0.990, 0.955, 0.954, 0.928, 0.908, 0.923],
    (5, 3): [1.000, 1.033, 1.018, 1.009, 0.972, 0.982, 0.967, 0.972, 0.959],
    (10, 1): [1.000, 0.965, 0.948, 0.949, 0.903, 0.885, 0.882, 0.879, 0.890],
    (10, 2): [1.000, 0.965, 0.948, 0.917, 0.867, 0.829, 0.821, 0.815, 0.828],
    (10, 3): [1.000, 1.006, 0.967, 0.915, 0.882, 0.851, 0.787, 0.826, 0.826],
    (15, 1): [1.000, 0.900, 0.846, 0.787, 0.760, 0.764, 0.746, 0.751, 0.764],
    (15, 2): [1.000, 0.922, 0.878, 0.842, 0.760, 0.736, 0.746, 0.744, 0.738],
    (15, 3): [1.000, 0.944, 0.877, 0.831, 0.754, 0.726, 0.741, 0.767, 0.779],
    (20, 1): [1.000, 0.882, 0.708, 0.538, 0.390, 0.397, 0.410, 0.391, 0.367],
    (20, 2): [1.000, 0.848, 0.872, 0.854, 0.856, 0.882, 0.887, 0.867, 0.882],
    (20, 3): [1.000, 0.821, 0.651, 0.508, 0.390, 0.377, 0.400, 0.379, 0.385],
}
PI = {0: 0.0, 5: 0.052, 10: 0.181, 15: 0.412, 20: 0.77}   # nominal PEG osmotic pressure, MPa
GROUPS = [0, 5, 10, 15]
COL = {0: "#5b5b5b", 5: "#0072B2", 10: "#E69F00", 15: "#009E73", 20: "#8a5a9e"}
PI_MAX = 1.0                                              # extrapolate the EOS to 1 MPa

pi_all = np.array([PI[g] for g in GROUPS for s in (1, 2, 3)])
eps_all = np.array([-np.log(H[(g, s)][-1]) for g in GROUPS for s in (1, 2, 3)])


# ------------------------------------------------------------------ stiffening EOS
# K = dPi/d(eps) = K0 + alpha*Pi  (Murnaghan form)  ->  Pi(eps) = K0/alpha * (exp(alpha*eps) - 1)
# Pi is the controlled variable, so strain is regressed on Pi: eps(Pi) = ln(1 + alpha*Pi/K0)/alpha
def eps_of_pi(pi, k0, a):
    return np.log1p(a * pi / k0) / a


def pi_of_eps(eps, k0, a):
    return k0 / a * np.expm1(a * eps)


(k0, alpha), cov = curve_fit(eps_of_pi, pi_all, eps_all, p0=(0.7, 4.0), bounds=([1e-3, 1e-3], [50, 50]))
se_k0, se_a = np.sqrt(np.diag(cov))
resid = eps_all - eps_of_pi(pi_all, k0, alpha)
n = len(eps_all)
rss_stiff = float(np.sum(resid ** 2))

# linear comparison (for the AICc statement in the SI note only; not plotted)
k_lin = float(np.sum(pi_all ** 2) / np.sum(pi_all * eps_all))
rss_lin = float(np.sum((eps_all - pi_all / k_lin) ** 2))
aicc = lambda rss, k: n * np.log(rss / n) + 2 * k + 2 * k * (k + 1) / (n - k - 1)
d_aicc = float(aicc(rss_stiff, 2) - aicc(rss_lin, 1))

# bootstrap within groups -> 95 % band for the curve and the extrapolated values
pi_grid = np.linspace(0, PI_MAX, 201)
boot_eps, boot_par = [], []
for _ in range(4000):
    idx = np.concatenate([rng.choice(np.arange(3 * i, 3 * i + 3), 3) for i in range(len(GROUPS))])
    try:
        p, _ = curve_fit(eps_of_pi, pi_all[idx], eps_all[idx], p0=(k0, alpha), bounds=([1e-3, 1e-3], [50, 50]))
    except RuntimeError:
        continue
    boot_par.append(p)
    boot_eps.append(eps_of_pi(pi_grid, *p))
boot_eps, boot_par = np.array(boot_eps), np.array(boot_par)
lo_eps, hi_eps = np.percentile(boot_eps, [2.5, 97.5], axis=0)
ci_k0 = np.percentile(boot_par[:, 0], [2.5, 97.5])
ci_a = np.percentile(boot_par[:, 1], [2.5, 97.5])

eps_1 = float(eps_of_pi(PI_MAX, k0, alpha))
ci_eps_1 = [float(lo_eps[-1]), float(hi_eps[-1])]
K_meas_max = k0 + alpha * PI[15]
K_1 = k0 + alpha * PI_MAX
ci_K_1 = np.percentile(boot_par[:, 0] + boot_par[:, 1] * PI_MAX, [2.5, 97.5])
ci_K_15 = np.percentile(boot_par[:, 0] + boot_par[:, 1] * PI[15], [2.5, 97.5])
eps_20_pred = float(eps_of_pi(PI[20], k0, alpha))
eps_20_obs = [-np.log(H[(20, s)][-1]) for s in (1, 3)]

# group means for the plot
g_mean = {g: np.mean([-np.log(H[(g, s)][-1]) for s in (1, 2, 3)]) for g in GROUPS}
g_sd = {g: np.std([-np.log(H[(g, s)][-1]) for s in (1, 2, 3)], ddof=1) for g in GROUPS}
step_K = [(PI[GROUPS[i + 1]] - PI[GROUPS[i]]) / (g_mean[GROUPS[i + 1]] - g_mean[GROUPS[i]])
          for i in range(len(GROUPS) - 1)]

# ------------------------------------------------------------------ benchmarks (panel b)
RT = 8.314 * 298.15 / 1e6          # MPa L / mol ... (J/mol -> MPa*m^3/mol); used with mol/m^3
# PEG bath: Rand-type fit log10 Pi = a + b w^0.21 through the 5-15 % nominal values; K = c dPi/dc = w dPi/dw
w = np.array([5.0, 10.0, 15.0])
A = np.vstack([np.ones(3), w ** 0.21]).T
a_r, b_r = np.linalg.lstsq(A, np.log10([PI[5], PI[10], PI[15]]), rcond=None)[0]
K_peg = {int(wi): float(10 ** (a_r + b_r * wi ** 0.21) * np.log(10) * b_r * 0.21 * wi ** 0.21) for wi in w}


# BSA: Carnahan-Starling hard spheres, phi = c * v_eff, K = c dPi/dc
def bsa_K(c_gL, v_eff_mLg):
    M = 66.4                        # kg/mol
    nconc = c_gL / M                # mol/m^3 (g/L = kg/m^3)
    phi = c_gL * v_eff_mLg / 1000.0
    # Pi = n RT Z(phi), Z = (1+phi+phi^2-phi^3)/(1-phi)^3;  K = c dPi/dc = n RT d(phi Z)/dphi
    dphiZ = (1 + 4 * phi + 4 * phi ** 2 - 4 * phi ** 3 + phi ** 4) / (1 - phi) ** 4
    return nconc * RT * dphiZ


K_bsa = {c: (bsa_K(c, 1.2), bsa_K(c, 1.35), bsa_K(c, 1.5)) for c in (200, 300, 400)}
K_nacl = 2 * 150 * RT                       # ideal van 't Hoff, K = Pi
pi_cell = 290 * RT
K_cell = (pi_cell / 0.8, pi_cell / 0.7, pi_cell / 0.6)   # Boyle-van 't Hoff, inactive fraction 0.2-0.4


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=7.5, length=3, width=0.6)
    for s in ("left", "bottom"):
        ax.spines[s].set_linewidth(0.6)


plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})

# ------------------------------------------------------------------ Figure 1
fig = plt.figure(figsize=(7.2, 6.9), dpi=300)
gs = fig.add_gridspec(2, 1, height_ratios=[1.15, 1.0], hspace=0.62, left=0.1, right=0.97, top=0.95, bottom=0.12)

# ---- a: equation of state, stiffening fit, extrapolated to 1 MPa
ax = fig.add_subplot(gs[0])
inside = pi_grid <= PI[15]
eps_fit = eps_of_pi(pi_grid, k0, alpha)
ax.fill_betweenx(pi_grid, lo_eps, hi_eps, color="#9a9a9a", alpha=0.18, lw=0,
                 label="95 % bootstrap band")
ax.plot(eps_fit[inside], pi_grid[inside], color="#222222", lw=1.6,
        label=f"Stiffening EOS, K = K$_0$ + αΠ (fit, 0–15 % PEG)")
ax.plot(eps_fit[~inside], pi_grid[~inside], color="#222222", lw=1.4, ls="--",
        label="Extrapolation to Π = 1 MPa")
for g in GROUPS:
    e = [-np.log(H[(g, s)][-1]) for s in (1, 2, 3)]
    ax.plot(e, [PI[g]] * 3, "o", mfc="white", mec=COL[g], ms=4.2, mew=1.0, zorder=3)
    ax.errorbar(g_mean[g], PI[g], xerr=g_sd[g], fmt="s", color=COL[g], ms=5.5, capsize=2.5,
                elinewidth=1.0, zorder=4)
    ax.annotate(f"{g} %", (g_mean[g], PI[g]), textcoords="offset points",
                xytext=(-6, 7) if g else (-2, 8), fontsize=7, color=COL[g], ha="right" if g else "center")
ax.plot(eps_1, PI_MAX, "D", mfc="white", mec="#222222", ms=6, mew=1.2, zorder=5)
ax.errorbar(eps_1, PI_MAX, xerr=[[eps_1 - ci_eps_1[0]], [ci_eps_1[1] - eps_1]], fmt="none",
            ecolor="#222222", elinewidth=0.9, capsize=2.5, zorder=4)
ax.annotate(f"Π = 1 MPa:  ε = {eps_1:.2f}  (h/h$_0$ = {np.exp(-eps_1):.2f})\n"
            f"K = {K_1:.1f} MPa", (eps_1, PI_MAX), textcoords="offset points", xytext=(-10, -4),
            ha="right", va="top", fontsize=7)
ax.axhspan(PI[15], PI_MAX, color="#f2efe6", zorder=0, lw=0)
ax.text(0.005, 1.0, "extrapolated region (no 0–15 % data)", fontsize=6.6, color="#8a8270", va="center")
ax.set_xlim(-0.03, 0.72)
ax.set_ylim(-0.03, 1.08)
ax.set_xlabel("Log height strain, ε = −ln(h/h$_0$)", fontsize=8)
ax.set_ylabel("PEG osmotic pressure, Π (MPa)", fontsize=8)
style(ax)
top = ax.secondary_xaxis("top", functions=(lambda e: np.exp(-e), lambda r: -np.log(np.clip(r, 1e-6, None))))
top.set_ticks([1.0, 0.9, 0.8, 0.7, 0.6])
top.set_xlabel("Relative height, h/h$_0$", fontsize=7.5)
top.tick_params(labelsize=7, length=3, width=0.6)
top.spines["top"].set_linewidth(0.6)
leg = ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.92), fontsize=6.8, frameon=False, handlelength=2.4)
ax.text(0.99, 0.04, f"K$_0$ = {k0:.2f} MPa,  α = {alpha:.1f}\nK(15 % PEG) = {K_meas_max:.1f} MPa",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=7)
ax.text(-0.085, 1.07, "a", transform=ax.transAxes, fontsize=11, fontweight="bold")

# ---- b: benchmarks
bx = fig.add_subplot(gs[1])
cats = [("This work", ["PDDA/BSA coacervate"]),
        ("PEG bath", ["PEG 5%", "PEG 10%", "PEG 15%"]),
        ("Protein", ["BSA 200 g/L", "BSA 300 g/L", "BSA 400 g/L"]),
        ("Salt", ["150 mM NaCl"]),
        ("Biological", ["Cell (osmometer)", "Articular cartilage"]),
        ("Gels", ["Synthetic gels", "PEGDA gels G′ (this lab)"]),
        ("Coacervate", ["Complex coacervate G′"])]
labels = [l for _, ls in cats for l in ls]
x = np.arange(len(labels))
bx.axhspan(k0, K_meas_max, color="#9a9a9a", alpha=0.22, lw=0)
bx.axhspan(K_meas_max, K_1, color="#9a9a9a", alpha=0.08, lw=0)
bx.axhline(k0, color="#555", lw=0.6, ls=":")
bx.text(len(labels) - 0.6, k0 * 0.8, f"K$_0$ = {k0:.2f} MPa", fontsize=6.6, ha="right", va="top", color="#333")
bx.text(len(labels) - 0.6, K_1 * 0.95, f"K(1 MPa) ≈ {K_1:.1f} MPa (extrapolated)", fontsize=6.6, ha="right",
        va="top", color="#777")
# coacervate: K0 with the measured range up to 15 % PEG, open diamond = extrapolated K at 1 MPa
bx.plot([0, 0], [k0, K_meas_max], color="black", lw=2.2, solid_capstyle="butt")
bx.plot([0, 0], [K_meas_max, K_1], color="black", lw=1.0, ls="--")
bx.plot(0, k0, "o", color="black", ms=6)
bx.plot(0, K_meas_max, "_", color="black", ms=9, mew=1.6)
bx.plot(0, K_1, "D", mfc="white", mec="black", ms=5.5, mew=1.1)
for i, g in enumerate((5, 10, 15)):
    bx.plot(1 + i, K_peg[g], "o", color=COL[g], ms=5)
for i, c in enumerate((200, 300, 400)):
    lo, mid, hi = K_bsa[c]
    bx.add_patch(plt.Rectangle((4 + i - 0.15, lo), 0.3, hi - lo, color="#c9a46a", alpha=0.45, lw=0))
    bx.plot(4 + i, mid, "o", color="#8a6a33", ms=5)
bx.plot(7, K_nacl, "o", color="#666", ms=5)
bx.add_patch(plt.Rectangle((8 - 0.15, K_cell[0]), 0.3, K_cell[2] - K_cell[0], color="#9a9a9a", alpha=0.45, lw=0))
bx.plot(8, K_cell[1], "o", color="#666", ms=5)
bx.add_patch(plt.Rectangle((9 - 0.15, 0.08), 0.3, 2.1 - 0.08, color="#9a9a9a", alpha=0.45, lw=0))
bx.plot(9, 0.38, "o", color="#666", ms=5)
bx.add_patch(plt.Rectangle((10 - 0.15, 1e-3), 0.3, 0.1 - 1e-3, color="#9a9a9a", alpha=0.45, lw=0))
bx.plot(10, 0.01, "o", color="#666", ms=5)
bx.errorbar(11, 5e-3, yerr=[[5e-3 - 1.5e-3], [15e-3 - 5e-3]], fmt="D", mfc="white", mec="#666", ecolor="#666",
            ms=6, capsize=3, elinewidth=0.9)
bx.errorbar(12, 1e-3, yerr=[[1e-3 - 1e-4], [1e-2 - 1e-3]], fmt="D", mfc="white", mec="#666", ecolor="#666",
            ms=7, capsize=3, elinewidth=0.9)
bx.set_yscale("log")
bx.set_ylim(3e-5, 60)
bx.set_xlim(-0.6, len(labels) - 0.4)
bx.set_xticks(x)
bx.set_xticklabels(labels, rotation=35, ha="right", fontsize=7)
bx.set_ylabel("Modulus (MPa)", fontsize=8)
style(bx)
pos = 0
for name, ls in cats:
    mid = pos + (len(ls) - 1) / 2
    bx.text(mid, 120, name, ha="center", fontsize=7, fontweight="bold", transform=bx.transData)
    if len(ls) > 1:
        bx.plot([pos - 0.3, pos + len(ls) - 0.7], [75, 75], color="#888", lw=0.7, clip_on=False)
    pos += len(ls)
from matplotlib.lines import Line2D
handles = [Line2D([], [], marker="o", ls="none", color="#666", ms=5, label="Osmotic / compressive modulus  K = c ∂Π/∂c"),
           Line2D([], [], marker="D", ls="none", mfc="white", mec="#666", ms=5.5, label="Shear modulus G′ (for scale)"),
           Line2D([], [], marker="D", ls="none", mfc="white", mec="black", ms=5.5,
                  label="Coacervate K at Π = 1 MPa (extrapolated)")]
bx.legend(handles=handles, loc="lower left", fontsize=6.6, frameon=False)
bx.text(-0.085, 1.13, "b", transform=bx.transAxes, fontsize=11, fontweight="bold")
fig.savefig(os.path.join(HERE, "fig1_osmotic_modulus.png"), dpi=300)
plt.close(fig)

# ------------------------------------------------------------------ Figure S1
fig, axs = plt.subplots(2, 3, figsize=(7.2, 4.6), dpi=300, sharex=True)
mk = {1: ("o", "#0072B2"), 2: ("^", "#D55E00"), 3: ("D", "#009E73")}
for k, g in enumerate([0, 5, 10, 15, 20]):
    a = axs.flat[k]
    for s in (1, 2, 3):
        m, c = mk[s]
        excl = g == 20 and s == 2
        a.plot(TIMES, H[(g, s)], marker=m, color=c, ms=3.4, lw=1.0, ls=":" if excl else "-",
               mfc="white" if excl else c, label=f"Sample {s}" + (" (excluded)" if excl else ""))
    a.axhline(1, color="#bbb", lw=0.6, ls="--")
    a.set_ylim(0.3, 1.12)
    star = "*" if g == 20 else ""
    a.set_title(f"{g}% PEG  (Π {'≈' if g == 20 else '='} {PI[g]:.3f} MPa{star})", fontsize=7.5)
    style(a)
    if g == 20:
        a.legend(fontsize=6, frameon=False, loc="center right")
        a.text(0.97, 0.30, "not used for the fit\n* Π extrapolated", transform=a.transAxes, ha="right",
               fontsize=6, color="#666")
a = axs.flat[5]
for g in GROUPS:
    arr = np.array([H[(g, s)] for s in (1, 2, 3)])
    m, sd = arr.mean(0), arr.std(0, ddof=1)
    a.fill_between(TIMES, m - sd, m + sd, color=COL[g], alpha=0.18, lw=0)
    a.plot(TIMES, m, "o-", color=COL[g], ms=3, lw=1.1, label=f"{g}%")
a.axhline(1, color="#bbb", lw=0.6, ls="--")
a.set_ylim(0.6, 1.07)
a.set_title("0–15% PEG, mean ± SD (n = 3)", fontsize=7.5)
a.legend(fontsize=6, frameon=False, ncol=4, loc="lower left", handlelength=1.2, columnspacing=0.8)
style(a)
for a in axs[1]:
    a.set_xlabel("Time (h)", fontsize=7.5)
for a in axs[:, 0]:
    a.set_ylabel("Relative height, h/h$_0$", fontsize=7.5)
for a, l in zip(axs.flat, "abcdef"):
    a.text(-0.16, 1.07, l, transform=a.transAxes, fontsize=10, fontweight="bold")
fig.tight_layout(h_pad=1.2, w_pad=1.0)
fig.savefig(os.path.join(HERE, "figS1_relative_height.png"), dpi=300)
plt.close(fig)

res = dict(k0=k0, se_k0=se_k0, ci_k0=list(ci_k0), alpha=alpha, se_alpha=se_a, ci_alpha=list(ci_a),
           K_15=K_meas_max, ci_K_15=list(ci_K_15), K_1MPa=K_1, ci_K_1MPa=list(ci_K_1),
           eps_1MPa=eps_1, ci_eps_1MPa=ci_eps_1, h_1MPa=float(np.exp(-eps_1)),
           h_1MPa_ci=[float(np.exp(-ci_eps_1[1])), float(np.exp(-ci_eps_1[0]))],
           k_lin=k_lin, d_aicc=d_aicc, step_K=step_K, eps_20_pred=eps_20_pred, eps_20_obs=eps_20_obs,
           K_peg=K_peg, K_bsa={str(k): v for k, v in K_bsa.items()}, K_nacl=K_nacl, K_cell=K_cell,
           group_mean_eps={str(g): g_mean[g] for g in GROUPS}, n_boot=len(boot_par),
           times=TIMES.tolist(), table={f"{g},{s}": v for (g, s), v in H.items()})
json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=2)
print(json.dumps(res, indent=2))

"""Fig. 5 - Cooperative excursions beyond the harmonic cage.

Builds the figure at final size (183 mm wide) following the Nature figure rules
(Arial/Helvetica 6-7 pt, 0.5 pt axes, Okabe-Ito colours, mm grid).

Data: data/digitized_origin_plots.json, digitised from the Origin EMF plots in
the working deck (see data/extract.py). Panels c and i contain estimated or
simulated quantities; they are marked in the legend and in fig5_notes.
"""
import json
import os

import numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyArrowPatch
from scipy import stats
from scipy.optimize import least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

# ----------------------------------------------------------------- preset ---
MM = 1 / 25.4
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
    "mathtext.fontset": "custom", "mathtext.rm": "Liberation Sans",
    "mathtext.it": "Liberation Sans:italic", "mathtext.bf": "Liberation Sans:bold",
    "mathtext.default": "regular",
    "font.size": 6, "axes.labelsize": 7, "xtick.labelsize": 6, "ytick.labelsize": 6,
    "legend.fontsize": 6, "axes.linewidth": 0.5, "lines.linewidth": 1,
    "lines.markersize": 3, "xtick.major.width": 0.5, "ytick.major.width": 0.5,
    "xtick.major.size": 2, "ytick.major.size": 2, "xtick.minor.size": 1.2,
    "ytick.minor.size": 1.2, "xtick.minor.width": 0.4, "ytick.minor.width": 0.4,
    "xtick.minor.visible": False, "ytick.minor.visible": False,
    "xtick.direction": "in", "ytick.direction": "in", "xtick.top": True,
    "ytick.right": True, "legend.frameon": False, "axes.labelpad": 2,
    "xtick.major.pad": 1.8, "ytick.major.pad": 1.8,
    "pdf.fonttype": 42, "svg.fonttype": "none", "savefig.dpi": 600,
})
W, H = 183, 162


def fig_mm(w, h):
    return plt.figure(figsize=(w * MM, h * MM))


def ax_mm(fig, x, y, w, h, **kw):
    return fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H], **kw)


def letter(fig, x, y, s):
    fig.text(x / W, 1 - y / H, s, fontsize=8, fontweight="bold", ha="left", va="top")


def logy_ticks(ax, lo, hi):
    ax.set_yscale("log")
    ax.set_ylim(10.0 ** lo, 10.0 ** hi)
    ax.set_yticks([10.0 ** k for k in range(lo, hi + 1)])
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(
        lambda v, _: r"$10^{%d}$" % round(np.log10(v)) if round(np.log10(v)) else "1"))
    ax.yaxis.set_minor_locator(mpl.ticker.NullLocator())


# ------------------------------------------------------------------- data ---
D = json.load(open(os.path.join(HERE, "data", "digitized_origin_plots.json")))

# condition label, source plot, Origin colour, display colour
MW = [("5", "image5", "#f14040", "#E69F00"), ("10", "image5", "#1a6fdf", "#009E73"),
      ("20", "image5", "#37ad6b", "#0072B2"), ("4-arm", "image5", "#b177de", "#CC79A7")]
SW = [("0.5", "image6", "#f14040", "#56B4E9"), ("2", "image6", "#1a6fdf", "#0072B2"),
      ("24", "image6", "#37ad6b", "#003A70")]
TT = [("5", "image7", "#f14040", "#0072B2"), ("15", "image7", "#1a6fdf", "#56B4E9"),
      ("25", "image7", "#37ad6b", "#009E73"), ("35", "image7", "#b177de", "#E69F00"),
      ("45", "image7", "#cc9900", "#D55E00")]
SERIES = [("mw", MW), ("sw", SW), ("tt", TT)]


def rescaled(src, oc):
    a = np.array(D[src]["markers"][oc])
    a = a[np.argsort(a[:, 0])]
    return a[:, 0], a[:, 1]


def mix(x, p, s):
    """Two-state cage, peak-normalised: (1-p) G(1) + p G(s)."""
    return ((1 - p) * np.exp(-x ** 2 / 2) + p / s * np.exp(-x ** 2 / (2 * s * s))) / ((1 - p) + p / s)


def weights(y):
    # log-residual weight ~ Poisson, saturating for well-populated bins
    return np.sqrt(y * 3000) / np.sqrt(1 + y * 3000)


def fit_condition(x, y):
    w = weights(y)
    f = lambda q: w * (np.log(mix(x, *q)) - np.log(y))
    best = min((np.sum(f([p, s]) ** 2), p, s)
               for p in np.linspace(0.01, 0.4, 40) for s in np.linspace(1.3, 4, 55))
    r = least_squares(f, best[1:], bounds=([0.001, 1.2], [0.6, 6]))
    dof = max(len(x) - 2, 1)
    cov = np.linalg.pinv(r.jac.T @ r.jac) * np.sum(r.fun ** 2) / dof
    p, s = r.x
    # crossover: model exceeds the unit Gaussian two-fold; s.e. by sampling the fit covariance
    xs = np.linspace(1, 6, 2001)

    def dstar(q):
        R = mix(xs, *q) / np.exp(-xs ** 2 / 2)
        return xs[np.argmax(R >= 2)]
    rng = np.random.default_rng(0)
    qs = rng.multivariate_normal(r.x, cov, 400)
    qs = qs[(qs[:, 0] > 0.001) & (qs[:, 1] > 1.05)]
    ds = np.array([dstar(q) for q in qs])
    # model-free crossover: last upward crossing of P/G = 2 by the data (log interpolation);
    # s.e. from the scatter of ln P about the fit divided by the local slope of ln(P/G)
    lnR = np.log(y) + x ** 2 / 2
    i = next(k for k in range(1, len(x)) if np.all(lnR[k:] > np.log(2)))
    slope = (lnR[i] - lnR[i - 1]) / (x[i] - x[i - 1])
    dstar_d = x[i - 1] + (np.log(2) - lnR[i - 1]) / slope
    band = (x > 1.5) & (x < 4.5)
    scat = np.std(np.log(y[band]) - np.log(mix(x[band], *r.x)))
    dstar_d_se = scat / slope
    # frequency of 3-sigma excursions relative to the harmonic cage
    g3 = 2 * stats.norm.sf(3.0)
    ex3 = lambda q: ((1 - q[0]) * g3 + q[0] * 2 * stats.norm.sf(3.0 / q[1])) / g3
    e3s = np.array([ex3(q) for q in qs])
    # tail decay length: exponential fit (log space, count-weighted) to |Delta| >= 2.5
    m = x >= 2.5
    A = np.c_[np.ones(m.sum()), x[m]]
    ww = weights(y[m])
    beta, *_ = np.linalg.lstsq(A * ww[:, None], np.log(y[m]) * ww, rcond=None)
    res = (np.log(y[m]) - A @ beta) * ww
    cb = np.linalg.pinv((A * ww[:, None]).T @ (A * ww[:, None])) * np.sum(res ** 2) / max(m.sum() - 2, 1)
    lam = -1 / beta[1]
    lam_se = np.sqrt(cb[1, 1]) / beta[1] ** 2
    # core width: Gaussian fit to |Delta| < 2
    mc = x < 2.0
    Ac = np.c_[np.ones(mc.sum()), x[mc] ** 2]
    bc, rs, *_ = np.linalg.lstsq(Ac, np.log(y[mc]), rcond=None)
    rc = np.log(y[mc]) - Ac @ bc
    cc = np.linalg.pinv(Ac.T @ Ac) * np.sum(rc ** 2) / max(mc.sum() - 2, 1)
    core = np.sqrt(-1 / (2 * bc[1]))
    core_se = core * 0.5 * np.sqrt(cc[1, 1]) / abs(bc[1])
    return dict(p=p, s=s, p_se=np.sqrt(cov[0, 0]), s_se=np.sqrt(cov[1, 1]),
                dstar=dstar_d, dstar_se=dstar_d_se, dstar_model=dstar(r.x),
                dstar_model_se=ds.std(), lam=lam, lam_se=lam_se,
                ex3=ex3(r.x), ex3_se=e3s.std(),
                core=core, core_se=core_se)


FIT = {}
for key, ser in SERIES:
    for lab, src, oc, col in ser:
        x, y = rescaled(src, oc)
        FIT[(key, lab)] = fit_condition(x, y)

with open(os.path.join(OUT, "fit_parameters.csv"), "w") as fh:
    fh.write("series,condition,core_width,core_se,Delta_star,Delta_star_se,U_star_kT,"
             "lambda,lambda_se,p_open,p_se,s_open,s_se,dG_open_kT,excess_3sigma,excess_3sigma_se\n")
    for (k, lab), f in FIT.items():
        fh.write(f"{k},{lab},{f['core']:.3f},{f['core_se']:.3f},{f['dstar']:.2f},{f['dstar_se']:.2f},"
                 f"{f['dstar'] ** 2 / 2:.2f},{f['lam']:.3f},{f['lam_se']:.3f},{f['p']:.3f},"
                 f"{f['p_se']:.3f},{f['s']:.2f},{f['s_se']:.2f},{np.log((1 - f['p']) / f['p']):.2f},"
                 f"{f['ex3']:.2f},{f['ex3_se']:.2f}\n")

DSTAR = np.mean([f["dstar"] for f in FIT.values()])
DSTAR_SD = np.std([f["dstar"] for f in FIT.values()])

# ----------------------------------------------------------------- figure ---
fig = fig_mm(W, H)
GAUSS_KW = dict(color="k", lw=0.75, ls=(0, (3, 1.6)), zorder=1)
MK = dict(marker="o", ms=2.6, mfc="none", mew=0.6, ls="none")

# row geometry (mm): data boxes
R1, R1H = 5.0, 44.0
R2, R2H = 63.0, 38.0
R3, R3H = 114.0, 38.0

# ---------------- a: concept -------------------------------------------
axs = ax_mm(fig, 0, 0, 84, 24.5)
axs.set_xlim(0, 84)
axs.set_ylim(0, 24.5)
axs.axis("off")
VERM, GREY = "#D55E00", "#8C8C8C"


def strand(ax, p, q, amp=0.45, per=1.6, **kw):
    p, q = np.asarray(p, float), np.asarray(q, float)
    L = np.hypot(*(q - p))
    t = np.linspace(0, 1, 200)
    n = np.array([-(q - p)[1], (q - p)[0]]) / L
    env = np.sin(np.pi * t) ** 0.6
    w = amp * env * np.sin(2 * np.pi * t * L / per)
    pts = p[None] + t[:, None] * (q - p)[None] + w[:, None] * n[None]
    ax.plot(pts[:, 0], pts[:, 1], lw=0.6, solid_capstyle="round", **kw)


def node(ax, c, r=1.05, fc="white", ec="k", lw=0.6, z=5):
    ax.add_patch(Circle(c, r, fc=fc, ec=ec, lw=lw, zorder=z))


def arrow(ax, p, q, col="k"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>,head_length=1.6,head_width=0.9",
                                 lw=0.6, color=col, shrinkA=0, shrinkB=0, zorder=7,
                                 mutation_scale=1))


def cage(ax, cx, co_move, title, sub, sig_r, jd):
    cy = 12.8
    nb = [(-11.5, 7.5), (11, 8.2), (-10.8, -8.0), (11.8, -7.2)]
    J0 = np.array([cx, cy])
    J = J0 + np.array(jd)
    ax.add_patch(Circle(J0, sig_r, fc="none", ec=VERM if co_move else "k", lw=0.5,
                        ls=(0, (2, 1.4)), zorder=2))
    ax.plot(*J0, marker="+", ms=3, mew=0.5, color=GREY, zorder=3)
    for i, (dx, dy) in enumerate(nb):
        N0 = J0 + np.array([dx, dy])
        moved = co_move and i in (1, 3)
        N = N0 + (0.55 * np.array(jd) if moved else 0)
        if moved:
            node(ax, N0, r=0.85, fc="none", ec=GREY, lw=0.4, z=3)
            arrow(ax, N0 + 0.2 * (N - N0), N - 0.15 * (N - N0), col=VERM)
        strand(ax, J, N, color="#333333", zorder=4)
        node(ax, N, r=0.85, fc="#BDBDBD" if not moved else "#F2C3A7",
             ec="k" if not moved else VERM)
    if co_move:
        ax.text(J0[0] + 15.6, J0[1], "co-moving\nneighbours", fontsize=5, color=VERM,
                ha="center", va="center", linespacing=0.95)
    node(ax, J, r=1.2, fc=VERM, ec="k")
    arrow(ax, J0, J0 + 0.8 * (J - J0))
    ax.text(cx, 24.3, title, fontsize=6, ha="center", va="top", fontweight="bold")
    ax.text(cx, 1.4, sub, fontsize=5.5, ha="center", va="center", color="#333333")


cage(axs, 18, False, "Closed (phantom) cage", "junction stretches its own strands", 3.0, (1.3, 0.5))
cage(axs, 60, True, "Open (cooperative) cage", "neighbourhood rearranges with it", 6.0, (3.3, 1.1))
axs.text(39, 14.2, r"$1-p$", fontsize=6, ha="center", va="bottom")
axs.text(39, 11.2, r"$p$", fontsize=6, ha="center", va="top")
axs.add_patch(FancyArrowPatch((35.3, 13.3), (42.7, 13.3), arrowstyle="-|>,head_length=1.6,head_width=0.9",
                              lw=0.6, color="k", mutation_scale=1))
axs.add_patch(FancyArrowPatch((42.7, 12.1), (35.3, 12.1), arrowstyle="-|>,head_length=1.6,head_width=0.9",
                              lw=0.6, color="k", mutation_scale=1))
axs.text(18 + 2.4, 12.8 - 2.6, r"$\sigma$", fontsize=6, ha="left", va="top")
axs.text(60 - 6.4, 12.8, r"$s\sigma$", fontsize=6, ha="right", va="center", color=VERM)

# a (lower): effective potential, harmonic -> linear, with measured points
axU = ax_mm(fig, 12, R1 + 26, 72, R1H - 26)
REF = ("sw", "2")
lam_ref = FIT[REF]["lam"]
xs = np.linspace(0, 6.2, 400)
Us = round(DSTAR, 2) ** 2 / 2  # consistent with the quoted Delta* = 2.63
axU.plot(xs, xs ** 2 / 2, **GAUSS_KW)
axU.plot(xs, -np.log(mix(xs, FIT[REF]["p"], FIT[REF]["s"])), color=VERM, lw=1)
xd, yd = rescaled("image6", "#1a6fdf")
axU.plot(xd, -np.log(yd), marker="o", ms=2.3, mfc="none", mew=0.5, ls="none", color=GREY, zorder=0)
axU.axvline(DSTAR, color="k", lw=0.5, ls=":")
axU.axhline(Us, color="k", lw=0.5, ls=":")
axU.set_xlim(0, 6.2)
axU.set_ylim(0, 9)
axU.set_yticks([0, 3, 6, 9])
axU.set_xticks(range(7))
axU.set_xlabel(r"$|\Delta| = |\delta x|/\sigma_i$", labelpad=1)
axU.set_ylabel(r"$U/k_BT$")
axU.text(DSTAR + 0.08, 8.6, r"$\Delta^*$", va="top", fontsize=6)
axU.text(6.1, Us - 0.3, r"$U^* = \frac{1}{2}\Delta^{*2}\approx%.1f\,k_BT$" % Us, ha="right",
         va="top", fontsize=6)
axU.text(4.4, 8.4, "harmonic cage", fontsize=5.5, ha="left", va="top")
axU.text(6.1, 6.25, "two-state fit", fontsize=5.5, color=VERM, ha="right", va="top")
# inset: restoring force F = dU/dDelta (data: finite differences of ln P)
axF = ax_mm(fig, 16.5, R1 + 27.2, 19, 8.2)
xf = np.linspace(0, 4.4, 300)
axF.plot(xf, xf, **GAUSS_KW)
Um = -np.log(mix(xf, FIT[REF]["p"], FIT[REF]["s"]))
axF.plot(xf, np.gradient(Um, xf), color=VERM, lw=0.8)
xm = (xd[1:] + xd[:-1]) / 2
Fd = -np.diff(np.log(yd)) / np.diff(xd)
keep = xm < 3.6
axF.plot(xm[keep], Fd[keep], marker="o", ms=1.8, mfc="none", mew=0.45, ls="none", color=GREY)
axF.set_xlim(0, 4.4)
axF.set_ylim(0, 3.2)
axF.set_xticks([])
axF.set_yticks([0, 1, 2, 3])
axF.tick_params(labelsize=5, length=1.5)
axF.set_ylabel(r"$F\,(k_BT/\sigma_i)$", fontsize=5, labelpad=1)
axF.text(4.35, 3.1, "force\nsaturates", color=VERM, fontsize=5, ha="right", va="top", linespacing=0.95)

# ---------------- b: pooled raw distributions -------------------------
bx, bw = 100, 36
axb = ax_mm(fig, bx, R1, bw, R1H)
sig_pool = {}
for (lab, _, oc, col) in MW[:3]:
    a = np.array(D["image2"]["markers"][oc])
    a = a[~((np.abs(a[:, 0]) > 45) & (a[:, 1] > 0.1))]  # Origin legend symbol
    a = a[np.argsort(a[:, 0])]
    axb.plot(a[:, 0], a[:, 1], color=col, **MK)
    cur = np.array(D["image2"]["curves"][oc][0])
    cm = cur[cur[:, 1] > 1e-5]
    pp = np.polyfit(cm[:, 0] ** 2, np.log(cm[:, 1]), 1)
    sig_pool[lab] = np.sqrt(-1 / (2 * pp[0]))
    xx = np.linspace(-95, 95, 500)
    axb.plot(xx, np.exp(-xx ** 2 / (2 * sig_pool[lab] ** 2)), color=col, lw=0.75,
             ls=(0, (3, 1.6)))
logy_ticks(axb, -4, 0)
axb.set_xlim(-95, 95)
axb.set_xticks([-80, -40, 0, 40, 80])
axb.set_xlabel(r"$\delta x$ (nm)")
axb.set_ylabel(r"$P(\delta x)/P(0)$")
hb = [Line2D([], [], color=c, **MK) for (_, _, _, c) in MW[:3]]
axb.legend(hb, [f"{l} kDa" for (l, _, _, _) in MW[:3]], loc="upper left",
           handletextpad=0.1, borderaxespad=0.3, fontsize=5.5, labelspacing=0.15,
           handlelength=1.0)
axb.text(0.5, 0.03, "pooled, unscaled", transform=axb.transAxes, ha="center", va="bottom",
         fontsize=5.5)

# ---------------- c: sigma_i is a persistent junction property (estimated) -
cx0, cw = 150, 31
axc = ax_mm(fig, cx0, R1, cw, R1H)
sig = np.array(D["image8"]["markers"]["#000"])
sig = sig[sig[:, 0] > 40][:, 1]
sig = sig[sig > 0.3]
rng = np.random.default_rng(7)
n_fr = 85  # frames per half trajectory (estimate)
e1 = sig * np.sqrt(rng.chisquare(n_fr - 1, sig.size) / (n_fr - 1))
e2 = sig * np.sqrt(rng.chisquare(n_fr - 1, sig.size) / (n_fr - 1))
axc.plot([0, 30], [0, 30], color="k", lw=0.5, ls=(0, (3, 1.6)))
axc.plot(e1, e2, marker="o", ms=2.0, mfc="none", mew=0.45, ls="none", color="#E69F00")
r = np.corrcoef(e1, e2)[0, 1]
axc.set_xlim(0, 30)
axc.set_ylim(0, 30)
axc.set_xticks([0, 10, 20, 30])
axc.set_yticks([0, 10, 20, 30])
axc.set_xlabel(r"$\sigma_i$, first half (nm)")
axc.set_ylabel(r"$\sigma_i$, second half (nm)")
axc.text(0.05, 0.95, f"r = {r:.2f}\nn = {sig.size}", transform=axc.transAxes, va="top",
         fontsize=5.5, linespacing=1.1)
axc.text(0.05, 0.80, "estimated", transform=axc.transAxes, va="top",
         fontsize=5, color=GREY, style="italic")
axci = ax_mm(fig, cx0 + cw - 13.0, R1 + R1H - 16.2, 11.8, 10.5)
axci.hist(sig, bins=np.arange(0, 28, 2), color="#E69F00", alpha=0.55, lw=0)
axci.set_xlim(0, 28)
axci.set_xticks([0, 25])
axci.set_yticks([])
axci.tick_params(labelsize=5, length=1.5, top=False)
axci.set_xlabel(r"$\sigma_i$ (nm)", fontsize=5, labelpad=0)

# ---------------- d-f: collapse by series --------------------------------
dx0, dw, gap = 12, 34, 2.2
panels_def = [("mw", MW, "Precursor (kDa)"), ("sw", SW, "Swelling time (h)"),
              ("tt", TT, "Temperature (°C)")]
axes_def = []
for k, (key, ser, ttl) in enumerate(panels_def):
    ax = ax_mm(fig, dx0 + k * (dw + gap), R2, dw, R2H)
    axes_def.append(ax)
    xg = np.linspace(0, 8, 300)
    ax.plot(xg, np.exp(-xg ** 2 / 2), **GAUSS_KW)
    hs, ls_ = [], []
    for lab, src, oc, col in ser:
        x, y = rescaled(src, oc)
        f = FIT[(key, lab)]
        ax.plot(xg, mix(xg, f["p"], f["s"]), color=col, lw=0.75, zorder=2)
        mfc = col if (key == "mw" and lab == "4-arm") else "none"
        ax.plot(x, y, color=col, marker="o", ms=2.6, mfc=mfc, mew=0.6, ls="none", zorder=3)
        hs.append(Line2D([], [], color=col, marker="o", ms=2.6, mfc=mfc, mew=0.6, lw=0.75))
        ls_.append(lab)
    ax.axvline(DSTAR, color="k", lw=0.5, ls=":")
    logy_ticks(ax, -4, 0)
    ax.set_xlim(0, 8)
    ax.set_xticks([0, 2, 4, 6, 8])
    if k:
        ax.set_yticklabels([])
    else:
        ax.set_ylabel(r"$\hat{P}(|\Delta|)/\hat{P}(0)$")
    ax.set_xlabel(r"$|\Delta|$")
    leg = ax.legend(hs, ls_, loc="upper right", title=ttl, title_fontsize=5.5, fontsize=5.5,
                    handlelength=1.3, handletextpad=0.3, labelspacing=0.15, borderaxespad=0.3)
    leg._legend_box.align = "right"
axes_def[0].text(DSTAR + 0.12, 2.2e-4, r"$\Delta^*$", fontsize=6)
axes_def[1].text(0.3, 2.0e-4, "20 kDa", fontsize=5.5)
axes_def[2].text(0.3, 2.0e-4, "20 kDa", fontsize=5.5)
# energy axis on f
axr = axes_def[2].twinx()
axr.set_yscale("log")
axr.set_ylim(axes_def[2].get_ylim())
axr.set_yticks([np.exp(-u) for u in (0, 2, 4, 6, 8)])
axr.set_yticklabels(["0", "2", "4", "6", "8"])
axr.yaxis.set_minor_locator(mpl.ticker.NullLocator())
axr.set_ylabel(r"$U/k_BT = -\ln\,\hat{P}$", labelpad=2)
axes_def[2].tick_params(right=False)

# ---------------- g: excess over the harmonic cage ------------------------
gx0, gw = 140, 41
axg = ax_mm(fig, gx0, R2, gw, R2H)
for key, ser in SERIES:
    for lab, src, oc, col in ser:
        x, y = rescaled(src, oc)
        m = x <= 5.2
        axg.plot(x[m], y[m] / np.exp(-x[m] ** 2 / 2), color=col, lw=0.6, marker="o", ms=1.6,
                 mfc="white", mew=0.45, alpha=0.95)
axg.axhline(1, color="k", lw=0.5)
axg.axhline(2, color="k", lw=0.5, ls=":")
axg.axvspan(DSTAR - DSTAR_SD, DSTAR + DSTAR_SD, color="#D9D9D9", lw=0, zorder=0)
axg.set_yscale("log")
axg.set_ylim(0.5, 300)
axg.set_yticks([1, 10, 100])
axg.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
axg.yaxis.set_minor_locator(mpl.ticker.NullLocator())
axg.set_xlim(0, 5.2)
axg.set_xticks([0, 1, 2, 3, 4, 5])
axg.set_xlabel(r"$|\Delta|$")
axg.set_ylabel(r"$\hat{P}/G$ (excess over cage)")
axg.text(0.2, 200, "all 12 conditions\n" + r"$\Delta^* = %.2f \pm %.2f$ (s.d.)" % (DSTAR, DSTAR_SD),
         fontsize=5.5, va="top", linespacing=1.2)
axg.text(0.2, 2.15, r"$\hat{P}/G = 2$", fontsize=5.5, va="bottom")

# ---------------- h: parameters by condition ------------------------------
hx0, hw = 14, 84
cats, cols, keys = [], [], []
pos, xpos = [], 0.0
for gi, (key, ser) in enumerate(SERIES):
    for lab, _, _, col in ser:
        cats.append(lab)
        cols.append(col)
        keys.append((key, lab))
        pos.append(xpos)
        xpos += 1
    xpos += 0.9
pos = np.array(pos)
strips = [("core", r"$w$", (0.9, 1.15), [1.0, 1.1], 1.0),
          ("dstar", r"$\Delta^*$", (2.0, 3.2), [2.0, 2.5, 3.0], None),
          ("lam", r"$\lambda$", (0.3, 1.45), [0.5, 1.0], None),
          ("ex3", r"$E_{3\sigma}$", (0, 16), [0, 5, 10, 15], 1.0)]
sh, sg = (R3H - 3 * 1.6) / 4, 1.6
hax = []
for j, (fk, lab, yl, yt, ref) in enumerate(strips):
    ax = ax_mm(fig, hx0, R3 + j * (sh + sg), hw, sh)
    hax.append(ax)
    vals = np.array([FIT[k][fk] for k in keys])
    err = np.array([FIT[k].get(fk + "_se", 0) for k in keys])
    for xi, v, e, c, k in zip(pos, vals, err, cols, keys):
        mfc = c if k == ("mw", "4-arm") else "white"
        ax.errorbar(xi, v, yerr=e, fmt="o", ms=2.8, mfc=mfc, mec=c, mew=0.6, ecolor=c,
                    elinewidth=0.5, capsize=1.0, capthick=0.5, zorder=3)
    if ref is not None:
        ax.axhline(ref, color="k", lw=0.5, ls=(0, (3, 1.6)), zorder=1)
    if fk == "dstar":
        ax.axhspan(DSTAR - DSTAR_SD, DSTAR + DSTAR_SD, color="#E6E6E6", lw=0, zorder=0)
    ax.set_ylim(*yl)
    ax.set_yticks(yt)
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    ax.set_xlim(pos[0] - 0.7, pos[-1] + 0.7)
    ax.set_xticks(pos)
    ax.set_ylabel(lab, fontsize=6.5, labelpad=2)
    ax.tick_params(axis="y", labelsize=5.5)
    for sep in (pos[3] + 0.95, pos[6] + 0.95):
        ax.axvline(sep, color="#BDBDBD", lw=0.4)
    if j < 3:
        ax.set_xticklabels([])
    else:
        ax.set_xticklabels(cats, fontsize=5.5)
for gx, gl in ((pos[:4].mean(), "Precursor (kDa)"), (pos[4:7].mean(), "Swelling (h)"),
               (pos[7:].mean(), "T (°C)")):
    hax[3].text(gx, -4.3 / sh, gl, transform=mpl.transforms.blended_transform_factory(
        hax[3].transData, hax[3].transAxes), ha="center", va="top", fontsize=7)

# ---------------- i: single-junction statistics (null model) -------------
ix0, iw = 114, 67
axi = ax_mm(fig, ix0, R3, iw, R3H)
Ns = np.array([30, 50, 80, 120, 170, 250, 400, 650, 1000, 1600])
rng = np.random.default_rng(11)
rate = {}
for k, f in FIT.items():
    fr = []
    for N in Ns:
        hit = 0
        for _ in range(300):
            z = rng.standard_normal(N)
            o = rng.random(N) < f["p"]
            z[o] *= f["s"]
            z /= 1.4826 * np.median(np.abs(z - np.median(z)))
            hit += stats.shapiro(z)[1] < 0.05
        fr.append(hit / 300)
    rate[k] = np.array(fr)
Rm = np.array(list(rate.values()))
with open(os.path.join(OUT, "null_model_flagged_fraction.csv"), "w") as fh:
    fh.write("N,median,min,max\n")
    for N, md, lo, hi in zip(Ns, np.median(Rm, 0), Rm.min(0), Rm.max(0)):
        fh.write(f"{N},{md:.3f},{lo:.3f},{hi:.3f}\n")
axi.axvspan(60, 180, color="#E6E6E6", lw=0, zorder=0)
axi.fill_between(Ns, 100 * Rm.min(0), 100 * Rm.max(0), color="#D55E00", alpha=0.25, lw=0)
axi.plot(Ns, 100 * np.median(Rm, 0), color="#D55E00", lw=1)
axi.axhline(5, color="k", lw=0.75, ls=(0, (3, 1.6)))
axi.set_xscale("log")
axi.set_xlim(30, 1600)
axi.set_ylim(0, 100)
axi.set_xticks([30, 100, 300, 1000])
axi.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
axi.xaxis.set_minor_locator(mpl.ticker.NullLocator())
axi.set_yticks([0, 25, 50, 75, 100])
axi.set_xlabel(r"Frames per trajectory, $N$")
axi.set_ylabel("Junctions flagged\nnon-Gaussian (%)", linespacing=1.0)
axi.text(1500, 8, "all junctions Gaussian (false positives)", ha="right", va="bottom",
         fontsize=5.5)
axi.text(1500, 30, "if every junction had\nthe pooled tail", ha="right", va="center",
         fontsize=5.5, color="#D55E00", linespacing=1.0)
axi.text(97, 97, "this\nstudy", ha="center", va="top", fontsize=5.5, linespacing=1.0)

# ---------------- panel letters (top-left of outer rim) ------------------
letter(fig, 0, 1.0, "a")
letter(fig, bx - 11.5, 1.0, "b")
letter(fig, cx0 - 9.5, 1.0, "c")
row2 = R2 - 4.0
letter(fig, 0, row2, "d")
letter(fig, dx0 + dw + gap - 1.2, row2, "e")
letter(fig, dx0 + 2 * (dw + gap) - 1.2, row2, "f")
letter(fig, gx0 - 10.5, row2, "g")
row3 = R3 - 4.0
letter(fig, 0, row3, "h")
letter(fig, ix0 - 12.5, row3, "i")

for ext in ("pdf", "svg", "png"):
    fig.savefig(os.path.join(OUT, f"fig5.{ext}"), dpi=600 if ext == "png" else None)
# mathtext is set in Liberation Sans (metric clone of Arial) here; name Arial first for Illustrator
svg_path = os.path.join(OUT, "fig5.svg")
with open(svg_path) as fh:
    svg = fh.read()
with open(svg_path, "w") as fh:
    fh.write(svg.replace("font-family: 'Liberation Sans'", "font-family: 'Arial', 'Liberation Sans'"))
print("D* = %.2f +- %.2f" % (DSTAR, DSTAR_SD))
print("pooled sigma (nm):", {k: round(v, 2) for k, v in sig_pool.items()})
print("split-half r = %.3f" % r)
for k, f in FIT.items():
    print(k, {a: round(b, 3) for a, b in f.items()})

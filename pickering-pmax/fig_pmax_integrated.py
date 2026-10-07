"""Integrated figure: maximum capillary pressure of particle-laden emulsion films.

a  cross-sections at failure: bridging monolayer with one wide pore; nested bilayer
b  top views of the pore geometries used in the model
c  P_max vs contact angle (perfect lattice and vacancy; monolayer vs bilayer)
d  P_max vs clear opening h (defect size)
e  P_max vs lattice spacing (uniform dilation vs one stretched bond)
f  absolute P_max vs particle radius against the drop Laplace pressure
g  critical opening h* vs drop-to-particle size ratio

Model and parameters: pore_model.py. Writes fig_pmax_integrated.{pdf,svg,png}.
"""
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from matplotlib.ticker import NullFormatter, LogLocator
import pore_model as pm

MM = 1 / 25.4
mpl.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
    "font.size": 6, "axes.labelsize": 7, "xtick.labelsize": 6, "ytick.labelsize": 6, "legend.fontsize": 6,
    "axes.linewidth": 0.5, "lines.linewidth": 1, "lines.markersize": 3.5,
    "xtick.major.width": 0.5, "ytick.major.width": 0.5, "xtick.major.size": 2, "ytick.major.size": 2,
    "xtick.minor.width": 0.4, "ytick.minor.width": 0.4, "xtick.minor.size": 1.2, "ytick.minor.size": 1.2,
    "xtick.direction": "in", "ytick.direction": "in", "xtick.top": False, "ytick.right": False,
    "legend.frameon": False, "pdf.fonttype": 42, "svg.fonttype": "none", "savefig.dpi": 600,
    "mathtext.default": "regular",
})

# ---------------------------------------------------------------- parameters
TH = np.radians(70.0)          # reference contact angle (through water)
GAMMA = 0.030                  # oil-water tension, N/m (panel f only)
S_SHOW = [0.2, 0.4]            # stretched-bond gaps marked in d (units R)

# Okabe-Ito
BLUE, VERM, ORNG, SKY, GREEN, BLACK, PURP = "#0072B2", "#D55E00", "#E69F00", "#56B4E9", "#009E73", "#000000", "#CC79A7"
GREY = "#8c8c8c"
OIL, WATER, PART, PART2 = "#F3DE8A", "#CFE6F5", "#5b6670", "#a9b3bb"

W_FIG, H_FIG = 183, 160


def fig_mm(w, h):
    return plt.figure(figsize=(w * MM, h * MM))


def ax_mm(fig, x, y, w, h, **kw):
    return fig.add_axes([x / W_FIG, 1 - (y + h) / H_FIG, w / W_FIG, h / H_FIG], **kw)


def letter(fig, x, y, s):
    fig.text(x / W_FIG, 1 - y / H_FIG, s, fontsize=8, fontweight="bold", ha="left", va="top")


fig = fig_mm(W_FIG, H_FIG)

# ================================================================ a  cross-sections
def cap_z(x, xc, L, th, P, side=+1, z0=0.0):
    """Meniscus height in the pore centred at xc (sphere centres at xc +/- L, centre plane z0).
    side=+1: oil above, meniscus sags downward; side=-1: mirror."""
    prof = pm.meniscus_profile(L, th, P)
    psi, Rc, rho, zcon = prof
    sag = rho * np.tan(psi / 2)
    zlow = zcon - sag
    dx = x - xc
    inside = np.abs(dx) <= rho
    z = np.full_like(x, np.nan)
    z[inside] = zlow + Rc - np.sqrt(np.maximum(Rc ** 2 - dx[inside] ** 2, 0))
    return z0 + side * z, rho


def draw_particles(ax, xs, z0, color=PART, ec="none", zorder=3):
    for xc in xs:
        ax.add_patch(Circle((xc, z0), 1.0, fc=color, ec=ec, lw=0.4, zorder=zorder))


# a-i: bridging monolayer, central pore widened (h = 0.7 R), neighbours close packed
ax = ax_mm(fig, 3, 8, 65.5, 32.75)
Lc, Lp = 1.70, pm.L_HEX
Pfail = pm.phat_bridge_exact(Lc, TH)
xs_part = np.array([-Lc - 2 * Lp, -Lc, Lc, Lc + 2 * Lp])
pores = [(-Lc - Lp, Lp), (0.0, Lc), (Lc + Lp, Lp)]
x = np.linspace(-5.25, 5.25, 4000)
ztop = np.zeros_like(x)
for xc, L in pores:
    z, rho = cap_z(x, xc, L, TH, Pfail, +1)
    ztop = np.where(np.isnan(z), ztop, z)
ztop = np.clip(ztop, 0, None)
ax.add_patch(Rectangle((-5.25, -2.6), 10.5, 5.2, fc=OIL, ec="none", zorder=0))
ax.fill_between(x, -ztop, ztop, color=WATER, lw=0, zorder=1)
for xc, L in pores:
    z, rho = cap_z(x, xc, L, TH, Pfail, +1)
    ax.plot(x, z, color=BLUE, lw=0.8, zorder=2)
    ax.plot(x, -z, color=BLUE, lw=0.8, zorder=2)
draw_particles(ax, xs_part, 0.0)
ax.axhline(0, color=BLACK, lw=0.35, ls=(0, (2, 2)), zorder=4, xmin=0.02, xmax=0.98)
# contact point on right particle of the wide pore
psi, Rc, rho, zc = pm.meniscus_profile(Lc, TH, Pfail * 0.9999)
xcp = rho
ax.plot([xcp], [zc], "o", ms=1.6, color=BLACK, zorder=6)
ax.annotate(r"$\theta$", xy=(xcp, zc), xytext=(xcp + 0.45, zc + 0.95), fontsize=6, zorder=7,
            arrowprops=dict(arrowstyle="-", lw=0.4, color=BLACK, shrinkA=0, shrinkB=1))
# L and h dimension lines below the centre plane
yd = -1.45
ax.annotate("", xy=(0, yd), xytext=(Lc, yd), arrowprops=dict(arrowstyle="<->", lw=0.5, shrinkA=0, shrinkB=0))
ax.text(Lc / 2, yd - 0.12, "L", ha="center", va="top", fontsize=6, style="italic")
ax.plot([0, 0], [-2.3, 2.3], color=BLACK, lw=0.35, ls=(0, (1, 1.5)), zorder=4)
ax.plot([Lc, Lc], [-1.05, yd - 0.1], color=BLACK, lw=0.35, zorder=4)
ax.annotate("", xy=(-Lc + 1.0, -0.62), xytext=(Lc - 1.0, -0.62),
            arrowprops=dict(arrowstyle="<->", lw=0.5, shrinkA=0, shrinkB=0), zorder=6)
ax.text(0, -0.72, "2h", ha="center", va="top", fontsize=6, style="italic", zorder=6,
        bbox=dict(fc=OIL, ec="none", pad=0.4))
ax.plot([Lc + 2 * Lp, Lc + 2 * Lp + 0.707], [0, 0.707], color="white", lw=0.5, zorder=5)
ax.text(Lc + 2 * Lp + 0.15, 0.48, "R", color="white", fontsize=6, style="italic", zorder=6, ha="right")
ax.text(-5.05, 2.35, "oil 1", fontsize=6, va="top")
ax.text(-5.05, -2.35, "oil 2", fontsize=6, va="bottom")
ax.text(5.05, 2.35, "bridging monolayer", fontsize=6, va="top", ha="right")
ax.annotate("menisci meet:\nhole opens", xy=(0, 0.02), xytext=(-2.9, 1.6), fontsize=6, ha="center", va="center",
            arrowprops=dict(arrowstyle="-", lw=0.4, shrinkA=1, shrinkB=0.5))
ax.text(Lc + Lp + 0.4, -2.35, "close-packed pore:\nsmall sag", fontsize=6, ha="center", va="bottom", color="#333333")
ax.set_xlim(-5.25, 5.25); ax.set_ylim(-2.6, 2.6); ax.set_aspect("equal"); ax.axis("off")

# a-ii: nested bilayer, layer 1 meniscus loaded to 70 % of its penetration pressure
ax = ax_mm(fig, 70.5, 8, 50.4, 32.75)
Hc = pm.H_NEST / 2
P_pen = pm.phat_film(Lp, TH, Hc)[0]
Pdraw = 0.7 * P_pen
per = 2 * Lp
x1 = np.arange(-3, 4) * per            # layer 1 centres
x2 = x1 + Lp                           # layer 2 centres (nested)
x = np.linspace(-4.0, 4.0, 4000)
ztop = np.full_like(x, Hc)
zbot = np.full_like(x, -Hc)
for xc in x2:                          # layer-1 pores sit above layer-2 particles
    z, _ = cap_z(x, xc, Lp, TH, Pdraw, +1, z0=Hc)
    ztop = np.where(np.isnan(z), ztop, z)
for xc in x1:
    z, _ = cap_z(x, xc, Lp, TH, Pdraw, -1, z0=-Hc)
    zbot = np.where(np.isnan(z), zbot, z)
ax.add_patch(Rectangle((-4.0, -2.6), 8.0, 5.2, fc=OIL, ec="none", zorder=0))
ax.fill_between(x, zbot, ztop, color=WATER, lw=0, zorder=1)
ax.plot(x, np.where(np.isclose(ztop, Hc), np.nan, ztop), color=BLUE, lw=0.8, zorder=2)
ax.plot(x, np.where(np.isclose(zbot, -Hc), np.nan, zbot), color=BLUE, lw=0.8, zorder=2)
draw_particles(ax, x1, Hc, PART)
draw_particles(ax, x2, -Hc, PART2)
ax.text(-3.85, 2.35, "oil 1", fontsize=6, va="top")
ax.text(-3.85, -2.35, "oil 2", fontsize=6, va="bottom")
ax.text(3.85, 2.35, "bilayer", fontsize=6, va="top", ha="right")
ax.annotate("1 penetrates own layer", xy=(Lp, Hc + 0.12), xytext=(-1.6, 2.2), fontsize=6, ha="left", va="center",
            arrowprops=dict(arrowstyle="-", lw=0.4, shrinkA=1, shrinkB=0.5))
ax.annotate("2 bridges partner layer", xy=(Lp, -Hc - 0.35), xytext=(-1.6, -2.2), fontsize=6,
            ha="left", va="center", arrowprops=dict(arrowstyle="-", lw=0.4, shrinkA=1, shrinkB=0.5))
ax.set_xlim(-4.0, 4.0); ax.set_ylim(-2.6, 2.6); ax.set_aspect("equal"); ax.axis("off")

letter(fig, 1, 3, "a")

# ================================================================ b  top views
def hex_lattice(nx, ny, d=2.0):
    pts = []
    for j in range(-ny, ny + 1):
        for i in range(-nx, nx + 1):
            pts.append((i * d + (j % 2) * d / 2, j * d * np.sqrt(3) / 2))
    return np.array(pts)


def tile(x0, y0, title, draw):
    ax = ax_mm(fig, x0, y0, 26, 15.9)
    draw(ax)
    ax.set_xlim(-3.9, 3.9); ax.set_ylim(-2.4, 2.4); ax.set_aspect("equal"); ax.axis("off")
    fig.text((x0 + 13) / W_FIG, 1 - (y0 + 16.5) / H_FIG, title, ha="center", va="top", fontsize=6)


def discs(ax, pts, color=PART, alpha=1.0, z=2):
    for (px, py) in pts:
        ax.add_patch(Circle((px, py), 1.0, fc=color, ec="white", lw=0.3, alpha=alpha, zorder=z))


def opening(ax, cx, cy, r):
    ax.add_patch(Circle((cx, cy), r, fc="none", ec=VERM, lw=0.7, zorder=5))


lat = hex_lattice(3, 2)


def t_perfect(ax):
    ax.add_patch(Rectangle((-4, -2.5), 8, 5, fc=WATER, ec="none", zorder=0))
    discs(ax, lat)
    opening(ax, 1.0, 1 / np.sqrt(3), pm.L_HEX - 1)


def t_bond(ax):
    ax.add_patch(Rectangle((-4, -2.5), 8, 5, fc=WATER, ec="none", zorder=0))
    d = 2.4
    yap = np.sqrt(4 - (d / 2) ** 2)
    pts = [(-d / 2, 0), (d / 2, 0), (0, yap), (0, -yap)]
    discs(ax, pts)
    Ls = pm.L_stretched_bond(d)
    for sgn in (+1, -1):
        cy = sgn * (yap - Ls)          # circumcentre of (2,2,d) triangle on the axis
        opening(ax, 0, cy, Ls - 1)


def t_vac(ax):
    ax.add_patch(Rectangle((-4, -2.5), 8, 5, fc=WATER, ec="none", zorder=0))
    pts = [p for p in lat if np.hypot(*p) > 0.1]
    discs(ax, pts)
    opening(ax, 0, 0, 1.0)


def t_bilayer(ax):
    ax.add_patch(Rectangle((-4, -2.5), 8, 5, fc=WATER, ec="none", zorder=0))
    lat2 = lat + np.array([1.0, 1 / np.sqrt(3)])
    discs(ax, lat2, PART2, z=1)
    pts = [p for p in lat if np.hypot(*p) > 0.1]
    discs(ax, pts, PART, z=2)
    opening(ax, 0, 0, 1.0)


letter(fig, 124, 3, "b")
tile(127, 6, "i  close packed, h = 0.155R", t_perfect)
tile(156, 6, "ii  bond gap s = 0.4R", t_bond)
tile(127, 26.5, "iii  vacancy, h = R", t_vac)
tile(156, 26.5, "iv  bilayer, one-layer defect", t_bilayer)

# ================================================================ shared helpers for plots
def phat_mono(h, th=TH):
    return pm.phat_bridge_exact(1 + np.asarray(h), th)


def lab(ax, x, y, s, color, **kw):
    ax.text(x, y, s, color=color, fontsize=6, **kw)


ROW2_Y, ROW2_H = 60, 34
ROW3_Y, ROW3_H = 113, 36
YL_P = "$P_{max}R/2\\gamma$"

# ================================================================ c  contact angle
ax = ax_mm(fig, 13, ROW2_Y, 42, ROW2_H)
thd = np.linspace(1, 89.5, 160)
th = np.radians(thd)
mono_hex = [pm.phat_bridge_exact(pm.L_HEX, t) for t in th]
mono_vac = [pm.phat_bridge_exact(2.0, t) for t in th]
bil_hex = [pm.phat_bilayer(pm.L_HEX, pm.L_HEX, t) for t in th]
bil_vac = [pm.phat_bilayer(2.0, 2.0, t) for t in th]
ax.plot(thd, bil_hex, color=VERM)
ax.plot(thd, bil_vac, color=VERM, ls=(0, (3, 1.5)))
ax.plot(thd, mono_hex, color=BLUE)
ax.plot(thd, mono_vac, color=BLUE, ls=(0, (3, 1.5)))
ax.axvspan(90, 100, color="#e6e6e6", lw=0)
ax.text(95, 0.12, "bridging unstable", rotation=90, ha="center", va="bottom", fontsize=5.5, color="#555555")
ax.set_yscale("log"); ax.set_xlim(0, 100); ax.set_ylim(0.01, 20)
ax.set_xticks([0, 30, 60, 90])
ax.set_xlabel("Contact angle $\\theta$ (°)")
ax.set_ylabel(YL_P)
lab(ax, 5, 9.0, "bilayer", VERM)
lab(ax, 5, 2.4, "monolayer", BLUE)
ax.plot([5, 13], [0.03, 0.03], color=BLACK, lw=0.8)
ax.text(15, 0.03, "close packed", va="center", fontsize=6)
ax.plot([5, 13], [0.015, 0.015], color=BLACK, lw=0.8, ls=(0, (3, 1.5)))
ax.text(15, 0.015, "vacancy", va="center", fontsize=6)
letter(fig, 1, ROW2_Y - 10, "c")

# ================================================================ d  defect size
ax = ax_mm(fig, 74, ROW2_Y, 42, ROW2_H)
h = np.logspace(np.log10(0.155), np.log10(6), 140)
L = 1 + h
ax.plot(h, [pm.phat_bilayer(l, l, TH) for l in L], color=VERM)
ax.plot(h, [pm.phat_bilayer(l, pm.L_HEX, TH) for l in L], color=ORNG, ls=(0, (3, 1.5)))
ax.plot(h, phat_mono(h), color=BLUE)
# markers
hm = [pm.L_HEX - 1] + [pm.L_stretched_bond(2 + s) - 1 for s in S_SHOW] + [1.0]
mk = ["o", "D", "D", "s"]
for hh, m in zip(hm, mk):
    ax.plot(hh, phat_mono(hh), m, color=BLUE, mfc="white", mew=0.7, ms=3.2, zorder=5)
ax.text(hm[0], phat_mono(hm[0]) * 0.72, "i", fontsize=6, va="top", ha="center")
ax.text(hm[2] * 1.02, phat_mono(hm[2]) * 0.72, "ii", fontsize=6, va="top", ha="center")
ax.text(1.0 * 1.12, phat_mono(1.0) * 1.12, "iii", fontsize=6, va="bottom")
# asymptotes
hs = np.array([1.8, 5.0])
ax.plot(hs, 2 * np.cos(TH) / hs ** 2 * 0.5, color=BLACK, lw=0.5)
ax.text(2.6, 0.022, "$\\propto h^{-2}$", fontsize=6, ha="center", va="top")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(0.1, 6); ax.set_ylim(0.01, 20)
ax.set_xticks([0.1, 1]); ax.set_xticklabels(["0.1", "1"]); ax.xaxis.set_minor_formatter(NullFormatter())
ax.set_xlabel("Clear opening $h/R$")
ax.set_ylabel(YL_P)
lab(ax, 0.3, 4.3, "bilayer, one-layer defect (iv)", ORNG, va="center")
lab(ax, 1.5, 0.9, "bilayer,\ncoincident", VERM, va="center")
lab(ax, 0.12, 0.05, "monolayer", BLUE)
letter(fig, 62, ROW2_Y - 10, "d")

# ================================================================ e  spacing
ax = ax_mm(fig, 135, ROW2_Y, 42, ROW2_H)
r = np.linspace(1.0, 1.4, 120)          # d / 2R
d = 2 * r
ax.plot(r, [pm.phat_bilayer(pm.L_uniform(dd), pm.L_uniform(dd), TH) for dd in d], color=VERM, label="bilayer, uniform")
ax.plot(r, [pm.phat_bridge_exact(pm.L_uniform(dd), TH) for dd in d], color=BLUE, label="monolayer, uniform")
ax.plot(r, [pm.phat_bridge_exact(pm.L_stretched_bond(dd), TH) for dd in d], color=BLUE, ls=(0, (3, 1.5)),
        label="monolayer, one stretched bond")
ax.set_xlim(1.0, 1.4); ax.set_yscale("log"); ax.set_ylim(0.01, 20)
ax.set_xticks([1.0, 1.1, 1.2, 1.3, 1.4])
ax.set_xlabel("Centre spacing $d/2R$")
ax.set_ylabel(YL_P)
ax.legend(loc="lower left", handlelength=2.4, borderaxespad=0.4, labelspacing=0.3)
top = ax.secondary_xaxis("top", functions=(lambda x: 0.9069 / np.maximum(x, 1e-3) ** 2,
                                           lambda p: np.sqrt(0.9069 / np.maximum(p, 1e-3))))
top.set_xticks([0.9, 0.8, 0.7, 0.6, 0.5])
top.tick_params(direction="in", length=2, width=0.5)
top.set_xlabel("Coverage $\\phi$ (uniform lattice)", fontsize=6, labelpad=2)
letter(fig, 123, ROW2_Y - 10, "e")

# ================================================================ f  absolute vs particle radius
ax = ax_mm(fig, 13, ROW3_Y, 74, ROW3_H)
R = np.logspace(np.log10(5e-9), -5, 200)
scale = 2 * GAMMA / R
curves = [
    (pm.phat_bilayer(pm.L_HEX, pm.L_HEX, TH), VERM, "-", "bilayer, close packed"),
    (pm.phat_bridge_exact(pm.L_HEX, TH), BLUE, "-", "monolayer, close packed"),
    (pm.phat_bridge_exact(2.0, TH), BLUE, (0, (3, 1.5)), "monolayer, vacancy"),
    (pm.phat_bridge_exact(4.0, TH), BLUE, (0, (1, 1.2)), "monolayer, h = 3R"),
]
for k, c, ls, s in curves:
    ax.plot(R * 1e6, k * scale, color=c, ls=ls, label=s)
for a_um, yoff in [(1, 1.0), (10, 1.0), (100, 1.0)]:
    Pl = 2 * GAMMA / (a_um * 1e-6)
    ax.axhline(Pl, color=GREY, lw=0.5, ls=(0, (1, 1.5)))
    ax.text(6e-3, Pl * 0.85, f"2$\\gamma$/$a$, $a$ = {a_um} µm", color="#555555", fontsize=6, ha="left", va="top")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(5e-3, 10); ax.set_ylim(1e2, 1e8)
ax.set_xticks([0.01, 0.1, 1, 10]); ax.set_xticklabels(["0.01", "0.1", "1", "10"])
ax.set_yticks([1e2, 1e3, 1e4, 1e5, 1e6, 1e7, 1e8])
ax.set_yticklabels(["0.1", "1", "10", "100", "10$^3$", "10$^4$", "10$^5$"])
ax.set_xlabel("Particle radius $R$ (µm)")
ax.set_ylabel("$P_{max}$ (kPa)")
ax.legend(loc="upper right", handlelength=2.4, borderaxespad=0.4, labelspacing=0.3)
letter(fig, 1, ROW3_Y - 6, "f")

# ================================================================ g  critical opening
ax = ax_mm(fig, 108, ROW3_Y, 69, ROW3_H)
ar = np.logspace(1, 4, 160)             # a / R
for thd_, ls in [(50, (0, (3, 1.5))), (70, "-"), (85, (0, (1, 1.2)))]:
    c = np.cos(np.radians(thd_))
    ax.plot(ar, -1 + np.sqrt(1 + 2 * ar * c), color=BLUE, ls=ls, label=f"monolayer, {thd_}°")
# bilayer, coincident defects, theta = 70: invert P_bil(h) = R/a
hgrid = np.logspace(np.log10(0.16), 2.3, 220)
pb = np.array([pm.phat_bilayer(1 + hh, 1 + hh, TH) for hh in hgrid])
hb = np.interp(np.log(1 / ar), np.log(pb[::-1]), np.log(hgrid[::-1]))
ax.plot(ar, np.exp(hb), color=VERM, label="bilayer, coincident, 70°")
ax.axhline(pm.L_HEX - 1, color=GREY, lw=0.5, ls=(0, (1, 1.5)))
ax.text(12, 0.168, "close-packed opening", fontsize=6, color="#555555", va="bottom")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(10, 1e4); ax.set_ylim(0.1, 300)
ax.set_xticks([10, 100, 1000, 10000]); ax.set_xticklabels(["10", "10$^2$", "10$^3$", "10$^4$"])
ax.set_yticks([0.1, 1, 10, 100]); ax.set_yticklabels(["0.1", "1", "10", "100"])
ax.set_xlabel("Drop-to-particle radius ratio $a/R$")
ax.set_ylabel("Critical opening $h^{*}/R$")
ax.legend(loc="lower right", bbox_to_anchor=(1, 0.1), handlelength=2.4, borderaxespad=0.4, labelspacing=0.3)
ax.text(14, 120, "film fails", fontsize=6, color="#333333", va="center")
ax.text(60, 0.42, "film holds", fontsize=6, color="#333333", va="center")
letter(fig, 96, ROW3_Y - 6, "g")

for ext in ("pdf", "svg", "png"):
    fig.savefig(f"fig_pmax_integrated.{ext}", dpi=600 if ext == "png" else None)
print("written")

"""Figure 2 - what would make the work complete for Nature Water: decisive tests with their expected
outcomes. Arc: pin the oxidant (a-c) -> prove and bound the feedback (d-f) -> follow the carbon (g) ->
natural ice and meltwater (h-j). All data panels are simulated expectations (data/simulated/)."""
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle

import common as c
from common import ICE, WATER, NULL, BLACK, PE_C, NP_C, ROS

FW, FH = 183.0, 158.0
X = [9.0, 54.5, 100.0, 145.5]
PW = 35.0
Y1, H1 = 4.0, 46.0
Y2, H2 = 62.0, 32.0
Y3, H3 = 106.0, 44.0
RATE_LIM = (0, 0.9)                   # shared y range for the two oxidation-rate panels

fig = c.fig_mm(FW, FH)
groups = {}


def track(name):
    n_ax, n_tx = len(fig.axes), len(fig.texts)
    return lambda: groups.setdefault(name, []).extend(fig.axes[n_ax:] + fig.texts[n_tx:])


def err(ax, x, y, ye, color, marker="o", label=None, xe=None, ms=3.0):
    return ax.errorbar(x, y, yerr=ye, xerr=xe, fmt=marker, ms=ms, mfc="white", mec=color, mew=0.7,
                       color=color, elinewidth=0.5, capsize=1.0, capthick=0.5, label=label, zorder=4)


# ============================================================== a: discrimination matrix
done = track("a")
AW = X[1] + PW - X[0]
ax = c.canvas_mm(fig, X[0], Y1, AW, H1)
mat = c.sim("hypothesis_matrix.csv")
hyps = ["H1", "H2", "H3", "H4", "H5"]
heads = ["Polymer\nsensitizer", "Freezing\npotential", "Plastic\nsurface", "Nano-\nbubbles", "Contact\ncharging"]
x_lab, x_c0, colw = 0.0, 30.5, (AW - 30.5) / 5
pitch, y_first = 4.45, 34.6
cx = [x_c0 + colw * (i + 0.5) for i in range(5)]
rows_y = [y_first - i * pitch for i in range(len(mat["manipulation"]))]
ax.add_patch(FancyBboxPatch((cx[3] - colw / 2 + 0.3, rows_y[-1] - pitch / 2 + 0.2), colw - 0.6,
                            H1 - 0.2 - (rows_y[-1] - pitch / 2 + 0.2), boxstyle="round,pad=0,rounding_size=1.0",
                            fc="#EEF5FB", ec=ICE, lw=0.7, zorder=0))
for x, h, lab in zip(cx, hyps, heads):
    ax.text(x, H1 - 0.6, h, ha="center", va="top", fontsize=6, fontweight="bold")
    ax.text(x, H1 - 3.5, lab, ha="center", va="top", fontsize=5.2, linespacing=1.05)
ax.text(x_lab, H1 - 0.6, "Manipulation", ha="left", va="top", fontsize=6, fontweight="bold")
ax.text(x_lab, H1 - 3.5, "readout: ROS yield and\nPS oxidation rate in ice", ha="left", va="top", fontsize=5.2,
        linespacing=1.05, color="#555555")
sym = {"v": ("v", BLACK, BLACK), "^": ("^", BLACK, BLACK), "D": ("D", BLACK, BLACK), "o": ("o", "white", NULL)}
for i, (y, man) in enumerate(zip(rows_y, mat["manipulation"])):
    ax.plot([0, AW], [y + pitch / 2, y + pitch / 2], color="#D0D0D0", lw=0.35, zorder=1)
    ax.text(x_lab, y, man, ha="left", va="center", fontsize=5.5)
    for x, h in zip(cx, hyps):
        mk, fc, ec = sym[mat[h][i]]
        ax.plot(x, y, marker=mk, ms=3.6 if mk != "D" else 3.0, mfc=fc, mec=ec, mew=0.6, ls="none", zorder=3)
ax.plot([0, AW], [rows_y[-1] - pitch / 2, rows_y[-1] - pitch / 2], color="#D0D0D0", lw=0.35, zorder=1)
ly, xl = 1.4, 0.0
for mk, fc, ec, s in [("v", BLACK, BLACK, "suppressed"), ("^", BLACK, BLACK, "enhanced"),
                      ("D", BLACK, BLACK, "altered"), ("o", "white", NULL, "unchanged")]:
    ax.plot(xl + 1.0, ly, marker=mk, ms=3.0, mfc=fc, mec=ec, mew=0.6, ls="none")
    ax.text(xl + 2.4, ly, s, ha="left", va="center", fontsize=5.5)
    xl += {"suppressed": 15.5, "enhanced": 13.5, "altered": 11.5}.get(s, 0)
ax.text(AW, ly, "H4 = deck mechanism", ha="right", va="center", fontsize=5.5, color=ICE)
done()

# ============================================================== b: is it a bubble? buoyant-mass sign
done = track("b")
d = c.sim("buoyant_mass.csv")
axb = c.ax_mm(fig, X[2], Y1, PW, H1)
axb.axvline(0, color=BLACK, lw=0.5)
axb.plot(d["mb_fg"], d["melted_ice"], color=ICE, lw=1.0, label="Melted ice")
axb.plot(d["mb_fg"], d["after_pressure"], color=BLACK, lw=0.8, ls=(0, (3, 1.5)), label="After pressure pulse")
axb.text(-2.7, 0.75, "Bubbles\nρ < ρ$_{water}$", ha="center", va="bottom", fontsize=5.5, linespacing=1.05)
axb.text(1.7, 0.42, "Plastic\nfragments", ha="center", va="bottom", fontsize=5.5, linespacing=1.05)
axb.set_xlim(-4.5, 3.0)
axb.set_ylim(0, 2.9)
axb.set_xticks([-4, -2, 0, 2])
axb.set_yticks([0, 1, 2])
axb.set_xlabel("Buoyant mass (fg)")
c.ylabel_mm(axb, "Number (10$^8$ mL$^{-1}$ fg$^{-1}$)")
axb.legend(loc="upper left", bbox_to_anchor=(0.0, 0.9))
c.sim_tag(axb)
done()

# ============================================================== c: does oxidation track bubble number?
done = track("c")
d = c.sim("dose_response.csv")
axc = c.ax_mm(fig, X[3], Y1, PW, H1)
axc.axvspan(2.9, 3.1, color="#E0E0E0", lw=0, zorder=0)
xx = np.linspace(0, 5, 50)
axc.plot(xx, 0.28 * xx / 3.0, color=ICE, lw=0.9, label="H4: rate $\\propto$ bubbles")
axc.plot(xx, 0.28 + 0 * xx, color=NULL, lw=0.9, ls=(0, (3, 1.5)), label="H1–H3, H5")
err(axc, d["nb_mean"], d["rate_mean"], d["rate_sd"], ICE, xe=d["nb_sd"])
lab_pos = {"1 MPa freeze": (0.0, 0.045, "center"), "O$_2$ only": (0.25, 0.0, "left"),
           "Air": (0.0, 0.06, "center"), "O$_2$+Ar": (0.0, 0.07, "center")}
for lab, x, y in zip(d["condition"], d["nb_mean"], d["rate_mean"]):
    dx, dy, ha = lab_pos[lab]
    axc.text(x + dx, y + dy, lab.replace(" freeze", ""), ha=ha, va="center" if ha == "left" else "bottom",
             fontsize=5.2)
axc.text(3.0, 0.03, "deck", ha="center", va="bottom", fontsize=5.0, color="#555555", rotation=90)
axc.set_xlim(0, 5)
axc.set_ylim(*RATE_LIM)
axc.set_xticks([0, 2, 4])
axc.set_yticks([0, 0.3, 0.6, 0.9])
axc.set_xlabel("Nanobubbles (10$^8$ mL$^{-1}$)")
c.ylabel_mm(axc, "Initial rate (ΔO/C per 100 h)")
axc.legend(loc="upper left", bbox_to_anchor=(0.0, 0.9))
c.sim_tag(axc)
done()

# ============================================================== d: grain-mediated vs chemical feedback
done = track("d")
d = c.sim("decoupling.csv")
mdl = c.sim("decoupling_model.csv")
axd = c.ax_mm(fig, X[0], Y2, PW, H2)
axd.plot(mdl["sv_mm"], mdl["grain_mediated"], color=ICE, lw=0.9)
m = (mdl["sv_mm"] > 38) & (mdl["sv_mm"] < 97)
axd.plot(mdl["sv_mm"][m], mdl["rooh_driven"][m], color=NULL, lw=0.9, ls=(0, (3, 1.5)))
axd.text(37, 0.64, "ROOH-driven", ha="right", va="center", fontsize=5.2, color="#666666")
axd.text(100, 0.37, "Grain-mediated", ha="right", va="top", fontsize=5.2, color=ICE)
for series, mk, lab in (("anneal", "o", "Annealed ice"), ("spectator", "^", "+ oxidized spectators")):
    s = d["series"] == series
    err(axd, d["sv_mm"][s], d["rate_mean"][s], d["rate_sd"][s], ICE, marker=mk, label=lab)
axd.set_xlim(0, 105)
axd.set_ylim(*RATE_LIM)
axd.set_yticks([0, 0.3, 0.6, 0.9])
axd.set_xlabel("Grain boundary, S$_v$ (mm$^{-1}$)")
c.ylabel_mm(axd, "Initial rate (ΔO/C per 100 h)")
h, l = axd.get_legend_handles_labels()
axd.legend(h, l, loc="upper left", bbox_to_anchor=(0.0, 0.92), fontsize=5.2, labelspacing=0.15,
           handlelength=1.2)
c.sim_tag(axd, loc="lower right")
done()

# ============================================================== e: ratchet test
done = track("e")
d = c.sim("ratchet.csv")
axe = c.ax_mm(fig, X[1], Y2, PW, H2)
axe.plot(d["cycle"], d["feedback"], color=ICE, lw=0.9, label="Net positive feedback")
axe.plot(d["cycle"], d["replenish"], color=NULL, lw=0.9, ls=(0, (3, 1.5)), label="O$_2$ replenishment only")
axe.plot(d["cycle"], d["passivation"], color=BLACK, lw=0.9, ls=(0, (1, 1)), label="Self-passivation")
err(axe, d["cycle"], d["sim_mean"], d["sim_sd"], ICE)
axe.set_xlim(0.5, 10.5)
axe.set_ylim(0, 3.4)
axe.set_xticks([1, 4, 7, 10])
axe.set_yticks([0, 1, 2, 3])
axe.set_xlabel("Freeze–thaw cycle")
c.ylabel_mm(axe, "Rate constant, k$_n$/k$_1$")
axe.legend(loc="upper left", bbox_to_anchor=(0.0, 0.92), fontsize=5.2, labelspacing=0.15, handlelength=1.2)
c.sim_tag(axe)
done()

# ============================================================== f: Zener bound
done = track("f")
d = c.sim("zener.csv")
bands = c.sim("zener_bands.csv")
bd = {b: (lo, hi) for b, lo, hi in zip(bands["band"], bands["lo"], bands["hi"])}
axf = c.ax_mm(fig, X[2], Y2, PW, H2)
axf.axvspan(*bd["natural"], color="#D6D6D6", lw=0, zorder=0)
axf.axvspan(*bd["lab"], color="#EDEDED", lw=0, zorder=0)
axf.axhspan(*bd["deck_grain_um"], color=c.ICE_FILL, lw=0, zorder=0)
axf.plot(d["f"], d["d_um_r0.25"], color=ICE, lw=0.9, label="0.5 µm MPs")
axf.plot(d["f"], d["d_um_r5"], color=BLACK, lw=0.9, ls=(0, (3, 1.5)), label="10 µm MPs")
axf.text(3e-9, 2e6 * 3, "Natural", ha="left", va="center", fontsize=5.0, rotation=90)
axf.text(1.0e-4, 3e6, "Lab", ha="center", va="center", fontsize=5.0, rotation=90)
axf.text(4e-2, 70, "deck", ha="right", va="center", fontsize=5.0, color=ICE)
axf.set_xscale("log")
axf.set_yscale("log")
axf.set_xlim(1e-9, 1e-1)
axf.set_ylim(10, 1e9)
c.pow10_log(axf.xaxis, [1e-8, 1e-5, 1e-2])
c.pow10_log(axf.yaxis, [1e1, 1e4, 1e7])
axf.set_xlabel("MP volume fraction")
c.ylabel_mm(axf, "Zener grain size (µm)")
axf.legend(loc="lower left", bbox_to_anchor=(0.0, 0.26), fontsize=5.2, labelspacing=0.15, handlelength=1.4)
c.sim_tag(axf, "Calculated")
done()

# ============================================================== g: 13C carbon budget
done = track("g")
mdl = c.sim("carbon_budget_model.csv")
pts = c.sim("carbon_budget_points.csv")
axg = c.ax_mm(fig, X[3], Y2, PW, H2)
for key, col, lab, ls in (("np", NP_C, "Nanoplastics", "-"), ("doc", PE_C, "$^{13}$C-DOC", "-"),
                          ("co2", BLACK, "$^{13}$CO$_2$", "-")):
    axg.plot(mdl["ftc"], mdl[key], color=col, lw=0.9, ls=ls, label=lab)
    axg.plot(pts["ftc"], pts[key], "o", ms=3.0, mfc="white", mec=col, mew=0.7)
axg.plot(mdl["ftc"], mdl["water"], color=WATER, lw=0.9, ls=(0, (3, 1.5)), label="Water control")
axg.set_xlim(0, 125)
axg.set_ylim(0, 5)
axg.set_xticks([0, 50, 100])
axg.set_yticks([0, 2, 4])
axg.set_xlabel("Freeze–thaw cycles")
c.ylabel_mm(axg, "Added $^{13}$C (%)")
axg.legend(loc="upper left", bbox_to_anchor=(0.0, 0.92), fontsize=5.2, labelspacing=0.15, handlelength=1.2)
c.sim_tag(axg, "Illustrative")
done()

# ============================================================== h: field design (schematic)
done = track("h")
HW = X[1] + PW - X[0]
ax = c.canvas_mm(fig, X[0], Y3, HW, H3)
GROUND = 2.5
mtn = [(0, GROUND), (5, 6), (10, 11), (14, 15), (18, 20), (22, 26), (25, 30.5), (27, 33), (29, 31.5),
       (32, 27), (35, 21), (38, 14), (41, 8), (44, GROUND)]
ax.add_patch(Polygon(mtn, closed=True, fc="#D4D4D4", ec="#7F7F7F", lw=0.5, zorder=1))
snow = [(19.33, 22), (22, 26), (25, 30.5), (27, 33), (29, 31.5), (32, 27), (34.5, 22),
        (32.5, 20.9), (30.0, 22.3), (27.5, 21.0), (25.0, 22.2), (22.5, 21.1)]
ax.add_patch(Polygon(snow, closed=True, fc="white", ec="#7F7F7F", lw=0.5, zorder=2))
ax.plot([0, 45.5], [GROUND, GROUND], color="#7F7F7F", lw=0.5, zorder=1)


def trio(x, y, s=1.35, gap=0.3):
    for i, fc in enumerate(("white", BLACK, WATER)):
        ax.add_patch(Rectangle((x + i * (s + gap), y), s, s, fc=fc, ec=BLACK, lw=0.4, zorder=5))
    xm = x + 1.5 * s + gap
    ax.plot([xm, xm], [y - 1.3, y], color=BLACK, lw=0.4, zorder=4)


trio(2.0, 7.4)
trio(11.0, 16.5)
trio(21.0, 29.8)
txt = dict(ha="left", va="center", fontsize=5.2, linespacing=1.05, zorder=6)
ax.text(8.6, 4.4, "Low: few freeze–thaw cycles (FTC)", **txt)
ax.text(16.2, 13.6, "Mid: most FTC", **txt)
ax.text(29.6, 33.6, "High: mostly\nfrozen, high UV", **txt)
# lysimeter under the mid station -> meltwater (panel j)
lx, ly0 = 14.6, 10.0
ax.add_patch(Polygon([(lx - 1.3, ly0 + 1.3), (lx + 1.3, ly0 + 1.3), (lx + 0.35, ly0), (lx - 0.35, ly0)],
                     closed=True, fc=c.VEIN, ec=BLACK, lw=0.4, zorder=5))
c.arrow(ax, (lx + 0.6, ly0 + 0.2), (19.6, 8.2), lw=0.5, color=ICE, rad=0.2)
ax.text(20.0, 8.2, "Lysimeter → j", ha="left", va="center", fontsize=5.2, color=ICE, zorder=6)
# snow/firn pit at the high station (upper left)
px, py, pw, ph = 0.5, 26.0, 6.4, 13.6
shades = ["#FFFFFF", "#EEF6FC", "#DCEEF9", "#C8E3F5"]
for i, (sh, lb) in enumerate(zip(shades, ["fresh", "weeks", "months", "seasons"])):
    y0 = py + ph - (i + 1) * ph / 4
    ax.add_patch(Rectangle((px, y0), pw, ph / 4, fc=sh, ec="#7F7F7F", lw=0.4, zorder=3))
    for j in range(2):
        c.mp(ax, px + 1.8 + 2.8 * j, y0 + ph / 8, 0.55, oxidized=i >= 2, lw=0.35)
    ax.text(px + pw + 0.7, y0 + ph / 8, lb, ha="left", va="center", fontsize=5.0)
ax.text(px, py + ph + 0.5, "Snow/firn pit: native MPs", ha="left", va="bottom", fontsize=5.2)
ax.plot([15.0, 20.6], [33.5, 31.0], color=BLACK, lw=0.35, ls=(0, (2, 1)), zorder=3)
# right-hand column: what not to do, cassette design, lab twin
rx, rw = 47.0, HW - 47.0
c.cross(ax, rx + 0.2, H3 - 2.4, s=1.7)
ax.text(rx + 2.9, H3 - 0.3, "One summit sample over time:\nunknown t$_0$, UV-aged on arrival,\nno counterfactual",
        ha="left", va="top", fontsize=5.0, linespacing=1.1)
by, bh = 22.5, 14.0
ax.add_patch(FancyBboxPatch((rx, by), rw, bh, boxstyle="round,pad=0,rounding_size=0.8",
                            fc="white", ec="#7F7F7F", lw=0.45, zorder=3))
ax.text(rx + 1.0, by + bh - 0.6, "Cassette trio per station\n$^{13}$C-PS, PE, PET; known t$_0$",
        ha="left", va="top", fontsize=5.0, linespacing=1.1, zorder=4)
for i, (fc, lab) in enumerate((("white", "Exposed"), (BLACK, "Dark"), (WATER, "Unfrozen\n+2 °C"))):
    x0 = rx + 3.0 + i * 10.6
    ax.add_patch(Rectangle((x0, by + 4.6), 3.2, 3.2, fc=fc, ec=BLACK, lw=0.45, zorder=4))
    for k in range(3):
        ax.add_patch(Circle((x0 + 0.75 + k * 0.85, by + 6.2), 0.3, fc=c.MP_FILL if fc != BLACK else "#BDBDBD",
                            ec=c.MP_EDGE, lw=0.3, zorder=5))
    ax.text(x0 + 1.6, by + 4.0, lab, ha="center", va="top", fontsize=5.0, linespacing=1.0, zorder=4)
ty, th = GROUND, 18.0
ax.add_patch(FancyBboxPatch((rx, ty), rw, th, boxstyle="round,pad=0,rounding_size=0.8", fc="white",
                            ec="#7F7F7F", lw=0.45, zorder=3))
ax.text(rx + 1.0, ty + th - 0.6, "Lab twin: replay the logged\ntemperature and light record",
        ha="left", va="top", fontsize=5.0, linespacing=1.1, zorder=4)
tt = np.linspace(0, 1, 300)
temp = 3.0 * np.sin(2 * np.pi * 5.5 * tt) + 1.3 * np.sin(2 * np.pi * 1.2 * tt + 1.0) - 0.6
gx0, gy0, gw, gh = rx + 5.6, ty + 1.5, rw - 7.1, 9.5
ax.plot([gx0 - 0.4, gx0 + gw], [gy0 + gh / 2, gy0 + gh / 2], color=NULL, lw=0.4, ls=(0, (2, 1)), zorder=4)
ax.plot(gx0 + gw * tt, gy0 + gh / 2 + temp * gh / 10.5, color=ICE, lw=0.6, zorder=5)
ax.text(gx0 - 0.6, gy0 + gh / 2, "0 °C", ha="right", va="center", fontsize=4.8, color="#555555", zorder=6)
c.arrow(ax, (25.0, 31.6), (rx - 0.2, ty + th * 0.55), lw=0.45, color=BLACK, rad=0.25, ls=(0, (2, 1)))
done()

# ============================================================== i: field dose-response
done = track("i")
pts = c.sim("field_points.csv")
mdl = c.sim("field_model.csv")
axi = c.ax_mm(fig, X[2], Y3, PW, H3)
style = {"ps_ftc": (ICE, "PS, freeze–thaw"), "pe_ftc": (PE_C, "PE, freeze–thaw"),
         "ps_unfrozen": (WATER, "PS, unfrozen control")}
marks = {"low": "o", "mid": "s", "high": "^"}
for trt, (col, lab) in style.items():
    axi.plot(mdl["ftc"], mdl[trt], color=col, lw=0.9, label=lab)
    for st, mk in marks.items():
        s = (pts["treatment"] == trt) & (pts["station"] == st)
        axi.plot(pts["ftc"][s], pts["d_oc"][s], mk, ms=3.0, mfc="white", mec=col, mew=0.7, ls="none")
axi.set_xlim(0, 125)
axi.set_ylim(0, 0.3)
axi.set_xticks([0, 50, 100])
axi.set_yticks([0, 0.1, 0.2, 0.3])
axi.set_xlabel("Freeze–thaw cycles in field")
c.ylabel_mm(axi, "ΔO/C, dark cassettes")
leg1 = axi.legend(loc="upper left", bbox_to_anchor=(0.0, 0.93), fontsize=5.2, labelspacing=0.15,
                  handlelength=1.2)
axi.add_artist(leg1)
hs = [Line2D([], [], marker=mk, ms=3.0, mfc="white", mec=BLACK, mew=0.6, ls="none") for mk in marks.values()]
axi.legend(hs, ["Low", "Mid", "High"], loc="lower right", fontsize=5.2, ncol=3, columnspacing=0.6,
           handletextpad=0.1, bbox_to_anchor=(1.0, 0.25))
c.sim_tag(axi)
done()

# ============================================================== j: meltwater first flush
done = track("j")
mdl = c.sim("meltwater_model.csv")
pts = c.sim("meltwater_points.csv")
axj = c.ax_mm(fig, X[3], Y3, PW, H3)
axj.axhline(1, color="#BBBBBB", lw=0.5, ls=(0, (2, 1)), zorder=0)
axj.plot(mdl["F"], mdl["chloride"], color=BLACK, lw=0.9, label="Cl$^-$ (tracer)")
axj.plot(mdl["F"], mdl["products"], color=PE_C, lw=0.9, label="Oxidized products")
axj.plot(pts["F"], pts["products"], "o", ms=3.0, mfc="white", mec=PE_C, mew=0.7)
axj.plot(mdl["F"], mdl["nanoplastics"], color=NP_C, lw=0.9, ls=(0, (3, 1.5)), label="Nanoplastics")
axj.plot(mdl["F"], mdl["microplastics"], color=NULL, lw=0.9, ls=(0, (1, 1)), label="MPs > 10 µm")
axj.set_xlim(0, 1)
axj.set_ylim(0, 5.0)
axj.set_xticks([0, 0.5, 1])
axj.set_yticks([0, 1, 2, 3, 4])
axj.set_xlabel("Snowpack melted (fraction)")
c.ylabel_mm(axj, "Concentration factor, C/$\\bar{C}$")
axj.legend(loc="upper right", bbox_to_anchor=(1.0, 0.92), fontsize=5.2, labelspacing=0.15, handlelength=1.4)
c.sim_tag(axj)
done()

# ============================================================== letters
rims = c.panel_rims(fig, groups)
for name, y in [("a", Y1), ("d", Y2), ("h", Y3)]:
    c.letter(fig, 1.0, y - 3.1 if name != "a" else 0.6, name)
for name, y in [("b", Y1), ("c", Y1), ("e", Y2), ("f", Y2), ("g", Y2), ("i", Y3), ("j", Y3)]:
    c.letter(fig, rims[name][0], y - 3.1 if y != Y1 else 0.6, name)

c.audit(fig, groups, [["a", "b", "c"], ["d", "e", "f", "g"], ["h", "i", "j"]])
c.save(fig, "fig2_roadmap")

"""Figure 1 - the story as it stands: key message (schematic), logic spine with evidence status, and the
deck's own data re-plotted one panel per spine step (values digitized from the 2026-10-23 deck)."""
import numpy as np
from matplotlib.patches import Arc, Circle, FancyBboxPatch, Polygon, Rectangle

import common as c
from common import ICE, WATER, NULL, BLACK, ROS

FW, FH = 183.0, 158.5
X = [9.0, 54.5, 100.0, 145.5]        # data-box left lines of the 4-column grid
PW = 35.0                            # plot width
R_EDGE = X[3] + PW                   # 180.5
Y1, H1 = 4.0, 56.0                   # row 1: schematics
Y2, H2 = 66.1, 35.0                  # row 2
Y3, H3 = 113.2, 35.0                 # row 3

fig = c.fig_mm(FW, FH)
groups = {}


def track(name):
    n_ax, n_tx = len(fig.axes), len(fig.texts)
    return lambda: groups.setdefault(name, []).extend(fig.axes[n_ax:] + fig.texts[n_tx:])


# ============================================================== a: key-message schematic
done = track("a")
A_W = X[2] + PW - X[0]               # spans columns 1-3 (9 -> 135 mm)
ax = c.canvas_mm(fig, X[0], Y1, A_W, H1)
FT, FB = 47.0, 18.5                  # frame top / bottom (canvas mm, y up)
fx = {"A1": (0.0, 34.0), "A2": (41.0, 83.0), "A3": (90.0, A_W)}

# --- A1: coarse ice, pristine MPs, few bubbles
x0, x1 = fx["A1"]
cells = c.voronoi_cells(x0 + 0.3, FB + 0.3, x1 - x0 - 0.6, FT - FB - 0.6, 3, 3, jitter=0.32, seed=4)
c.draw_ice(ax, cells, vein_lw=1.8, edge_lw=0.6)
vs = c.interior_vertices(cells, x0, FB, x1 - x0, FT - FB, margin=2.0)
rng = np.random.default_rng(7)
mp_sites = vs[: min(6, len(vs))]
for (vx, vy) in mp_sites:
    c.mp(ax, vx, vy, 1.25)
    a = rng.uniform(0, 2 * np.pi)
    c.bubble(ax, vx + 1.75 * np.cos(a), vy + 1.75 * np.sin(a), 0.5)
zoom_site = mp_sites[0]
ax.add_patch(Circle(zoom_site, 2.6, fc="none", ec=BLACK, lw=0.5, ls=(0, (2, 1)), zorder=9))
c.frame(ax, x0, FB, x1 - x0, FT - FB)

# --- A2: grain-boundary microreactor (zoom)
x0, x1 = fx["A2"]
ax.add_patch(Rectangle((x0, FB), x1 - x0, FT - FB, fc=c.VEIN, ec="none", zorder=1))
top = [(x0, FT), (x1, FT), (x1, 37.4), (76, 38.0), (68, 37.3), (58, 38.3), (49, 37.2), (x0, 37.8)]
bot = [(x0, FB), (x1, FB), (x1, 25.6), (75, 25.0), (66, 25.9), (56, 25.0), (48, 25.8), (x0, 25.3)]
for poly in (top, bot):
    ax.add_patch(Polygon(poly, closed=True, fc=c.ICE_FILL, ec=c.BOUNDARY, lw=0.6, zorder=2))
mx, my, mr = 63.0, 31.6, 5.0
c.mp(ax, mx, my, mr, lw=0.5)
ax.add_patch(Arc((mx, my), 2 * mr, 2 * mr, theta1=135, theta2=245, color=c.OX_FILL, lw=2.0, zorder=4.6))
ax.add_patch(Arc((mx, my), 2 * mr, 2 * mr, theta1=-40, theta2=0, color=c.OX_FILL, lw=2.0, zorder=4.6))
ax.text(mx + 0.6, my - 0.2, "–OH\nC=O", ha="center", va="center", fontsize=5.5, zorder=6, linespacing=1.0)
rb = 1.25
for ang in (150, 192, 228, -20):
    t = np.deg2rad(ang)
    bx, by = mx + (mr + rb) * np.cos(t), my + (mr + rb) * np.sin(t)
    c.bubble(ax, bx, by, rb)
    cx, cy = mx + (mr + 0.35) * np.cos(t), my + (mr + 0.35) * np.sin(t)
    off = rng.normal(0, 0.45, (3, 2))
    c.ros_dots(ax, cx + off[:, 0], cy + off[:, 1], s=2.2)
# free bubble out of reach
fb = (47.0, 31.0)
c.bubble(ax, *fb, rb)
ax.add_patch(Circle(fb, 3.0, fc="none", ec=ROS, lw=0.5, ls=(0, (2, 1.2)), zorder=5))
ang = rng.uniform(0, 2 * np.pi, 6)
rad = rng.uniform(rb + 0.3, 2.7, 6)
c.ros_dots(ax, fb[0] + rad * np.cos(ang), fb[1] + rad * np.sin(ang), s=2.2)
# chain scission products
c.arrow(ax, (mx + mr + 0.3, my + 2.4), (74.2, 33.6), lw=0.5)
for (px, py, s) in [(75.6, 34.2, 0.45), (77.8, 33.0, 0.35), (79.6, 34.6, 0.4), (77.0, 35.6, 0.3), (80.8, 32.7, 0.3)]:
    ax.add_patch(Circle((px, py), s, fc=c.OX_FILL, ec="none", zorder=5))
# labels
lab = dict(fontsize=5.5, zorder=10)
ax.text(x0 + 1.0, FT - 1.2, "Ice grain", ha="left", va="top", **lab)
ax.text(x0 + 1.0, 36.6, "Liquid vein", ha="left", va="top", **lab)
ax.text(55.0, 41.2, "Nanobubble", ha="center", va="bottom", **lab)
ax.plot([55.6, 56.6], [41.1, 36.6], color=BLACK, lw=0.35, zorder=10)
ax.text(71.5, 41.2, "Microplastic", ha="center", va="bottom", **lab)
ax.plot([70.6, 66.4], [41.1, 35.3], color=BLACK, lw=0.35, zorder=10)
ax.text(47.6, 23.9, "Beyond reach\n(¹O₂ ≈ 150 nm)", ha="center", va="top", linespacing=1.0, **lab)
ax.text(x1 - 0.8, 23.9, "S5  Chain scission\n→ small molecules", ha="right", va="top", linespacing=1.0, **lab)
c.frame(ax, x0, FB, x1 - x0, FT - FB)
# zoom connectors from A1 site to A2 frame corners
for (ty) in (FT, FB):
    ax.plot([zoom_site[0] + 1.8, x0], [zoom_site[1] + (1.8 if ty == FT else -1.8), ty],
            color=BLACK, lw=0.35, ls=(0, (2, 1)), zorder=9)

# --- A3: fine ice, oxidized MPs, more bubbles
x0, x1 = fx["A3"]
cells3 = c.voronoi_cells(x0 + 0.3, FB + 0.3, x1 - x0 - 0.6, FT - FB - 0.6, 6, 5, jitter=0.32, seed=11)
c.draw_ice(ax, cells3, vein_lw=1.3, edge_lw=0.5)
vs3 = c.interior_vertices(cells3, x0, FB, x1 - x0, FT - FB, margin=1.5)
rng3 = np.random.default_rng(3)
pick = rng3.choice(len(vs3), size=min(6, len(vs3)), replace=False)
for (vx, vy) in vs3[pick]:
    c.mp(ax, vx, vy, 1.0, oxidized=True)
others = np.setdiff1d(np.arange(len(vs3)), pick)
for (vx, vy) in vs3[rng3.choice(others, size=min(14, len(others)), replace=False)]:
    c.bubble(ax, vx, vy, 0.45)
for (vx, vy) in vs3[pick]:
    a = rng3.uniform(0, 2 * np.pi)
    c.bubble(ax, vx + 1.4 * np.cos(a), vy + 1.4 * np.sin(a), 0.45)
c.frame(ax, x0, FB, x1 - x0, FT - FB)

# --- arrows and headers
c.arrow(ax, (83.6, 32.0), (89.4, 32.0), lw=0.7)
c.arrow(ax, (fx["A3"][0] + 18.0, FB - 0.4), (fx["A1"][0] + 17.0, FB - 0.4), rad=-0.17, lw=0.7, color=ICE)
ax.text(62.0, 16.6, "S4  Finer ice → more boundary and nanobubbles\n→ faster oxidation (proposed positive feedback)",
        ha="center", va="top", fontsize=6, color=ICE, linespacing=1.05)
hdr = dict(fontsize=6, ha="center", va="top", linespacing=1.1)
ax.text(17.0, H1 - 0.3, "S2  Freezing expels gas\nas grain-boundary nanobubbles", **hdr)
ax.text(62.0, H1 - 0.3, "S3  ROS from attached nanobubbles\noxidize only the MPs they touch", **hdr)
ax.text((fx["A3"][0] + A_W) / 2, H1 - 0.3, "S4  Oxidized, hydrophilic MPs\ninhibit recrystallization", **hdr)

# --- legend row
ly = 1.6
items = []
xcur = 1.0
def leg_text(x, s):
    return ax.text(x, ly, s, ha="left", va="center", fontsize=5.5)
c.mp(ax, xcur + 0.9, ly, 0.9); leg_text(xcur + 2.3, "Microplastic"); xcur += 17
c.mp(ax, xcur + 0.9, ly, 0.9, oxidized=True); leg_text(xcur + 2.3, "Oxidized MP"); xcur += 17
c.bubble(ax, xcur + 0.7, ly, 0.6); leg_text(xcur + 2.0, "Nanobubble"); xcur += 16
c.ros_dots(ax, [xcur + 0.7], [ly], s=5); leg_text(xcur + 2.0, "ROS (¹O₂ as proposed)"); xcur += 27
ax.add_patch(Rectangle((xcur, ly - 0.9), 2.4, 1.8, fc=c.ICE_FILL, ec=c.BOUNDARY, lw=0.5)); leg_text(xcur + 3.2, "Ice grain"); xcur += 14
ax.add_patch(Rectangle((xcur, ly - 0.9), 2.4, 1.8, fc=c.VEIN, ec="none")); leg_text(xcur + 3.2, "Liquid vein")
done()

# ============================================================== b: logic spine with evidence status
done = track("b")
GUT = 8.0                                    # balls hang into the column gutter
axb = c.canvas_mm(fig, X[3] - GUT, Y1, PW + GUT, H1)
steps = [
    ("S1", "Ice, not water, oxidizes C–H\npolymers; PTFE inert   → c", 1),
    ("S2", "Freezing makes nanobubbles\nthat generate ROS   → d", 0),
    ("S3", "Bubbles meet MPs at grain\nboundaries; size effect   → e", 0.5),
    ("S4", "Oxidized MPs refine ice, more\nbubbles, faster oxidation  → f–h", 0.5),
    ("S5", "Chain scission to small\nmolecules (PS only)   → i", 0.5),
    ("S6", "Operates in natural ice\nand meltwater   → Fig. 2", 0),
]
bh, bg = 7.3, 1.55
ytop = H1 - 0.2
bx = 2.6
centers = []
for i, (tag, txt, lvl) in enumerate(steps):
    y_hi = ytop - i * (bh + bg)
    y_lo = y_hi - bh
    centers.append((y_hi + y_lo) / 2)
    axb.add_patch(FancyBboxPatch((GUT, y_lo), PW, bh, boxstyle="round,pad=0,rounding_size=0.8",
                                 fc="white" if lvl < 1 else "#F2F7FB", ec="#7F7F7F", lw=0.45))
    axb.text(GUT + 1.0, y_hi - 0.9, tag, ha="left", va="top", fontsize=6, fontweight="bold")
    axb.text(GUT + 5.0, y_hi - 0.9, txt, ha="left", va="top", fontsize=5.5, linespacing=1.15)
axb.plot([bx, bx], [centers[0], centers[-1]], color=BLACK, lw=0.6, zorder=1)
for yc, (_, _, lvl) in zip(centers, steps):
    c.harvey(axb, bx, yc, 1.45, lvl, lw=0.55)
    axb.plot([bx + 1.45, GUT], [yc, yc], color=BLACK, lw=0.4)
ly = 1.6
for xl, lvl, s in [(GUT + 0.2, 1, "supported"), (GUT + 13.0, 0.5, "partial"), (GUT + 22.2, 0, "unproven")]:
    c.harvey(axb, xl + 0.9, ly, 0.9, lvl, lw=0.45)
    axb.text(xl + 2.2, ly, s, ha="left", va="center", fontsize=5.5)
done()

# ============================================================== row 2
# c: O/C by polymer, with stoichiometric O/C
done = track("c")
d = c.deck("polymer_oc.csv")
axc = c.ax_mm(fig, X[0], Y2, X[1] + PW - X[0], H2)
xs = np.arange(len(d["polymer"]))
bw = 0.36
hw = axc.bar(xs - bw / 2, d["oc_water"], bw, color=WATER, lw=0, label="Water, 20 °C")
hi = axc.bar(xs + bw / 2, d["oc_ice"], bw, color=ICE, lw=0, label="Ice, −20 °C")
hs = None
for xi, s, has_o in zip(xs, d["oc_stoich"], d["contains_O"]):
    if has_o:
        (ln,) = axc.plot([xi - 0.44, xi + 0.44], [s, s], color=BLACK, lw=0.9, label="Stoichiometric O/C")
        hs = hs or ln
axc.set_xticks(xs)
axc.set_xticklabels([p + ("†" if p == "PVA" else "") for p in d["polymer"]])
axc.set_xlim(-0.6, len(xs) - 0.4)
axc.set_ylim(0, 0.6)
axc.set_yticks([0, 0.2, 0.4, 0.6])
c.ylabel_mm(axc, "O/C (XPS)")
axc.legend(handles=[hw, hi, hs], loc="upper left", bbox_to_anchor=(0.0, 1.0))
c.step_tag(axc, "S1", 1, loc="upper right")
done()

# d: nanobubbles through freeze/melt
done = track("d")
d = c.deck("nanobubble_freeze_melt.csv")
ph = c.deck("freeze_melt_phases.csv")
axd = c.ax_mm(fig, X[2], Y2, PW, H2)
for p, s, e in zip(ph["phase"], ph["start_h"], ph["end_h"]):
    if p == "frozen":
        axd.axvspan(s, e, color=c.ICE_FILL, lw=0, zorder=0)
axd.plot(d["time_h"], d["conc_1e8_mL"], color=ICE, lw=0.6, zorder=2)
axd.errorbar(d["time_h"], d["conc_1e8_mL"], yerr=d["err"], fmt="o", ms=2.4, color=ICE, mfc=ICE,
             mew=0, elinewidth=0.5, capsize=1.0, capthick=0.5, zorder=3)
axd.text(24.2, 3.9, "Frozen", ha="center", va="top", fontsize=5)
axd.set_xlim(0, 292)
axd.set_ylim(0, 4.0)
axd.set_yticks([0, 1, 2, 3, 4])
axd.set_xticks([0, 100, 200])
axd.set_xlabel("Time (h)")
c.ylabel_mm(axd, "Nanobubbles (10$^8$ mL$^{-1}$)")
c.step_tag(axd, "S2", 0, loc="upper right")
done()

# e: O/C vs PS size
done = track("e")
d = c.deck("ps_size_oc.csv")
axe = c.ax_mm(fig, X[3], Y2, PW, H2)
axe.plot(d["diameter_nm"], d["oc_ice"], "-o", color=ICE, ms=2.6, mew=0, lw=0.75, label="Ice, −20 °C")
axe.plot(d["diameter_nm"], d["oc_water"], "-o", color=WATER, ms=2.6, mew=0, lw=0.75, label="Water, 20 °C")
axe.set_xscale("log")
c.pow10_log(axe.xaxis, [1e2, 1e3, 1e4])
axe.set_xlim(60, 17000)
axe.set_ylim(0, 0.3)
axe.set_yticks([0, 0.1, 0.2, 0.3])
axe.set_xlabel("PS diameter (nm)")
c.ylabel_mm(axe, "O/C (XPS)")
axe.legend(loc="center right", bbox_to_anchor=(1.0, 0.33))
c.step_tag(axe, "S3", 0.5, loc="upper left")
done()

# ============================================================== row 3
# f: grain size vs O/C
done = track("f")
d = c.deck("grain_vs_oc.csv")
axf = c.ax_mm(fig, X[0], Y3, PW, H3)
axf.errorbar(d["oc"], d["grain_um"], yerr=d["err"], fmt="o", ms=2.6, color=ICE, mew=0,
             elinewidth=0.5, capsize=1.0, capthick=0.5)
axf.set_xlim(-0.01, 0.23)
axf.set_ylim(0, 80)
axf.set_xticks([0, 0.1, 0.2])
axf.set_xlabel("O/C of embedded PS")
c.ylabel_mm(axf, "Ice grain size (µm)")
c.step_tag(axf, "S4", 0.5, loc="upper right")
done()

# g: nanobubbles vs grain size, against geometric scalings
done = track("g")
d = c.deck("bubbles_vs_grain.csv")
axg = c.ax_mm(fig, X[1], Y3, PW, H3)
gx = np.geomspace(12, 400, 50)
ref_x, ref_y = d["grain_um"][-1], d["conc_1e8_mL"][-1]
axg.plot(gx, ref_y * (ref_x / gx), color=NULL, lw=0.7, ls=(0, (3, 1.5)))
axg.plot(gx, ref_y * (ref_x / gx) ** 2, color=NULL, lw=0.7, ls=(0, (1, 1)))
axg.errorbar(d["grain_um"], d["conc_1e8_mL"], yerr=d["err"], fmt="o", ms=2.6, color=ICE, mew=0,
             elinewidth=0.5, capsize=1.0, capthick=0.5, zorder=3)
slope = np.polyfit(np.log(d["grain_um"]), np.log(d["conc_1e8_mL"]), 1)[0]
print(f"bubble-vs-grain log-log slope: {slope:.2f}")
axg.text(30, 9.5, "d$^{-1}$", color="#666666", fontsize=6, ha="left", va="bottom")
axg.text(60, 17.0, "d$^{-2}$", color="#666666", fontsize=6, ha="left", va="bottom")
axg.text(14, 0.55, f"fit slope {slope:.1f}".replace("-", "−"), color=ICE, fontsize=5.5, ha="left", va="bottom")
axg.set_xscale("log")
axg.set_yscale("log")
c.plain_log(axg.xaxis, [20, 50, 100, 200])
c.plain_log(axg.yaxis, [1, 10])
axg.set_xlim(12, 400)
axg.set_ylim(0.4, 40)
axg.set_xlabel("Ice grain size (µm)")
c.ylabel_mm(axg, "Nanobubbles (10$^8$ mL$^{-1}$)")
c.step_tag(axg, "S4", 0.5, loc="upper right")
done()

# h: oxidation kinetics with melt-refreeze
done = track("h")
d = c.deck("oc_cycles.csv")
axh = c.ax_mm(fig, X[2], Y3, PW, H3)
style = {"cycle0": ("No refreeze", "#56B4E9"), "cycle1": ("Refreeze at 72 h", ICE),
         "cycle2": ("+ refreeze at 217 h", BLACK)}
for key, (lab, col) in style.items():
    m = d["series"] == key
    axh.plot(d["time_h"][m], d["oc"][m], "-o", color=col, ms=2.4, mew=0, lw=0.75, label=lab)
for t in (72.3, 216.8):
    axh.axvline(t, color=NULL, lw=0.5, ls=(0, (2, 1.5)), zorder=0)
axh.set_xlim(0, 350)
axh.set_ylim(0, 0.2)
axh.set_xticks([0, 100, 200, 300])
axh.set_yticks([0, 0.1, 0.2])
axh.set_xlabel("Time at −20 °C (h)")
c.ylabel_mm(axh, "O/C of PS (XPS)")
axh.legend(loc="lower right", bbox_to_anchor=(1.0, 0.03))
c.step_tag(axh, "S4", 0.5, loc="upper right")
done()

# i: Mw change by polymer, vs GPC reproducibility
done = track("i")
d = c.deck("mw_change.csv")
axi = c.ax_mm(fig, X[3], Y3, PW, H3)
chg = 100 * (d["mw_after"] / d["mw_before"] - 1)
xs = np.arange(len(chg))
axi.axhspan(-10, 10, color="#E6E6E6", lw=0, zorder=0)
axi.axhline(0, color=BLACK, lw=0.5)
axi.bar(xs, chg, 0.55, color=ICE, lw=0, zorder=2)
axi.text(len(xs) - 0.45, 8.5, "±10%", ha="right", va="top", fontsize=5.5, color="#555555")
axi.set_xticks(xs)
axi.set_xticklabels(d["polymer"])
axi.set_xlim(-0.6, len(xs) - 0.4)
axi.set_ylim(-60, 12)
axi.set_yticks([-60, -40, -20, 0])
c.ylabel_mm(axi, "Change in M$_w$ (%)")
c.step_tag(axi, "S5", 0.5, loc="lower right")
done()

# ============================================================== letters (left column shares x; others at rim)
rims = c.panel_rims(fig, groups)
LX = 1.0
letters = {}
for name, y in [("a", Y1), ("c", Y2), ("f", Y3)]:
    letters[name] = c.letter(fig, LX, y - 3.1 if name != "a" else 0.6, name)
for name, y in [("b", Y1), ("d", Y2), ("e", Y2), ("g", Y3), ("h", Y3), ("i", Y3)]:
    letters[name] = c.letter(fig, rims[name][0], y - 3.1 if name != "b" else 0.6, name)

c.audit(fig, groups, [["a", "b"], ["c", "d", "e"], ["f", "g", "h", "i"]])
c.save(fig, "fig1_current_spine")

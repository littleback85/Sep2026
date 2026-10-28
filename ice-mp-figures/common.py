"""Shared Nature-style preset, mm-grid helpers and schematic primitives."""
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle, Wedge
from scipy.spatial import Voronoi

HERE = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.join(HERE, "data", "deck")
SIM = os.path.join(HERE, "data", "simulated")
OUT = os.path.join(HERE, "out")

MM = 1 / 25.4
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
    "font.size": 6, "axes.labelsize": 7, "xtick.labelsize": 6, "ytick.labelsize": 6, "legend.fontsize": 6,
    "axes.linewidth": 0.5, "lines.linewidth": 1, "lines.markersize": 3,
    "xtick.major.width": 0.5, "ytick.major.width": 0.5, "xtick.major.size": 2, "ytick.major.size": 2,
    "xtick.minor.width": 0.4, "ytick.minor.width": 0.4, "xtick.minor.size": 1.2, "ytick.minor.size": 1.2,
    "xtick.minor.visible": False, "ytick.minor.visible": False,
    "xtick.direction": "in", "ytick.direction": "in", "xtick.top": False, "ytick.right": False,
    "axes.labelpad": 1.5, "xtick.major.pad": 1.5, "ytick.major.pad": 1.5,
    "legend.frameon": False, "legend.handlelength": 1.4, "legend.handletextpad": 0.4,
    "legend.borderpad": 0.2, "legend.labelspacing": 0.25,
    "pdf.fonttype": 42, "svg.fonttype": "none", "savefig.dpi": 600,
    "mathtext.default": "regular",
})

# Okabe-Ito, with fixed meanings across both figures
ICE = "#0072B2"       # frozen condition / nanobubble hypothesis (this work)
WATER = "#E69F00"     # liquid water / unfrozen control
PE_C = "#009E73"      # polyethylene; also DOC/small-molecule products
NP_C = "#CC79A7"      # nanoplastics
ROS = "#D55E00"       # reactive oxygen species (schematics)
SKY = "#56B4E9"
BLACK = "#000000"
NULL = "#999999"      # null / rival-hypothesis expectation

ICE_FILL = "#E4F1FA"
VEIN = "#A8D2EF"
BOUNDARY = "#56B4E9"
MP_FILL = "#DADADA"
MP_EDGE = "#5A5A5A"
OX_FILL = "#8E8E8E"


def fig_mm(w, h):
    return plt.figure(figsize=(w * MM, h * MM))


def ax_mm(fig, x, y, w, h):
    """Axes DATA BOX at x,y (mm from figure top-left), size w x h mm. Labels hang outside it."""
    W, H = fig.get_size_inches() / MM
    return fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])


def canvas_mm(fig, x, y, w, h):
    """Schematic canvas whose data units are millimetres (origin bottom-left)."""
    ax = ax_mm(fig, x, y, w, h)
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    return ax


YLAB_MM = 4.7   # right edge of every y-axis title sits this far left of its data box -> equal rims


def ylabel_mm(ax, text, off=YLAB_MM):
    fig = ax.figure
    w_mm = ax.get_position().width * fig.get_size_inches()[0] / MM
    ax.set_ylabel(text)
    ax.yaxis.set_label_coords(-off / w_mm, 0.5)


def plain_log(axis, ticks):
    """Fixed, plainly labelled ticks on a log axis, minor ticks off."""
    from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator
    axis.set_major_locator(FixedLocator(ticks))
    axis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    axis.set_minor_locator(NullLocator())


def pow10_log(axis, ticks):
    from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator
    axis.set_major_locator(FixedLocator(ticks))
    axis.set_major_formatter(FuncFormatter(lambda v, _: f"10$^{{{int(round(np.log10(v)))}}}$"))
    axis.set_minor_locator(NullLocator())


def letter(fig, x, y, s):
    W, H = fig.get_size_inches() / MM
    return fig.text(x / W, 1 - y / H, s, fontsize=8, fontweight="bold", ha="left", va="top")


def panel_rims(fig, groups):
    """groups: {panel: [artists]} -> {panel: (x0, y0, x1, y1)} in mm from top-left, labels included."""
    W, H = fig.get_size_inches() / MM
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    sx, sy = fig.bbox.width / W, fig.bbox.height / H
    out = {}
    for name, items in groups.items():
        bb = [it.get_tightbbox(r) for it in items]
        bb = [b for b in bb if b is not None and b.width > 0]
        out[name] = (min(b.x0 for b in bb) / sx, H - max(b.y1 for b in bb) / sy,
                     max(b.x1 for b in bb) / sx, H - min(b.y0 for b in bb) / sy)
    return out


def audit(fig, groups, rows):
    """Print rims and horizontal/vertical gaps. rows: list of lists of panel names, left to right."""
    rims = panel_rims(fig, groups)
    W, H = fig.get_size_inches() / MM
    print(f"figure {W:.1f} x {H:.1f} mm")
    for name, (x0, y0, x1, y1) in rims.items():
        print(f"  {name}: x {x0:6.1f}-{x1:6.1f}  y {y0:6.1f}-{y1:6.1f}")
    for row in rows:
        for a, b in zip(row, row[1:]):
            print(f"  gap {a}->{b}: {rims[b][0] - rims[a][2]:.1f} mm")
    for upper, lower in zip(rows, rows[1:]):
        bottom = max(rims[p][3] for p in upper)
        top = min(rims[p][1] for p in lower)
        print(f"  row gap {upper}->{lower}: {top - bottom:.1f} mm (to letter top: subtract ~0)")
    return rims


def save(fig, stem):
    os.makedirs(OUT, exist_ok=True)
    for ext in ("pdf", "svg"):
        fig.savefig(os.path.join(OUT, f"{stem}.{ext}"))
    fig.savefig(os.path.join(OUT, f"{stem}.png"), dpi=400)


def read_csv(path):
    """Read a CSV with '#' comment lines into a dict of numpy arrays (numeric where possible)."""
    with open(path) as fh:
        lines = [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    head = lines[0].split(",")
    cols = list(zip(*[ln.split(",") for ln in lines[1:]]))
    data = {}
    for h, c in zip(head, cols):
        try:
            data[h] = np.array([float(v) for v in c])
        except ValueError:
            data[h] = np.array(c)
    return data


def deck(name):
    return read_csv(os.path.join(DECK, name))


def sim(name):
    return read_csv(os.path.join(SIM, name))


# ---------------------------------------------------------------- evidence marks
def harvey(ax, x, y, r, level, lw=0.5, color=BLACK, zorder=5):
    """Harvey ball: level 1 = supported (full), 0.5 = partial/correlational (half), 0 = unproven (empty)."""
    ax.add_patch(Circle((x, y), r, fc="white", ec=color, lw=lw, zorder=zorder))
    if level >= 1:
        ax.add_patch(Circle((x, y), r, fc=color, ec=color, lw=lw, zorder=zorder + 1))
    elif level > 0:
        ax.add_patch(Wedge((x, y), r, 90, 270, fc=color, ec=color, lw=0, zorder=zorder + 1))
        ax.add_patch(Circle((x, y), r, fc="none", ec=color, lw=lw, zorder=zorder + 2))


def step_tag(ax, text, level, loc="upper left"):
    """Step tag ('S1') plus Harvey ball inside a data axes, in axes-fraction placement."""
    fig = ax.figure
    bbox = ax.get_position()
    W, H = fig.get_size_inches() / MM
    w_mm, h_mm = bbox.width * W, bbox.height * H
    pad = 1.3
    xa = pad / w_mm if "left" in loc else 1 - (pad + 6.2) / w_mm
    ya = 1 - pad / h_mm if "upper" in loc else (pad + 2.2) / h_mm
    t = ax.text(xa, ya, text, transform=ax.transAxes, ha="left", va="top", fontsize=6, fontweight="bold")
    # ball drawn on a tiny overlay axes so it stays round regardless of data aspect
    bx = bbox.x0 + (xa * w_mm + 4.6) / W
    by = bbox.y0 + (ya * h_mm - 1.05) / H
    r = 0.95
    sub = fig.add_axes([bx - r / W, by - r / H, 2 * r / W, 2 * r / H])
    sub.set_xlim(-r, r)
    sub.set_ylim(-r, r)
    sub.axis("off")
    harvey(sub, 0, 0, r * 0.92, level, lw=0.45)
    return [t, sub]


# ---------------------------------------------------------------- ice schematics
def voronoi_cells(x0, y0, w, h, nx, ny, jitter=0.35, seed=1):
    """Bounded Voronoi grains filling a rectangle (mirror-seed trick). Returns list of (seed, polygon)."""
    rng = np.random.default_rng(seed)
    gx = (np.arange(nx) + 0.5) / nx
    gy = (np.arange(ny) + 0.5) / ny
    pts = np.array([(x, y) for x in gx for y in gy])
    pts += rng.uniform(-jitter, jitter, pts.shape) * np.array([1 / nx, 1 / ny])
    pts = np.clip(pts, 0.02, 0.98)
    pts = pts * [w, h] + [x0, y0]
    mir = [pts]
    mir.append(np.c_[2 * x0 - pts[:, 0], pts[:, 1]])
    mir.append(np.c_[2 * (x0 + w) - pts[:, 0], pts[:, 1]])
    mir.append(np.c_[pts[:, 0], 2 * y0 - pts[:, 1]])
    mir.append(np.c_[pts[:, 0], 2 * (y0 + h) - pts[:, 1]])
    vor = Voronoi(np.vstack(mir))
    cells = []
    for i in range(len(pts)):
        reg = vor.regions[vor.point_region[i]]
        if -1 in reg or not reg:
            continue
        poly = vor.vertices[reg]
        poly[:, 0] = np.clip(poly[:, 0], x0, x0 + w)
        poly[:, 1] = np.clip(poly[:, 1], y0, y0 + h)
        cells.append((pts[i], poly))
    return cells


def interior_vertices(cells, x0, y0, w, h, margin=1.0):
    vs = np.vstack([p for _, p in cells])
    vs = np.unique(np.round(vs, 3), axis=0)
    keep = ((vs[:, 0] > x0 + margin) & (vs[:, 0] < x0 + w - margin) &
            (vs[:, 1] > y0 + margin) & (vs[:, 1] < y0 + h - margin))
    return vs[keep]


def draw_ice(ax, cells, vein_lw=1.6, edge_lw=0.6, zorder=1):
    for _, poly in cells:
        ax.add_patch(Polygon(poly, closed=True, fc=ICE_FILL, ec=VEIN, lw=vein_lw, joinstyle="round",
                             zorder=zorder))
    for _, poly in cells:
        ax.add_patch(Polygon(poly, closed=True, fc="none", ec=BOUNDARY, lw=edge_lw, joinstyle="round",
                             zorder=zorder + 0.1))


def mp(ax, x, y, r, oxidized=False, lw=0.45, zorder=4):
    ax.add_patch(Circle((x, y), r, fc=OX_FILL if oxidized else MP_FILL, ec=MP_EDGE, lw=lw, zorder=zorder))
    if oxidized:
        for a in (25, 140, 250):
            t = np.deg2rad(a)
            ax.plot([x + 0.15 * r * np.cos(t), x + 0.85 * r * np.cos(t + 0.3)],
                    [y + 0.15 * r * np.sin(t), y + 0.85 * r * np.sin(t + 0.3)],
                    color="white", lw=0.4, zorder=zorder + 0.1, solid_capstyle="round")
    else:
        ax.add_patch(Circle((x - 0.35 * r, y + 0.35 * r), 0.25 * r, fc="white", ec="none", alpha=0.8,
                            zorder=zorder + 0.1))


def bubble(ax, x, y, r, lw=0.45, zorder=4.5):
    ax.add_patch(Circle((x, y), r, fc="white", ec=ICE, lw=lw, zorder=zorder))


def ros_dots(ax, xs, ys, s=1.6, zorder=6):
    ax.scatter(xs, ys, s=s, c=ROS, marker="*", linewidths=0, zorder=zorder)


def arrow(ax, p0, p1, color=BLACK, lw=0.6, rad=0.0, head=3.0, zorder=7, ls="-"):
    a = FancyArrowPatch(p0, p1, arrowstyle=f"-|>,head_length={head * 0.12},head_width={head * 0.07}",
                        connectionstyle=f"arc3,rad={rad}", color=color, lw=lw, zorder=zorder,
                        shrinkA=0, shrinkB=0, linestyle=ls, mutation_scale=10)
    ax.add_patch(a)
    return a


def frame(ax, x, y, w, h, lw=0.5, color="#7F7F7F", zorder=8):
    ax.add_patch(Rectangle((x, y), w, h, fc="none", ec=color, lw=lw, zorder=zorder))


def sim_tag(ax, text="Simulated", loc="upper right"):
    y, va = (0.97, "top") if "upper" in loc else (0.04, "bottom")
    return ax.text(0.97, y, text, transform=ax.transAxes, ha="right", va=va, fontsize=5.5,
                   style="italic", color="#555555")


def cross(ax, x, y, s=1.6, color=ROS, lw=0.9, zorder=6):
    """Drawn 'x' mark (avoids fonts without U+2717)."""
    ax.plot([x, x + s], [y, y + s], color=color, lw=lw, solid_capstyle="round", zorder=zorder)
    ax.plot([x, x + s], [y + s, y], color=color, lw=lw, solid_capstyle="round", zorder=zorder)

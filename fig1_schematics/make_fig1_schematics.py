"""make_fig1_schematics.py — the two molecular schematics for Fig. 1 v2.

    python make_fig1_schematics.py                 # everything into out/
    python make_fig1_schematics.py --zoom-seed 7 --film-seed 3   # the defaults

out/fig1a_zoom.*            Fig. 1a zoom (27 x 42 mm, 1 nm = 0.6 mm), labelled
out/fig1a_zoom_art.*        same, no text (for compositing in fig1.py)
out/fig1c_film_states.*     Fig. 1c top strip (98 mm wide, 1 nm = 0.44 mm), labelled
out/fig1c_film_states_art.* same molecules, no text
out/legend.*                colour key (adsorbed / anchored / mobile BSA, PDDA)
out/fig1a_zoom_break.*      zoom with a break in the mobile layer (its thickness is set by V_C)
out/sheet.pdf/.png          review sheet: both schematics + the PDDA numbers
out/stats.json              what was drawn (counts, contour per BSA, chain orientation)

Built 1:1 at final size (Nature preset: Arial/Liberation Sans, 5-7 pt).
To use inside fig1.py, import scenes / pdda_glue and call draw_zoom() or
draw_strip() on your own figure (mm positions).
"""
import argparse, json, os
import numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon as MPoly, Circle, FancyBboxPatch, PathPatch
from matplotlib.path import Path
import coac_glyphs as G
import pdda_glue as PG
import scenes as SC
import pdda_capacity as CAP

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
MM = G.MM
P = G.PALETTE
INK = "#222222"
WATER = "#3F6E99"          # dilute-phase / water text and arrows
OIL_TXT = P["oil_text"]
PART = "#8A3B6E"           # partitioning arrow (Fig. 1 v2 draft)


# ----------------------------------------------------------------- helpers
def save(fig, stem, dpi=600, svg=True):
    os.makedirs(os.path.dirname(stem), exist_ok=True)
    fig.savefig(stem + ".pdf"); fig.savefig(stem + ".png", dpi=dpi)
    if svg:
        fig.savefig(stem + ".svg")
    plt.close(fig)

def overlay(fig):
    """Axes over the whole figure in mm, origin top-left, y down."""
    W, H = fig.get_size_inches() / MM
    ax = fig.add_axes([0, 0, 1, 1], zorder=50)
    ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")
    ax.patch.set_alpha(0)
    return ax

def ax_nm(fig, x, y, w, h, window):
    """Axes at x, y (mm from top-left), w x h mm, showing `window` (nm)."""
    W, H = fig.get_size_inches() / MM
    ax = fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])
    x0, y0, x1, y1 = window
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal"); ax.axis("off")
    return ax

def nm2mm(ax_box, window, z):
    """nm point in a window drawn at ax_box=(x, y, w, h) mm -> figure mm (y down)."""
    x, y, w, h = ax_box; x0, y0, x1, y1 = window
    return x + (z.real - x0) / (x1 - x0) * w, y + (y1 - z.imag) / (y1 - y0) * h

def circ_num(ax, x, y, n, r=1.15, fs=6.5):
    ax.add_patch(Circle((x, y), r, fc="white", ec=INK, lw=0.5, zorder=60))
    ax.text(x, y + 0.05, str(n), ha="center", va="center", fontsize=fs, color=INK, zorder=61)

def arrow(ax, p, q, lw=0.6, color=INK, head=3.0, style="-|>", z=60):
    ax.annotate("", xy=q, xytext=p, zorder=z,
                arrowprops=dict(arrowstyle=style, lw=lw, color=color, shrinkA=0, shrinkB=0,
                                mutation_scale=head))

def tag(ax, x, y, s, fs=6.0, color=INK, ha="left", va="center", pad=0.35, alpha=0.88, **kw):
    t = ax.text(x, y, s, fontsize=fs, color=color, ha=ha, va=va, zorder=70, **kw)
    t.set_bbox(dict(boxstyle=f"round,pad={pad},rounding_size=0.6", fc="white", ec="none", alpha=alpha))
    return t

def _vec(f, xs):
    return np.broadcast_to(np.asarray(f(xs), float), np.shape(xs)).copy()


# ----------------------------------------------------------------- film window
def draw_film(ax, S, hf, rng, bg=None):
    x0, y0, x1, y1 = S.window
    xs = np.linspace(x0 - 2, x1 + 2, 500); hx = _vec(hf, xs)
    ax.add_patch(Rectangle((x0 - 2, y0 - 2), x1 - x0 + 4, y1 - y0 + 4, fc=P["oil"], ec="none", zorder=0))
    ax.add_patch(MPoly(list(zip(xs, -hx / 2)) + list(zip(xs[::-1], hx[::-1] / 2)), closed=True,
                       fc=bg or P["coac_bg"], ec="none", zorder=0.5))
    for sgn in (-1, 1):
        ax.plot(xs, sgn * hx / 2, color=P["oil_line"], lw=0.4, zorder=0.6, solid_capstyle="butt")
    clip = Rectangle((x0, y0), x1 - x0, y1 - y0, transform=ax.transData, fc="none", ec="none")
    ax.add_patch(clip)
    PG.draw_scene(ax, S, rng, clip=clip)
    for a in ax.lines + ax.patches:
        a.set_clip_path(clip)


# ----------------------------------------------------------------- zoom (Fig. 1a)
def draw_zoom(fig, F, x, y, scene, labels=True, mmpn=0.6, break_y=None, rng=None):
    """Zoom window at (x, y) mm. scene = SC.zoom_scene(...)[0]."""
    S = scene; rng = rng or np.random.default_rng(1)
    w, h, yo, yi = SC.ZOOM["w"], SC.ZOOM["h"], SC.ZOOM["y_oil"], SC.ZOOM["y_int"]
    box_mm = (x, y, w * mmpn, h * mmpn)
    ax = ax_nm(fig, *box_mm, S.window)
    ax.add_patch(Rectangle((-1, -1), w + 2, yo + 1, fc=P["oil"], ec="none", zorder=0))
    ax.add_patch(Rectangle((-1, yo), w + 2, yi - yo, fc=P["coac_bg"], ec="none", zorder=0))
    ax.add_patch(Rectangle((-1, yi), w + 2, h - yi + 1, fc=P["dilute_bg"], ec="none", zorder=0))
    ax.plot([-1, w + 1], [yo, yo], color=P["oil_line"], lw=0.4, zorder=0.6)
    ax.plot([-1, w + 1], [yi, yi], color=P["coac"], lw=0.5, zorder=0.6)
    clip = Rectangle((0, 0), w, h, transform=ax.transData, fc="none", ec="none")
    ax.add_patch(clip)
    PG.draw_scene(ax, S, rng, clip=clip)
    if break_y is not None:          # mobile layer truncated: its thickness is set by V_C
        xx = np.linspace(-1, w + 1, 200)
        wave = 0.55 * np.sin(2 * np.pi * xx / 9.0)
        band = MPoly(list(zip(xx, break_y - 1.0 + wave)) + list(zip(xx[::-1], break_y + 1.0 + wave[::-1])),
                     closed=True, fc="white", ec="none", zorder=20)
        ax.add_patch(band)
        for d in (-1.0, 1.0):
            ax.plot(xx, break_y + d + wave, color=INK, lw=0.4, zorder=21)
    for a in ax.lines + ax.patches:
        a.set_clip_path(clip)
    ax.add_patch(Rectangle((0, 0), w, h, fc="none", ec=INK, lw=0.6, zorder=40, clip_on=False))
    if not labels:
        return ax, box_mm
    o = overlay(fig)
    X0, Y0, Wm, Hm = box_mm
    yy = lambda ynm: Y0 + (h - ynm) * mmpn
    o.text(X0 + 1.0, yy((yi + h) / 2), "dilute phase d (water)", fontsize=6, color=WATER,
           va="center", ha="left", zorder=70)
    o.text(X0 + Wm - 0.6, yy(yi) - 0.25, r"$\sigma_{\rm dc}$", fontsize=6, color=INK,
           ha="right", va="bottom", zorder=70)
    tag(o, X0 + 1.0, yy(yi) + 1.2, "mobile coacervate\nliquid (Fig. 3)", fs=6, va="top",
        linespacing=1.15)
    top_anc = yo + 10.0
    tag(o, X0 + 1.0, yy(top_anc) - 2.0, r"anchored layer, $\approx h_{\rm b}/2$", fs=6)
    o.text(X0 + 1.0, yy(yo) + 2.2, "oil o", fontsize=6, color=OIL_TXT, style="italic",
           ha="left", va="center", zorder=70)
    o.text(X0 + Wm - 0.6, yy(yo) + 0.35, r"$\sigma_{\rm oc}$", fontsize=6, color=INK,
           ha="right", va="top", zorder=70)
    # anchored-layer bracket on the right edge
    bx = X0 + Wm - 0.9
    o.plot([bx, bx + 0.0], [yy(yo), yy(top_anc)], color=INK, lw=0.5, zorder=70)
    for yb in (yy(yo), yy(top_anc)):
        o.plot([bx - 0.6, bx], [yb, yb], color=INK, lw=0.5, zorder=70)
    # partitioning path (as in the draft): dashed arrow from the dilute phase into the oil
    px = X0 + Wm - 3.9
    o.plot([px, px], [yy(h - 1.0), yy(yo - 6.5)], color=PART, lw=0.6, ls=(0, (2.2, 1.4)), zorder=69)
    arrow(o, (px, yy(yo - 6.0)), (px, yy(yo - 7.6)), lw=0.6, color=PART, head=3.5)
    o.text(X0 + Wm / 2, yy(yo - 11.0), "solutes reach oil by\npartitioning (Fig. 6)", fontsize=6,
           color=PART, ha="center", va="center", zorder=70, linespacing=1.15)
    return ax, box_mm


# ----------------------------------------------------------------- strip (Fig. 1c)
STRIP = dict(win_w=21.5, gutter=2.5, left=2.6, top=4.4, right=6.0, foot=9.2, legend=4.6)

def strip_size(legend=True):
    s = STRIP
    W = s["left"] + 4 * s["win_w"] + 3 * s["gutter"] + s["right"]
    win_h = s["win_w"] * SC.FILM["h"] / SC.FILM["w"]
    H = s["top"] + win_h + s["foot"] + (s["legend"] if legend else 0.0)
    return W, H, win_h

def draw_strip(fig, F, x=0.0, y=0.0, labels=True, legend=True, rng_seed=3):
    """Film states left to right in order of h, as on the Π(h) axis below:
    (3) compressed, (2) h = hb, stepwise thinning, (1) rest. Same scale in all."""
    s = STRIP
    W, H, win_h = strip_size(legend)
    mmpn = s["win_w"] / SC.FILM["w"]
    order = ["comp", "hb", "step", "rest"]
    boxes = {}
    o = overlay(fig) if labels else None
    for n, k in enumerate(order):
        S, hf, st = F[k]
        bx = (x + s["left"] + n * (s["win_w"] + s["gutter"]), y + s["top"], s["win_w"], win_h)
        boxes[k] = bx
        ax = ax_nm(fig, *bx, S.window)
        draw_film(ax, S, hf, np.random.default_rng(rng_seed + n),
                  bg="#BFE3D2" if k == "comp" else None)       # less water at 0.86 MPa
    if not labels:
        return boxes, mmpn
    head = {"comp": (3, "compressed"), "hb": (2, "core expelled"),
            "step": (None, "stepwise thinning"), "rest": (1, "rest")}
    foot = {"comp": (r"$h$ = 13 nm (0.65 $h_{\rm b}$)", r"$\Pi$ = 0.86 MPa", "water, ions leave"),
            "hb": (r"$h$ = $h_{\rm b}$ = 20 nm", r"$\Pi$ ≈ 10 kPa", "core → Plateau borders"),
            "step": (r"$h_{\rm b}$ + $d$  |  $h_{\rm b}$ + 2$d$", "one layer out per step"),
            "rest": (r"$h$ = $h_{\rm b}$ + 4$d$ = 51 nm", r"$\Pi$ ≈ 8–43 Pa", "core = bulk coacervate")}
    for k in order:
        X, Y, Wb, Hb = boxes[k]
        n, t = head[k]
        if n is not None:
            circ_num(o, X + 1.15, Y - 2.0, n)
            o.text(X + 2.65, Y - 1.95, t, fontsize=6.5, fontweight="bold", va="center", ha="left",
                   color=INK)
        else:
            o.text(X, Y - 1.95, t, fontsize=6.5, fontweight="bold", va="center", ha="left", color=INK)
        for q, line in enumerate(foot[k]):
            o.text(X, Y + Hb + 1.0 + 2.45 * q, line, fontsize=6, va="top", ha="left",
                   color=WATER if q == 2 else INK)
    # film thickness: dimension arrows in the gutter left of (3), (2), (1)
    for k in ("comp", "hb", "rest"):
        S, hf, st = F[k]
        X, Y, Wb, Hb = boxes[k]
        hk = float(_vec(hf, np.array([0.0]))[0])
        yc = Y + Hb / 2; half = hk / 2 * mmpn
        gx = X - 1.25
        arrow(o, (gx, yc), (gx, yc - half), lw=0.45, head=2.4)
        arrow(o, (gx, yc), (gx, yc + half), lw=0.45, head=2.4)
    # applied pressure: arrows in the oil, weight ~ log Pi
    for k, lw, L in (("step", 0.5, 2.2), ("hb", 0.8, 3.0), ("comp", 1.3, 4.2)):
        S, hf, st = F[k]
        X, Y, Wb, Hb = boxes[k]
        for fx in (0.18, 0.82):
            xm = X + fx * Wb
            hk = float(_vec(hf, np.array([S.window[0] + fx * (S.window[2] - S.window[0])]))[0])
            ytop = Y + Hb / 2 - hk / 2 * mmpn; ybot = Y + Hb / 2 + hk / 2 * mmpn
            gap = 0.8
            arrow(o, (xm, ytop - gap - L), (xm, ytop - gap), lw=lw, head=2.2 + 2 * lw)
            arrow(o, (xm, ybot + gap + L), (xm, ybot + gap), lw=lw, head=2.2 + 2 * lw)
    # stepwise thinning: the front moves toward the thick side; the extra layer leaves
    S, hf, st = F["step"]
    X, Y, Wb, Hb = boxes["step"]
    xf = st["x_front"]
    p = nm2mm(boxes["step"], S.window, complex(xf - 4.5, 0.0))
    q = nm2mm(boxes["step"], S.window, complex(xf + 4.0, 0.0))
    o.annotate("", xy=q, xytext=p, zorder=65,
               arrowprops=dict(arrowstyle="-|>", lw=0.9, color="white", mutation_scale=4.5,
                               shrinkA=0, shrinkB=0))
    arrow(o, p, q, lw=0.6, head=3.5, z=66)
    # rest: what the thickness is made of
    S, hf, st = F["rest"]
    X, Y, Wb, Hb = boxes["rest"]
    bx = X + Wb + 0.9
    hR = SC.H_REST
    marks = [-hR / 2, -hR / 2 + SC.HB / 2, hR / 2 - SC.HB / 2, hR / 2]
    ym = [Y + Hb / 2 - v * mmpn for v in marks]
    for a, b, lab in ((ym[0], ym[1], r"$h_{\rm b}$/2"), (ym[1], ym[2], r"4$d$"),
                      (ym[2], ym[3], r"$h_{\rm b}$/2")):
        o.plot([bx, bx], [a - 0.15, b + 0.15], color=INK, lw=0.45)
        for yb in (a - 0.15, b + 0.15):
            o.plot([bx - 0.45, bx], [yb, yb], color=INK, lw=0.45)
        o.text(bx + 0.5, (a + b) / 2, lab, fontsize=5.5, va="center", ha="left", color=INK)
    # oil label and scale bar (all windows share the scale)
    X, Y, Wb, Hb = boxes["comp"]
    o.text(X + 0.9, Y + 1.5, "oil", fontsize=6, style="italic", color=OIL_TXT, va="center")
    L10 = 10 * mmpn
    xb = X + Wb / 2
    o.plot([xb - L10 / 2, xb + L10 / 2], [Y + 3.4] * 2, color=INK, lw=1.0,
           solid_capstyle="butt", zorder=60)
    o.text(xb, Y + 2.8, "10 nm", fontsize=6, ha="center", va="bottom", color=INK, zorder=60)
    o.text(X + Wb / 2, Y + Hb - 2.4, "BSA, PDDA stay", fontsize=6, color=INK,
           va="center", ha="center")
    if legend:
        draw_legend(fig, o, x + s["left"], y + H - s["legend"] + 2.3)
    return boxes, mmpn


# ----------------------------------------------------------------- legend
def draw_legend(fig, o, x, y, mmpn=0.44):
    """One row: adsorbed / anchored / mobile BSA, PDDA. (x, y) = left, centre line, mm."""
    items = [("ads", "BSA adsorbed at oil"), ("anc", "BSA anchored (glued)"),
             ("mob", "BSA mobile"), ("pdda", "PDDA")]
    W, H = fig.get_size_inches() / MM
    cx = x
    for kind, lab in items:
        gw = 4.2 if kind == "pdda" else 3.6
        a = ax_nm(fig, cx, y - 1.6, gw, 3.2, (-gw / 2 / mmpn, -1.6 / mmpn, gw / 2 / mmpn, 1.6 / mmpn))
        if kind == "pdda":
            t = np.linspace(-4.2, 4.2, 80)
            z = t + 1j * 0.9 * np.sin(t * 0.9)
            G.draw_pdda(a, z, width=0.8, casing_pt=0.28)
        else:
            sq = {"ads": 0.56, "anc": 0.9, "mob": 0.95}[kind]
            pr = PG.make_bsa((0, 0), 0, False, sq, kind)
            G.draw_bsa_geom(a, pr.out, pr.seams, style=kind)
        o.text(cx + gw + 0.6, y, lab, fontsize=6, va="center", ha="left", color=INK)
        cx += gw + 0.6 + len(lab) * 1.02 + 2.2


# ----------------------------------------------------------------- review sheet
def make_sheet(Sz, stz, F, stem):
    """Both schematics at final size plus the numbers behind them (183 mm wide)."""
    r = CAP.calc(); f = CAP.fmt
    W, H = 183.0, 108.0
    fig = plt.figure(figsize=(W * MM, H * MM))
    o = overlay(fig)
    o.text(3, 3.5, "Fig. 1 molecular schematics: a, corona zoom; c, film states (Π(h) order)",
           fontsize=8, fontweight="bold", va="center")
    o.text(3, 7.2, "Built 1:1. Zoom 1 nm = 0.6 mm; film states 1 nm = 0.44 mm (all four windows). "
           "BSA 8 nm wide; PDDA tube 0.8 nm. Green shade = mobility.", fontsize=6, va="center",
           color="#555555")
    o.text(3, 12.2, "a", fontsize=8, fontweight="bold", va="center")
    draw_zoom(fig, None, 6.0, 12.0, Sz, labels=True, break_y=44.0)
    sw, sh, _ = strip_size(True)
    o.text(39, 12.2, "c", fontsize=8, fontweight="bold", va="center")
    draw_strip(fig, F, x=40.0, y=10.0, labels=True, legend=True)
    y0 = 63.0
    left = [
        ("PDDA, Mw 1.0–1.5 MDa: how many BSA one chain glues", True),
        (f"Repeat unit 161.7 g/mol, 0.50 nm, +1 → {f(r['charges_per_chain'])} charges; "
         f"contour {f(r['contour_um'], 1)} µm", False),
        (f"Coil (lp = 3 nm, ideal in the dense phase): Rg = {f(r['Rg_nm'])} nm", False),
        (f"Charge-matched (BSA net −13 to −18): {f(r['BSA_per_chain_charge_matched'])} BSA per chain "
         f"(≈ {r['BSA_per_chain_central']:.0f} at 1.25 MDa)", False),
        (f"= {f(r['contour_per_BSA_nm'], 1)} nm PDDA per BSA ≈ one BSA diameter: each glued BSA is wrapped",
         False),
        (f"Implied PDDA {f(r['c_PDDA_mg_per_mL_if_matched'], 0)} mg/mL; mesh "
         f"{f(r['mesh_nm'], 1)} nm (SANS ξ ≈ 9, d = 7.7 nm)", False),
        (f"Bulk: one coil volume holds {f(r['BSA_in_coil_volume'])} BSA → "
         f"{f(r['chains_sharing_a_coil_volume'], 0)} chains interpenetrate", False),
        ("The four tight layers at hb = 20 nm", True),
        (f"7.7-nm pitch → {r['Gamma_per_layer_mg_m2']:.1f} mg/m² per layer (≈ a protein monolayer); "
         f"{r['layer_pitch_at_hb_nm']:.0f} nm per layer", False),
        (f"One chain neutralises all 4 layers over {f(r['chain_footprint_diameter_nm'])} nm "
         f"≈ its coil width ({f(r['coil_lateral_diameter_nm'])} nm)", False),
        (f"It crosses the 20-nm film ~{f(r['film_crossings_per_chain'])} times: "
         "the anchored layers are stitched into one sheet", False),
        (f"Dry {f(r['dry_thickness_4_layers_nm'], 1)} nm; φdry {r['phi_dry_bulk']:.2f} (bulk) → "
         f"{f(r['phi_dry_at_hb'], 2)} (hb) → {f(r['phi_dry_at_0.86MPa'], 2)} (0.86 MPa)", False),
        ("→ below hb only water and ions can leave: the film densifies", False),
    ]
    zs = stz; fr = F["rest"][2]; fb = F["hb"][2]
    right = [
        ("Drawing rules", True),
        ("PDDA routed BSA to BSA: wraps each one it glues, then a tangent", False),
        ("  bridge that threads between two BSA or spans the gap (lp ≈ 3 nm)", False),
        ("No direction bias in the routing → isotropic where BSA are random", False),
        ("No chain ends in view: they leave at a window edge or go under a BSA", False),
        ("Adsorbed row flattened on the oil; glued row in its hollows, +1.1 nm", False),
        ("Same anchored molecules in every state; (3) = (2) squeezed to 0.65", False),
        ("What was drawn", True),
        (f"PDDA per BSA in view: {zs['contour_per_bsa']:.1f} nm (zoom), {fr['contour_per_bsa']:.1f} (rest), "
         f"{fb['contour_per_bsa']:.1f} (hb)", False),
        (f"Order S = <cos 2θ>: mobile {zs['order_mobile']['S']:+.2f} (zoom), "
         f"{fr['order_core']['S']:+.2f} (rest) → isotropic", False),
        (f"  anchored {zs['order_anchored']['S']:+.2f}, film at hb {fb['order']['S']:+.2f} "
         "→ parallel to the oil (confined)", False),
        (f"Mobile BSA area fraction {zs['phi_mobile']:.2f} (zoom), {fr['phi_core']:.2f} (rest); "
         "φeff 0.41–0.47", False),
        (f"{fb['midplane_crossings']} PDDA crossings of the midplane at hb (49-nm window)", False),
    ]
    for col, x in ((left, 3.0), (right, 106.0)):
        y = y0
        for t, b in col:
            if b:
                y += 1.2
            o.text(x, y, t, fontsize=7 if b else 6, fontweight="bold" if b else "normal",
                   va="top", ha="left", color=INK)
            y += 3.3 if b else 2.75
    save(fig, stem, dpi=400, svg=False)


# ----------------------------------------------------------------- outputs
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zoom-seed", type=int, default=7)
    ap.add_argument("--film-seed", type=int, default=3)
    a = ap.parse_args()
    G.rc()
    os.makedirs(OUT, exist_ok=True)

    Sz, stz = SC.zoom_scene(a.zoom_seed)
    F = SC.film_scenes(a.film_seed)

    # Fig. 1a zoom
    zw, zh = SC.ZOOM["w"] * 0.6, SC.ZOOM["h"] * 0.6
    for lab, stem in ((True, "fig1a_zoom"), (False, "fig1a_zoom_art")):
        fig = plt.figure(figsize=((zw + 1) * MM, (zh + 1) * MM))
        draw_zoom(fig, None, 0.5, 0.5, Sz, labels=lab)
        save(fig, os.path.join(OUT, stem))
    fig = plt.figure(figsize=((zw + 1) * MM, (zh + 1) * MM))
    draw_zoom(fig, None, 0.5, 0.5, Sz, labels=True, break_y=44.0)
    save(fig, os.path.join(OUT, "fig1a_zoom_break"))

    # Fig. 1c strip
    W, H, win_h = strip_size(True)
    for lab, stem in ((True, "fig1c_film_states"), (False, "fig1c_film_states_art")):
        fig = plt.figure(figsize=(W * MM, (H if lab else H - STRIP["legend"]) * MM))
        draw_strip(fig, F, labels=lab, legend=lab)
        save(fig, os.path.join(OUT, stem))

    # legend alone
    fig = plt.figure(figsize=(98 * MM, 4.0 * MM))
    draw_legend(fig, overlay(fig), 1.0, 2.0)
    save(fig, os.path.join(OUT, "legend"))

    make_sheet(Sz, stz, F, os.path.join(OUT, "sheet"))

    stats = dict(zoom=stz, films={k: v[2] for k, v in F.items()},
                 capacity=CAP.calc())
    def clean(o):
        if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)): return [clean(v) for v in o]
        if isinstance(o, (np.floating, float)): return round(float(o), 3)
        if isinstance(o, (np.integer,)): return int(o)
        return o
    with open(os.path.join(OUT, "stats.json"), "w") as f:
        json.dump(clean(stats), f, indent=1)
    print(json.dumps(clean(dict(zoom=stz, films={k: v[2] for k, v in F.items()})), indent=1))


if __name__ == "__main__":
    main()

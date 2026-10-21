"""coac_glyphs.py — molecular glyphs for the coacervate interior (BSA, PDDA).

Import into any figure script (fig1.py, fig2.py, ...) or run make_glyphs.py.
Everything is drawn in *nanometre* data coordinates on an equal-aspect axes;
stroke widths are converted to points with pt_per_unit(ax), so a glyph keeps
its look at any print scale.

Colour tokens: see PALETTE. v2 (Fig. 1 schematics): BSA is green in three
shades that encode mobility, taken from the Fig. 1 v2 draft (light #7DCBAA
mobile, mid #2E9E76 anchored second row, dark #0B5E44 adsorbed at the oil);
PDDA is neutral grey. Phase tints (coacervate #D2EDE1, oil #F5D2E5,
dilute #EEF5FB) are sampled from the Fig. 1 v2 draft.
"""
import numpy as np
import matplotlib as mpl
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Circle

MM = 1 / 25.4
PT_PER_MM = 72 / 25.4


# ----------------------------------------------------------------- colours
def _mix(c, other, f):
    c = np.array(mpl.colors.to_rgb(c)); o = np.array(mpl.colors.to_rgb(other))
    return mpl.colors.to_hex(c * (1 - f) + o * f)

def tint(c, f):   # f = fraction of colour kept, rest white
    return _mix(c, "white", 1 - f)

def shade(c, f):  # f = fraction of black mixed in
    return _mix(c, "black", f)

BSA = "#2E9E76"      # Fig. 1 v2 draft, anchored-row green
PDDA = "#A6A6A6"     # neutral grey: PDDA has no sample colour; grey keeps green = BSA
COAC = "#00896A"     # Fig. 5 i-k (PDDA/BSA)

PALETTE = {
    # BSA, mobile (bulk, mobile core): light fill, dark outline, seams mid green
    "bsa": "#3E9C78", "bsa_fill": "#A3DAC0", "bsa_line": "#1D6B50",
    # BSA, anchored second row (glued onto the adsorbed row by PDDA)
    "bsa_anc": "#14614A", "bsa_anc_fill": BSA, "bsa_anc_line": "#0B4A36",
    # BSA, adsorbed at the oil (flattened, partly unfolded): darkest
    "bsa_ads": "#3C8A6E", "bsa_ads_fill": "#0B5E44", "bsa_ads_line": "#05301F",
    # PDDA: grey tube, darker casing
    "pdda": PDDA, "pdda_line": "#555555",
    # phases (Fig. 1 v2 draft tints)
    "coac": COAC, "coac_bg": "#D2EDE1",
    "dilute_bg": "#EEF5FB",
    "oil": "#F5D2E5", "oil_text": "#C46A9C", "oil_line": "#D9A3C1",
    # neutral variant = Fig. 2e structure-icon look (image 1)
    "grey_fill": "#E4E4E4", "grey_line": "#666666", "grey_seam": "#8C8C8C",
    "badge_bg": "#FFFFFF",
}


# ----------------------------------------------------------------- helpers
def pt_per_unit(ax):
    """Points per data unit (nm) for an equal-aspect axes whose limits are set."""
    fig = ax.figure
    w_in = ax.get_position().width * fig.get_figwidth()
    x0, x1 = ax.get_xlim()
    return w_in * 72 / abs(x1 - x0)

def _c2xy(z):
    z = np.asarray(z); return np.c_[z.real, z.imag]

def _resample(z, n, closed=False):
    zz = np.r_[z, z[:1]] if closed else z
    d = np.r_[0, np.cumsum(np.abs(np.diff(zz)))]
    s = np.linspace(0, d[-1], n, endpoint=not closed)
    return np.interp(s, d, zz.real) + 1j * np.interp(s, d, zz.imag)

def catmull_rom_path(z, closed=False):
    """Uniform Catmull-Rom spline through points z -> cubic-Bezier Path.
    Gives clean, editable SVG/PDF curves (few nodes) instead of polylines."""
    z = np.asarray(z, complex); n = len(z)
    if closed:
        P = lambda i: z[i % n]
        segs = range(n)
    else:
        ext = np.r_[2 * z[0] - z[1], z, 2 * z[-1] - z[-2]]
        P = lambda i: ext[i + 1]
        segs = range(n - 1)
    verts = [P(0)]; codes = [Path.MOVETO]
    for i in segs:
        p0, p1, p2, p3 = P(i - 1), P(i), P(i + 1), P(i + 2)
        verts += [p1 + (p2 - p0) / 6, p2 - (p3 - p1) / 6, p2]
        codes += [Path.CURVE4] * 3
    if closed:
        verts.append(verts[0]); codes.append(Path.CLOSEPOLY)
    return Path(_c2xy(verts), codes)

def _xf(z, xy, size, angle, mirror, squash):
    """Local normalized coords -> data coords. squash < 1 foreshortens the
    glyph along its local y (a tilted view of the same molecule)."""
    z = np.asarray(z, complex)
    if mirror: z = -z.conj()
    z = z.real + 1j * z.imag * squash
    return complex(*xy) + size * z * np.exp(1j * np.radians(angle))


# ----------------------------------------------------------------- BSA
# Outline traced from the Fig. 2e BSA icon (image 1), Fourier-smoothed
# (|k| <= 7), centred, max extent = 1, counter-clockwise. Coefficients k=-7..7.
_BSA_COEF = np.array([
    -0.00184-0.00279j, +0.00020-0.00142j, +0.00205+0.00285j, -0.00464-0.01312j,
    -0.00077-0.00034j, +0.00894+0.03321j, +0.00758+0.03030j, +0.00000+0.00000j,
    +0.17503-0.39705j, +0.00080+0.00174j, -0.00544-0.00057j, -0.01586+0.00833j,
    +0.00067+0.00045j, +0.01038-0.00365j, -0.00154+0.00037j])
_K = np.arange(-7, 8)

# Surface-contour seams: each is the boundary of a front lobe continued from a
# concave notch of the outline into the interior (as in image 2, no helix).
# (start point on the notch, arc centre, radius, start angle deg, sweep deg)
_BSA_SEAMS = [
    (0.3047+0.1995j, 0.0459+0.2199j, 0.2595, -4.50, -79.5),   # top lobe over right lobe
    (-0.3940+0.0406j, -0.3176-0.1441j, 0.1998, 112.47, -86.0), # lower-left lobe over top lobe
    (-0.1074-0.3536j, -0.2472-0.0072j, 0.3735, -68.01, 39.9),  # lower-left lobe over bottom lobe
]

def bsa_outline(n=400):
    t = np.linspace(0, 1, n, endpoint=False)
    return (_BSA_COEF[None, :] * np.exp(2j * np.pi * _K[None, :] * t[:, None])).sum(1)

def _seam_points(seam, n=60):
    P, c, r, a0, sw = seam
    ph = np.radians(a0) + np.radians(sw) * np.linspace(0, 1, n)
    return c + r * np.exp(1j * ph)

def _taper(z, w0, w1, p=1.3):
    """Filled polygon along polyline z, width w0 -> w1 (data units), round start."""
    d = np.gradient(z); t = d / np.abs(d); nrm = 1j * t
    u = np.linspace(0, 1, len(z)); w = (w0 + (w1 - w0) * u ** p) / 2
    left, right = z + nrm * w, z - nrm * w
    cap0 = z[0] + (w[0]) * np.exp(1j * (np.angle(nrm[0]) + np.linspace(0, np.pi, 9)))
    cap1 = z[-1] + max(w[-1], 1e-9) * np.exp(1j * (np.angle(-nrm[-1]) + np.linspace(0, np.pi, 7)))
    return np.r_[left, cap1, right[::-1], cap0]

def bsa_geometry(xy=(0, 0), size=8.0, angle=0.0, mirror=False, squash=1.0):
    """Return transformed outline (complex) and seam centre-lines."""
    out = _xf(bsa_outline(), xy, size, angle, mirror, squash)
    seams = [_xf(_seam_points(s), xy, size, angle, mirror, squash) for s in _BSA_SEAMS]
    return out, seams

def bsa_path(xy=(0, 0), size=8.0, angle=0.0, mirror=False, squash=1.0):
    out, _ = bsa_geometry(xy, size, angle, mirror, squash)
    return catmull_rom_path(_resample(out, 36, closed=True), closed=True)

def draw_bsa(ax, xy=(0, 0), size=8.0, angle=0.0, mirror=False, squash=1.0,
             style="color", outline_pt=None, seams=True, charges=(), badge=None,
             zorder=3, ppu=None, gid=None):
    """Draw one BSA glyph.
    size     : max extent in data units (nm). 8 nm ~ crystal-structure width;
               the glyph area then equals a 6.9-nm disc (BSA d_H ≈ 7 nm).
    style    : 'color'/'mob', 'anc', 'ads' (see bsa_colors) or 'grey' (Fig. 2e icon look).
    charges  : outline positions (0-1 along the contour) for '-' badges.
    """
    out, sl = bsa_geometry(xy, size, angle, mirror, squash)
    path, arts = draw_bsa_geom(ax, out, sl if seams else (), style=style, size=size,
                               outline_pt=outline_pt, zorder=zorder, ppu=ppu)
    ppu = ppu or pt_per_unit(ax)
    line = bsa_colors(style)[1]
    if outline_pt is None:
        outline_pt = float(np.clip(0.5 * (size * ppu / (8 * PT_PER_MM)), 0.3, 0.9))
    if charges:
        b = badge or {}
        for u in charges:
            i = int(u * len(out)) % len(out)
            arts += draw_badge(ax, out[i], "-", r=b.get("r", 0.11 * size), color=line,
                               lw_pt=b.get("lw_pt", outline_pt), zorder=zorder + 0.03, ppu=ppu)
    if gid:
        for q, a in enumerate(arts): a.set_gid(f"{gid}_{q}")
    return path, arts

def bsa_colors(style):
    """(fill, outline, seam) for a BSA style: 'color'/'mob' (mobile, light),
    'anc' (anchored second row, mid), 'ads' (adsorbed at the oil, dark), 'grey'."""
    if style == "grey":
        return PALETTE["grey_fill"], PALETTE["grey_line"], PALETTE["grey_seam"]
    k = {"color": "bsa", "mob": "bsa", "anc": "bsa_anc", "ads": "bsa_ads"}[style]
    return PALETTE[k + "_fill"], PALETTE[k + "_line"], PALETTE[k]

def draw_bsa_geom(ax, out, seam_lines=(), style="mob", size=8.0, outline_pt=None,
                  zorder=3, ppu=None, nodes=40, gid=None):
    """Draw a BSA glyph from a precomputed outline (complex, nm) and seam
    centre-lines, e.g. after flattening against the oil or a film compression."""
    ppu = ppu or pt_per_unit(ax)
    if outline_pt is None:
        outline_pt = 0.5 * (size * ppu / (8 * PT_PER_MM))  # 0.5 pt at 8 mm
        outline_pt = float(np.clip(outline_pt, 0.3, 0.9))
    fill, line, seam_c = bsa_colors(style)
    path = catmull_rom_path(_resample(np.asarray(out), nodes, closed=True), closed=True)
    sl = seam_lines
    seams = len(sl) > 0
    arts = []
    body = PathPatch(path, facecolor=fill, edgecolor="none", lw=0, zorder=zorder)
    ax.add_patch(body); arts.append(body)
    if seams:
        w0 = 0.80 * outline_pt / ppu; w1 = 0.12 * outline_pt / ppu
        for s in sl:
            pg = _taper(s, w0, w1)
            p = PathPatch(Path(_c2xy(pg)), facecolor=seam_c, edgecolor="none", lw=0,
                          zorder=zorder + 0.01)
            ax.add_patch(p); arts.append(p)   # start cap lies inside the outline stroke
    edge = PathPatch(path, facecolor="none", edgecolor=line, lw=outline_pt,
                     joinstyle="round", zorder=zorder + 0.02)
    ax.add_patch(edge); arts.append(edge)
    if gid:
        for q, a in enumerate(arts): a.set_gid(f"{gid}_{q}")
    return path, arts

def draw_badge(ax, xy, sign, r=0.9, color="k", lw_pt=0.5, zorder=5, ppu=None, fill=None):
    """Circled + or - drawn as vector strokes (no font dependence)."""
    ppu = ppu or pt_per_unit(ax)
    z = complex(*xy) if not isinstance(xy, complex) else xy
    c = Circle((z.real, z.imag), r, facecolor=fill or PALETTE["badge_bg"], edgecolor=color,
               lw=lw_pt, zorder=zorder)
    ax.add_patch(c)
    a = 0.52 * r
    lines = [ax.plot([z.real - a, z.real + a], [z.imag, z.imag], color=color, lw=1.15 * lw_pt,
                     solid_capstyle="butt", zorder=zorder + 0.01)[0]]
    if sign == "+":
        lines.append(ax.plot([z.real, z.real], [z.imag - a, z.imag + a], color=color,
                             lw=1.15 * lw_pt, solid_capstyle="butt", zorder=zorder + 0.01)[0])
    return [c] + lines


# ----------------------------------------------------------------- PDDA
def wlc(rng, start=(0, 0), heading=0.0, length=40.0, lp=3.0, ds=0.1, smooth=1.0,
        steer=None):
    """2D worm-like-chain centre-line (data units = nm).
    lp      : persistence length; tangent correlation <cos dtheta(s)> = exp(-s/(2 lp))
              (a 3D chain of persistence length lp seen in projection looks
              similar). PDDA: ~3 nm intrinsic; 'relatively flexible' next to an
              8-nm protein.
    smooth  : Gaussian smoothing (nm) of the tangent angle -> clean curvature.
    steer   : optional f(z, theta) -> dtheta added each step (confinement,
              avoidance).
    """
    n = int(length / ds)
    dth = rng.normal(0, np.sqrt(ds / lp), n)
    if smooth:
        from scipy.ndimage import gaussian_filter1d
        # unit-sum kernel: keeps the long-range angular diffusion (lp),
        # removes only the small-scale curvature noise
        dth = gaussian_filter1d(dth, smooth / ds, mode="nearest")
    z = np.empty(n + 1, complex); z[0] = complex(*start); th = np.radians(heading)
    for i in range(n):
        if steer is not None:
            th += steer(z[i], th)
        th += dth[i]
        z[i + 1] = z[i] + ds * np.exp(1j * th)
    return z

def chain_path(z, node_spacing=0.6):
    """Polyline -> smooth Bezier Path with a node every ~node_spacing nm."""
    L = np.abs(np.diff(z)).sum(); n = max(int(L / node_spacing), 3)
    return catmull_rom_path(_resample(z, n), closed=False)

def draw_pdda(ax, z, width=0.8, casing_pt=0.45, style="tube", charges=None,
              badge=None, zorder=2, ppu=None, color=None, line=None,
              capstyle="round", gid=None, node_spacing=0.6):
    """Draw a PDDA chain along centre-line z (complex, nm).
    width     : tube width (nm). ~0.8 nm ~ cross-section of the
                dimethyl-pyrrolidinium backbone.
    style     : 'tube' (fill + darker casing; crossings read over/under) or
                'line' (single stroke, for dense or small use).
    charges   : spacing (nm) of '+' badges along the chain, or list of
                arc-length fractions. Symbols mark charge sign, not count
                (PDDA carries ~2 charges per nm).
    """
    ppu = ppu or pt_per_unit(ax)
    col = color or PALETTE["pdda"]; ln = line or PALETTE["pdda_line"]
    path = chain_path(z, node_spacing)
    w_pt = width * ppu
    arts = []
    if style == "tube":
        cpath = path
        if capstyle == "butt" and len(z) > 12:
            # overlay piece: casing stops 0.25 nm short of the fill so the
            # butt ends merge invisibly with the chain drawn underneath
            k = max(int(0.25 / np.abs(np.diff(z)).mean()), 1)
            cpath = chain_path(z[k:-k], node_spacing)
        cas = PathPatch(cpath, facecolor="none", edgecolor=ln, lw=w_pt + 2 * casing_pt,
                        capstyle=capstyle, joinstyle="round", zorder=zorder)
        ax.add_patch(cas); arts.append(cas)
    core = PathPatch(path, facecolor="none", edgecolor=col if style == "tube" else shade(col, 0.2),
                     lw=w_pt if style == "tube" else w_pt * 0.8,
                     capstyle=capstyle, joinstyle="round", zorder=zorder + 0.01)
    ax.add_patch(core); arts.append(core)
    if charges is not None:
        b = badge or {}
        d = np.r_[0, np.cumsum(np.abs(np.diff(z)))]
        if np.isscalar(charges):
            s = np.arange(charges / 2, d[-1] - 0.3 * charges, charges)
        else:
            s = np.asarray(charges) * d[-1]
        for si in s:
            p = np.interp(si, d, z.real) + 1j * np.interp(si, d, z.imag)
            arts += draw_badge(ax, p, "+", r=b.get("r", 0.95 * width), color=ln,
                               lw_pt=b.get("lw_pt", casing_pt), zorder=zorder + 0.02, ppu=ppu)
    if gid:
        for q, a in enumerate(arts): a.set_gid(f"{gid}_{q}")
    return path, arts


# ----------------------------------------------------------------- figure helpers
def rc():
    """Nature preset; Arial if installed, else metric-identical Liberation Sans.
    Math text (subscripts, Greek) uses the same face, no DejaVu fallback."""
    from matplotlib import font_manager as fm
    names = {f.name for f in fm.fontManager.ttflist}
    face = next((f for f in ("Arial", "Helvetica", "Liberation Sans") if f in names), "DejaVu Sans")
    mpl.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": [face],
        "font.size": 6, "pdf.fonttype": 42, "svg.fonttype": "none",
        "mathtext.fontset": "custom", "mathtext.rm": face,
        "mathtext.it": f"{face}:italic", "mathtext.bf": f"{face}:bold",
        "mathtext.sf": face, "mathtext.default": "regular",
        "savefig.dpi": 600, "path.simplify": False,
    })

def canvas_mm(w_mm, h_mm, mm_per_nm, origin_nm=(0, 0)):
    """Figure of w x h mm whose single axes maps 1 nm -> mm_per_nm mm.
    origin_nm = data coordinate at the lower-left corner."""
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(w_mm * MM, h_mm * MM))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(origin_nm[0], origin_nm[0] + w_mm / mm_per_nm)
    ax.set_ylim(origin_nm[1], origin_nm[1] + h_mm / mm_per_nm)
    ax.set_aspect("equal"); ax.axis("off")
    return fig, ax


# ----------------------------------------------------------------- interior scene
def _poly_of(z):
    return Path(_c2xy(z))

def place_bsa(rng, region, size=8.0, phi=0.43, gap=0.35, squash=(0.82, 1.0),
              pad=6.0, max_tries=60000):
    """Random sequential addition of non-overlapping BSA glyphs until the area
    fraction inside `region` (a closed Path, nm) reaches phi.
    Returns list of dicts (xy, angle, mirror, squash, outline)."""
    (x0, y0), (x1, y1) = region.get_extents().get_points()
    x0 -= pad; y0 -= pad; x1 += pad; y1 += pad
    gx, gy = np.meshgrid(np.arange(x0, x1, 0.25), np.arange(y0, y1, 0.25))
    grid = np.c_[gx.ravel(), gy.ravel()]
    in_reg = region.contains_points(grid)
    covered = np.zeros(len(grid), bool)
    out = []; rb = 0.55 * size
    base = bsa_outline(72)
    for _ in range(max_tries):
        if covered[in_reg].mean() >= phi:
            break
        xy = (rng.uniform(x0, x1), rng.uniform(y0, y1))
        ang = rng.uniform(0, 360); mir = bool(rng.integers(2)); sq = rng.uniform(*squash)
        zc = _xf(base, xy, size, ang, mir, sq)
        P = _poly_of(zc)
        ok = True
        for g in out:
            if abs(complex(*xy) - complex(*g["xy"])) > 2 * rb + gap:
                continue
            if g["path"].contains_points(_c2xy(zc), radius=gap).any() or \
               P.contains_points(_c2xy(g["z"]), radius=gap).any():
                ok = False; break
        if not ok:
            continue
        out.append(dict(xy=xy, angle=ang, mirror=mir, squash=sq, z=zc, path=P))
        bb = (abs(gx.ravel() - xy[0]) < rb) & (abs(gy.ravel() - xy[1]) < rb)
        covered[bb] |= P.contains_points(grid[bb])
    phi_drawn = covered[in_reg].mean()
    return out, phi_drawn

def chain_layers(z, proteins, rng, p_front=0.5, margin=0.6, link=2.5):
    """Split a chain into the parts drawn behind / in front of the proteins it
    crosses (2D projection of a 3D mesh). Returns list of (i0, i1) index
    ranges for front pieces, and a boolean 'hidden' mask (behind a protein)."""
    n = len(z); owner = -np.ones(n, int)
    pts = _c2xy(z)
    for j, g in enumerate(proteins):
        near = np.abs(z - complex(*g["xy"])) < 6.0
        if near.any():
            ins = np.zeros(n, bool); ins[near] = g["path"].contains_points(pts[near])
            owner[ins] = j
    inside = owner >= 0
    runs = []; i = 0
    while i < n:
        if inside[i]:
            j = i
            while j + 1 < n and inside[j + 1]: j += 1
            runs.append([i, j]); i = j + 1
        else:
            i += 1
    ds = np.abs(np.diff(z)).mean()
    front = []; prev_end = -10 ** 9; prev_front = None
    for r in runs:
        gap = (r[0] - prev_end) * ds
        f = prev_front if (prev_front is not None and gap < link) else (rng.random() < p_front)
        front.append(f); prev_end = r[1]; prev_front = f
    hidden = np.zeros(n, bool); pieces = []
    m = int(margin / ds)
    for r, f in zip(runs, front):
        if f:
            pieces.append([max(r[0] - m, 0), min(r[1] + m, n - 1)])
        else:
            hidden[r[0]:r[1] + 1] = True
    # merge overlapping front pieces
    merged = []
    for p in sorted(pieces):
        if merged and p[0] <= merged[-1][1] + int(link / ds):
            merged[-1][1] = max(merged[-1][1], p[1])
        else:
            merged.append(p)
    return merged, hidden

def _spread_target(rng, region, kd, cen, Rb):
    """Pick a target point in the region, favouring places far from strands."""
    g = np.arange(-Rb, Rb + 1e-9, 2.0)
    gx, gy = np.meshgrid(g + cen.real, g + cen.imag)
    pts = np.c_[gx.ravel(), gy.ravel()]
    pts = pts[region.contains_points(pts, radius=-3.0)]
    if kd is None:
        return complex(*pts[rng.integers(len(pts))])
    d, _ = kd.query(pts)
    w = d ** 3; w /= w.sum()
    return complex(*pts[rng.choice(len(pts), p=w)])

def _tight_loops(z, min_sep=20.0, step=0.5):
    """True if the chain crosses itself within < min_sep nm of contour."""
    zz = _resample(z, max(int(np.abs(np.diff(z)).sum() / step), 4))
    a, b = zz[:-1], zz[1:]
    n = len(a); m = int(min_sep / step)
    for i in range(n):
        j = np.arange(i + 2, min(i + m, n))
        if not len(j):
            continue
        p, r = a[i], b[i] - a[i]; q, s = a[j], b[j] - a[j]
        cr = (r.conj() * s).imag
        ok = np.abs(cr) > 1e-12
        t = ((q - p).conj() * s).imag / np.where(ok, cr, 1)
        u = ((q - p).conj() * r).imag / np.where(ok, cr, 1)
        if np.any(ok & (t >= 0) & (t <= 1) & (u >= 0) & (u <= 1)):
            return True
    return False

def strand_spacing(L_in, area):
    """Mean distance between strand crossings along a random line
    (Cauchy-Crofton): pi*A / (2*L)."""
    return np.pi * area / (2 * L_in)

def draw_interior(ax, region, rng, size=8.0, phi=0.43, spacing=9.0, lp=3.0,
                  width=0.8, bsa_charges=0, pdda_charge_every=None, clip=True,
                  bg=True, rim_pt=0.75, ppu=None, seams=True, repel=2.5,
                  max_chains=40, gid_prefix=""):
    """Coacervate interior inside `region` (closed Path in nm).
    phi      : BSA area fraction (0.43 ~ phi_eff 0.41-0.47 at ~260 mg/mL).
    spacing  : mean strand spacing of the drawn PDDA network (nm), measured
               along random lines; 9 nm ~ SANS xi. Chains are added until
               the drawn contour length reaches pi*A/(2*spacing).
    Chains enter from outside and leave again (no visible ends), are mildly
    repelled by strands already drawn (even mesh), and pass over or under
    the proteins they cross (random, 50:50)."""
    from scipy.spatial import cKDTree
    ppu = ppu or pt_per_unit(ax)
    crng = np.random.default_rng(int(rng.integers(1 << 30)))  # charges only
    clip_patch = PathPatch(region, facecolor=PALETTE["coac_bg"] if bg else "none",
                           edgecolor="none", zorder=0)
    clip_patch.set_gid(f"{gid_prefix}coacervate_bg")
    ax.add_patch(clip_patch)
    prots, phi_drawn = place_bsa(rng, region, size=size, phi=phi)
    arts = []
    for j, g in enumerate(prots):
        u = crng.uniform(0, 1, 3)
        ch = tuple(u[:bsa_charges]) if bsa_charges else ()
        _, a = draw_bsa(ax, g["xy"], size, g["angle"], g["mirror"], g["squash"],
                        charges=ch, zorder=3, ppu=ppu, seams=seams, gid=f"{gid_prefix}bsa{j:02d}")
        arts += a
    (x0, y0), (x1, y1) = region.get_extents().get_points()
    cen = complex((x0 + x1) / 2, (y0 + y1) / 2); Rb = 0.5 * max(x1 - x0, y1 - y0)
    area = np.abs(0.5 * np.sum(region.vertices[:-1, 0] * region.vertices[1:, 1]
                               - region.vertices[1:, 0] * region.vertices[:-1, 1]))
    L_target = np.pi * area / (2 * spacing)
    chains = []; kd = None; total_in = 0.0
    def make_steer(kd):
        if kd is None or not repel:
            return None
        def steer(zz, th):
            idx = kd.query_ball_point((zz.real, zz.imag), repel)
            if not idx:
                return 0.0
            p = kd.data[idx]; v = (zz.real - p[:, 0]) + 1j * (zz.imag - p[:, 1])
            F = (v / np.maximum(np.abs(v) ** 2, 0.25)).sum()
            return 0.03 * np.imag(np.conj(np.exp(1j * th)) * F)
        return steer
    def traverse():
        """Chain guided through 1-2 waypoints in sparsely covered places, then
        out the far side. Small-scale shape is worm-like (lp); the waypoint
        pull only sets the route across the window."""
        rep = make_steer(kd)
        for _ in range(200):
            wps = [_spread_target(rng, region, kd, cen, Rb)]
            if rng.random() < 0.6:
                w2 = _spread_target(rng, region, kd, cen, Rb)
                if abs(w2 - wps[0]) > 0.5 * Rb:
                    wps.append(w2)
            d_in = np.exp(1j * rng.uniform(0, 2 * np.pi))
            start = cen + (Rb + 3) * d_in
            if len(wps) == 1:
                d_out = -d_in * np.exp(1j * rng.uniform(-0.9, 0.9))
            else:
                d_out = (wps[-1] - wps[0]) / abs(wps[-1] - wps[0]) * np.exp(1j * rng.uniform(-0.6, 0.6))
            wps.append(cen + (Rb + 6) * d_out)
            state = {"k": 0}
            def steer(zz, th):
                w = wps[state["k"]]
                ahead = abs((np.angle(w - zz) - th + np.pi) % (2 * np.pi) - np.pi) < 1.75
                if state["k"] < len(wps) - 1 and (abs(zz - w) < 5.0 or
                                                  (abs(zz - w) < 9.0 and not ahead)):
                    state["k"] += 1; w = wps[state["k"]]   # passed it: no orbiting
                to = (np.angle(w - zz) - th + np.pi) % (2 * np.pi) - np.pi
                s = 0.018 * to
                return s + (rep(zz, th) if rep else 0.0)
            z = wlc(rng, (start.real, start.imag), np.degrees(np.angle(wps[0] - start)),
                    6 * Rb + 40, lp=lp, steer=steer)
            inr = region.contains_points(_c2xy(z))
            if not inr.any():
                continue
            k_in = int(np.argmax(inr))
            last_in = len(inr) - 1 - int(np.argmax(inr[::-1]))
            if last_in >= len(z) - 2 or state["k"] < len(wps) - 1:
                continue                      # never left / never reached its route
            if _tight_loops(z[:last_in + 1]):
                continue                      # lp = 3 nm makes small loops rare
            return z[:min(last_in + 25, len(z) - 1) + 1]
        raise RuntimeError("no traversing chain found")
    while total_in < L_target and len(chains) < max_chains:
        z = traverse()
        inreg = region.contains_points(_c2xy(z))
        L_in = np.abs(np.diff(z))[inreg[:-1]].sum()
        if total_in + L_in > L_target + 0.5 * L_in and chains:
            break                                   # closest to target
        chains.append(z); total_in += L_in
        allp = np.concatenate([_c2xy(c[::5]) for c in chains])
        kd = cKDTree(allp)
    n_badges = {"+": 0, "-": len(prots) * bsa_charges}
    allpts = np.concatenate([_c2xy(c) for c in chains])
    owner = np.concatenate([np.full(len(c), i) for i, c in enumerate(chains)])
    kd_all = cKDTree(allpts)
    def clear(i, z, k):
        """End of an over-piece at z[k] must sit in free space: >= 1.4 nm from
        other strands (or distant parts of the same strand), outside proteins."""
        for j in kd_all.query_ball_point((z[k].real, z[k].imag), 1.4):
            if owner[j] != i:
                return False
        for g in prots:
            if abs(z[k] - complex(*g["xy"])) < 6 and g["path"].contains_point((z[k].real, z[k].imag), radius=0.3):
                return False
        return True
    for i, z in enumerate(chains):
        pieces, hidden = chain_layers(z, prots, rng)
        stepn = max(int(0.2 / np.abs(np.diff(z)).mean()), 1); lim = int(4.0 / 0.1)
        for p in pieces:
            for side, sgn in ((0, -1), (1, +1)):
                for _ in range(0, lim, stepn):
                    if clear(i, z, p[side]):
                        break
                    nxt = p[side] + sgn * stepn
                    if nxt < 0 or nxt >= len(z) or hidden[nxt]:
                        break
                    p[side] = nxt
        zb = 2 + 0.05 * i; zf = 4 + 0.05 * i
        _, a = draw_pdda(ax, z, width=width, zorder=zb, ppu=ppu, gid=f"{gid_prefix}pdda{i:02d}"); arts += a
        for q, (p0, p1) in enumerate(pieces):
            _, a = draw_pdda(ax, z[p0:p1 + 1], width=width, zorder=zf, ppu=ppu,
                             capstyle="butt", gid=f"{gid_prefix}pdda{i:02d}_over{q:02d}"); arts += a
        off = crng.uniform(0, pdda_charge_every or 1)
        if pdda_charge_every:
            inreg = region.contains_points(_c2xy(z), radius=-1.0)
            d = np.r_[0, np.cumsum(np.abs(np.diff(z)))]
            for s in np.arange(off, d[-1], pdda_charge_every):
                k = min(int(np.searchsorted(d, s)), len(z) - 1)
                if hidden[k] or not inreg[k]:
                    continue
                infront = any(p0 <= k <= p1 for p0, p1 in pieces)
                arts += draw_badge(ax, z[k], "+", r=0.95 * width, color=PALETTE["pdda_line"],
                                   lw_pt=0.45, zorder=(zf if infront else zb) + 0.03, ppu=ppu)
                n_badges["+"] += 1
    if clip:
        for a in arts:
            a.set_clip_path(clip_patch)
    if rim_pt:
        ax.add_patch(PathPatch(region, facecolor="none", edgecolor=PALETTE["coac"],
                               lw=rim_pt, zorder=10))
    return dict(n_bsa_placed=len(prots),
                n_bsa_centred_in=int(sum(region.contains_point(g["xy"]) for g in prots)),
                phi_drawn=float(phi_drawn), n_chains=len(chains),
                chain_nm_in=float(total_in), region_nm2=float(area),
                strand_spacing_nm=float(strand_spacing(total_in, area)),
                badges=n_badges)

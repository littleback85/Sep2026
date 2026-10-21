"""scenes.py — the two Fig. 1 schematics as molecular scenes (all in nm).

    zoom_scene(seed)          Fig. 1a zoom: oil | anchored layer | mobile coacervate | dilute
    film_scenes(seed)         Fig. 1c film states: rest (1), stepwise thinning,
                              core expelled at hb (2), layers compressed (3)

Geometry follows the numbers in pdda_capacity.py / Fig. 1 v2:
  hb = 20 nm holds four BSA layers (two per oil surface: one adsorbed,
  flattened row + one row glued onto it by PDDA), so the anchored layer is
  ~hb/2 = 10 nm; above hb the mobile core is expelled one layer at a time
  (d = 7.7 nm); rest film hb + 4d = 50.8 nm; at 0.86 MPa h = 0.65 hb = 13 nm.
The anchored rows are the same molecules (same x positions) in every film
state; only the mobile core changes between (1) and (2). State (3) is state (2)
squeezed to 0.65 of its thickness: the same BSA and the same PDDA chains,
closer and flatter (water and ions leave).
"""
import numpy as np
from shapely.geometry import Polygon, box
import pdda_glue as PG

HB = 20.0          # nm
D = 7.7            # nm, SANS layer spacing
H_REST = HB + 4 * D
H_COMP = 0.65 * HB  # 13.0 nm (Murnaghan wall at 0.86 MPa)
PITCH = 8.9        # nm, lateral pitch of the anchored rows (8-nm glyph + ~0.9-nm gaps)


# ----------------------------------------------------------------- anchored rows
def _place_on_surface(x, y_s, side, sq, ang, mir, kind, c_off, flatten=True, dip=0.35):
    """Protein whose oil-facing side sits on the surface y_s (side +1: coacervate
    above the surface, -1: below). The outline dips `dip` nm into the oil and is
    flattened back onto it: an adsorbed, partly spread molecule."""
    a = ang + (180.0 if side < 0 else 0.0)
    p0 = PG.make_bsa((x, 0.0), a, mir, sq, kind, c_off=c_off)
    if side > 0:
        y = y_s - dip - p0.out.imag.min()
        return PG.make_bsa((x, y), a, mir, sq, kind, floor=y_s if flatten else None, c_off=c_off)
    y = y_s + dip - p0.out.imag.max()
    return PG.make_bsa((x, y), a, mir, sq, kind, ceiling=y_s if flatten else None, c_off=c_off)

def _nest(S, x, side, sq, ang, mir, kind, gap, y_start, c_off, against=("ads",)):
    """Lower (side +1) or raise (side -1) a protein from y_start toward the
    surface until it is `gap` nm from the row below it: it settles in the hollow
    between two adsorbed molecules."""
    a = ang + (180.0 if side < 0 else 0.0)
    lo, hi = 0.0, 18.0          # offset from y_start toward the surface
    mk = lambda t: PG.make_bsa((x, y_start - side * t), a, mir, sq, kind, c_off=c_off)
    if S.min_dist(mk(hi), against) > gap:
        return mk(hi)
    for _ in range(16):
        t = (lo + hi) / 2
        if S.min_dist(mk(t), against) > gap:
            lo = t
        else:
            hi = t
    return mk(lo)

# anchored rows: squash of the adsorbed row (sq1, flattened at the oil) and of the
# glued row (sq2), gap between them (room for one PDDA strand), tilt ranges (deg).
# sq2 is set so that the anchored layer is ~10 nm = hb/2 and the two glued rows
# meet at hb with ~1.5-2 nm left for PDDA stitching across the midplane.
ROWS = dict(sq1=(0.52, 0.58), sq2=(0.86, 0.94), gap12=(1.05, 1.3), a1=5.0, a2=12.0)

def anchored_rows(S, x_ads, y_surface, side, rng, sq1=ROWS["sq1"], sq2=ROWS["sq2"],
                  gap12=ROWS["gap12"], a1=ROWS["a1"], a2=ROWS["a2"]):
    """Two anchored rows on one oil surface. x_ads: x of the adsorbed row (the
    second row sits in the hollows between them). y_surface: float or f(x).
    Returns the list of added proteins."""
    ys = y_surface if callable(y_surface) else (lambda x, v=y_surface: v)
    added = []
    for x in x_ads:
        p = _place_on_surface(x, ys(x), side, rng.uniform(*sq1), rng.uniform(-a1, a1),
                              bool(rng.integers(2)), "ads", S.c_off)
        p.side = side
        added.append(S.add(p))
    xs2 = (np.asarray(x_ads)[:-1] + np.asarray(x_ads)[1:]) / 2
    for x in xs2:
        x = x + rng.uniform(-0.4, 0.4)
        p = _nest(S, x, side, rng.uniform(*sq2), rng.uniform(-a2, a2), bool(rng.integers(2)),
                  "anc", rng.uniform(*gap12), ys(x) + side * 16.0, S.c_off)
        p.side = side
        added.append(S.add(p))
    return added

def glue_pairs(Pi, Pj):
    """Routing preference: PDDA sandwiched between the adsorbed and the glued
    row (x3), and stitching the two glued rows across the film midplane (x3)."""
    k = {Pi.kind, Pj.kind}
    if k == {"ads", "anc"}:
        return 3.0
    if k == {"anc"} and getattr(Pi, "side", 0) * getattr(Pj, "side", 0) < 0:
        return 3.0
    if "ads" in k and "mob" in k:
        return 0.5
    return 1.0

def glue_strong(Pi, Pj):
    """First pass in the anchored layer: chains that run sandwiched between the
    adsorbed and the glued row and only now and then loop into the core."""
    k = {Pi.kind, Pj.kind}
    if k == {"ads", "anc"}:
        return 6.0
    if k == {"anc"}:
        return 1.5 if getattr(Pi, "side", 0) == getattr(Pj, "side", 0) else 3.0
    if k == {"anc", "mob"}:
        return 0.5
    return 0.2

def glue_first(S, rng, n=2, target=8.5):
    """Lay n glue chains in the anchored layer before the rest of the network."""
    PG.Router(S, rng, contour_per_bsa=target, pair_w=glue_strong, p_edge_start=0.7,
              start_filter=lambda p: p.kind in ("ads", "anc")).run(max_chains=n)

def row_x(rng, x0, x1, pitch=PITCH, jit=0.3, phase=0.0):
    xs = np.arange(x0 + phase, x1 + pitch, pitch)
    return xs + rng.uniform(-jit, jit, len(xs))

def extent(prots, side):
    """Highest (side +1) or lowest (side -1) outline point of a set of proteins."""
    v = [p.out.imag.max() if side > 0 else p.out.imag.min() for p in prots]
    return max(v) if side > 0 else min(v)


# ----------------------------------------------------------------- Fig. 1a zoom
ZOOM = dict(w=45.0, h=70.0, y_oil=16.0, y_int=61.0)

def zoom_scene(seed=11, phi=0.42, contour_per_bsa=8.5):
    """Zoom of the corona: oil (bottom), anchored layer (adsorbed row, dark;
    glued row, mid), mobile coacervate (light, isotropic), dilute phase (top)."""
    rng = np.random.default_rng(seed)
    w, h, yo, yi = ZOOM["w"], ZOOM["h"], ZOOM["y_oil"], ZOOM["y_int"]
    win = (0.0, 0.0, w, h)
    region = box(-12, yo + PG.R_TUBE + 0.05, w + 12, yi - 0.45)
    edges = [(complex(0, yo), complex(0, yi), -1 + 0j), (complex(w, yo), complex(w, yi), 1 + 0j)]
    S = PG.Scene(win, region, edges)
    xs = row_x(rng, -5.0, w + 5.0, phase=rng.uniform(0, PITCH))
    anc = anchored_rows(S, xs, yo, +1, rng)
    top = extent(anc, +1)
    phi_drawn = S.rsa(rng, box(-7, yo, w + 7, yi), box(0, top, w, yi), phi, gap=0.8)
    glue_first(S, rng, n=2)
    R = PG.Router(S, rng, contour_per_bsa=contour_per_bsa, pair_w=glue_pairs)
    st = R.run()
    st.update(phi_mobile=phi_drawn, anchored_top=top - yo,
              order_mobile=PG.orientation(S, box(0, top + 2, w, yi - 2)),
              order_anchored=PG.orientation(S, box(0, yo, w, top)))
    return S, st


# ----------------------------------------------------------------- Fig. 1c film states
FILM = dict(w=49.0, h=62.0)

def _film_scene(h_of_x, rng, c_off=0.5):
    """Empty scene for a film between two oil drops; thickness h(x) (callable)."""
    w, hh = FILM["w"], FILM["h"]
    win = (-w / 2, -hh / 2, w / 2, hh / 2)
    xs = np.linspace(-w / 2 - 12, w / 2 + 12, 400)
    hx = np.array([h_of_x(x) for x in xs])
    m = PG.R_TUBE + 0.05
    region = Polygon(list(zip(xs, -hx / 2 + m)) + list(zip(xs[::-1], hx[::-1] / 2 - m)))
    hl, hr = h_of_x(-w / 2), h_of_x(w / 2)
    edges = [(complex(-w / 2, -hl / 2), complex(-w / 2, hl / 2), -1 + 0j),
             (complex(w / 2, -hr / 2), complex(w / 2, hr / 2), 1 + 0j)]
    return PG.Scene(win, region, edges, c_off=c_off)

def _anchored_pair(S, h_of_x, xs_b, xs_t, seed, **kw):
    """Anchored rows on both surfaces; a fixed seed keeps them identical
    between film states."""
    rb = np.random.default_rng(seed); rt = np.random.default_rng(seed + 1)
    bot = anchored_rows(S, xs_b, lambda x: -h_of_x(x) / 2, +1, rb, **kw)
    topr = anchored_rows(S, xs_t, lambda x: h_of_x(x) / 2, -1, rt, **kw)
    return bot, topr

def _rows_mobile(S, rng, rows, gap=0.8, allowed=None, tries=80):
    """Mobile BSA in layers: rows = [(y, x0, x1, pitch)]. Random orientation;
    a slot is skipped if no orientation fits."""
    for y, x0, x1, pitch in rows:
        x = x0 + rng.uniform(0, 1.5)
        while x <= x1:
            for _ in range(tries):     # layered BSA lie roughly flat in the layer
                p = PG.make_bsa((x + rng.uniform(-0.8, 0.8), y + rng.uniform(-0.5, 0.5)),
                                rng.uniform(-30, 30) + 180 * rng.integers(2), bool(rng.integers(2)),
                                rng.uniform(0.8, 0.95), "mob", c_off=S.c_off)
                if S.fits(p, gap, allowed):
                    S.add(p); break
            x += pitch + rng.uniform(-0.4, 0.6)

def film_scenes(seed=5, rest_phi=0.42, contour_per_bsa=8.5):
    """Returns dict name -> (Scene, h_of_x, stats) for 'rest', 'step', 'hb', 'comp'."""
    w = FILM["w"]
    base = np.random.default_rng(seed)
    xs_b = row_x(base, -w / 2 - 6, w / 2 + 6, phase=base.uniform(0, PITCH))
    xs_t = xs_b + PITCH / 2 + base.uniform(-0.6, 0.6)      # top row offset: interdigitates at hb
    row_seed = int(base.integers(1 << 20))
    out = {}

    # (1) rest: anchored rows + bulk-like mobile core
    hR = lambda x: H_REST
    S = _film_scene(hR, None)
    bot, top = _anchored_pair(S, hR, xs_b, xs_t, row_seed)
    yb, yt = extent(bot, +1), extent(top, -1)
    rng = np.random.default_rng(seed + 101)
    allowed = box(-w / 2 - 7, -H_REST / 2, w / 2 + 7, H_REST / 2)
    phi = S.rsa(rng, allowed, box(-w / 2, yb, w / 2, yt), rest_phi, gap=0.65, max_tries=60000)
    glue_first(S, rng, n=3)
    st = PG.Router(S, rng, contour_per_bsa=contour_per_bsa, pair_w=glue_pairs).run()
    st.update(phi_core=phi, h=H_REST, order_core=PG.orientation(S, box(-w / 2, yb + 2, w / 2, yt - 2)))
    out["rest"] = (S, hR, st)

    # stepwise thinning: hb + d (left, one mobile layer) | hb + 2d (right, two)
    k = int(np.argmin(np.abs(xs_b + PITCH / 2)))          # front in the gap nearest x = 0
    xf = 0.5 * (xs_b[k] + xs_b[k + 1])
    hS = lambda x: HB + 1.5 * D + 0.5 * D * np.tanh((x - xf) / 1.8)
    S = _film_scene(hS, None)
    bot, top = _anchored_pair(S, hS, xs_b, xs_t, row_seed)
    rng = np.random.default_rng(seed + 202)
    allowed = S.region.buffer(0.45)
    _rows_mobile(S, rng, [(0.0, -w / 2 - 6, xf - 4.0, 9.0),
                          (-D / 2, xf + 1.5, w / 2 + 6, 9.0),
                          (+D / 2, xf + 5.5, w / 2 + 6, 9.0)], allowed=allowed)
    glue_first(S, rng, n=2)
    st = PG.Router(S, rng, contour_per_bsa=contour_per_bsa, pair_w=glue_pairs).run()
    st.update(h_left=hS(-w / 2), h_right=hS(w / 2), x_front=xf)
    out["step"] = (S, hS, st)

    # (2) core expelled: the two anchored layers meet at h = hb
    hB = lambda x: HB
    S = _film_scene(hB, None)
    bot, top = _anchored_pair(S, hB, xs_b, xs_t, row_seed)
    rng = np.random.default_rng(seed + 303)
    st = PG.Router(S, rng, contour_per_bsa=contour_per_bsa, g_max=3.6, pair_w=glue_pairs).run()
    mid = box(-w / 2, -2.5, w / 2, 2.5)
    st.update(h=HB, gap_mid=min(p.poly.distance(q.poly) for p in bot for q in top),
              order=PG.orientation(S, box(-w / 2, -HB / 2, w / 2, HB / 2)),
              midplane_crossings=_crossings(S, 0.0))
    out["hb"] = (S, hB, st)

    # (3) compressed to 0.65 hb: the SAME molecules and chains as (2), squeezed
    # normal to the film (water and ions leave; nothing else does)
    f = H_COMP / HB
    hC = lambda x: H_COMP
    S2 = out["hb"][0]
    S = _film_scene(hC, None, c_off=S2.c_off)
    squeeze = lambda z: z.real + 1j * f * z.imag
    for p in S2.prots:
        q = S.add(PG.transform_protein(p, squeeze, c_off=S2.c_off)); q.side = getattr(p, "side", 0)
    for ch in S2.chains:
        S.chains.append(dict(ch, z=squeeze(ch["z"])))
    bot = [p for p in S.prots if p.side > 0]; top = [p for p in S.prots if p.side < 0]
    R = PG.Router(S, rng)
    st = dict(contour_nm=sum(R.contour_in_view(c["z"]) for c in S.chains), bsa_in_view=R.bsa_in_view(),
              n_chains=len(S.chains), h=H_COMP, squeeze=f,
              gap_mid=min(p.poly.distance(q.poly) for p in bot for q in top),
              order=PG.orientation(S, box(-w / 2, -H_COMP / 2, w / 2, H_COMP / 2)),
              midplane_crossings=_crossings(S, 0.0))
    st["contour_per_bsa"] = st["contour_nm"] / st["bsa_in_view"]
    out["comp"] = (S, hC, st)
    return out

def _crossings(S, y0):
    """Times the drawn chains cross the film midplane inside the window."""
    x0, _, x1, _ = S.window
    n = 0
    for ch in S.chains:
        z = ch["z"]; m = (z.real[:-1] > x0) & (z.real[:-1] < x1)
        n += int((np.sign(z.imag[:-1] - y0) != np.sign(z.imag[1:] - y0))[m].sum())
    return n

"""pdda_glue.py — PDDA chains that glue BSA (belt-and-pulley routing).

A chain is a walk over neighbouring proteins. Around each protein it follows
the convex hull of the outline offset by the tube radius: a 'train', in
contact. Between proteins it runs along a common tangent: a 'bridge'.
  * same rotation sense on both proteins -> outer tangent: the chain spans the
    mouth of the gap;
  * opposite sense -> inner tangent: the chain threads through the gap and is
    sandwiched between both proteins (one strand gluing two BSA).
The tangent construction keeps the centre-line smooth (no kinks), the wrap per
protein sets the turning (lp ~ 3 nm vs an 8-nm protein: a chain turns by a
large angle at every protein, so it is a random walk on the protein scale),
and the next protein is chosen without any directional preference, so in an
isotropic packing the chain orientation is isotropic. Chains never end in
view: they enter/leave through open window edges or run under a protein
(out of the drawing plane).

Everything is in nm; draw with coac_glyphs (equal-aspect axes).
"""
import numpy as np
from scipy.spatial import ConvexHull, cKDTree
from scipy.ndimage import gaussian_filter1d
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union
import shapely
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch, Rectangle
import coac_glyphs as G

R_TUBE = 0.40        # nm, half of the 0.8-nm tube
DS = 0.1             # nm, sampling of all centre-lines


# ----------------------------------------------------------------- geometry
def ring_resample(z, ds=DS):
    zz = np.r_[z, z[:1]]
    d = np.r_[0, np.cumsum(np.abs(np.diff(zz)))]
    n = max(int(round(d[-1] / ds)), 8)
    s = np.linspace(0, d[-1], n, endpoint=False)
    return np.interp(s, d, zz.real) + 1j * np.interp(s, d, zz.imag)

def line_resample(z, ds=DS):
    z = np.asarray(z, complex)
    d = np.r_[0, np.cumsum(np.abs(np.diff(z)))]
    n = max(int(round(d[-1] / ds)), 2)
    s = np.linspace(0, d[-1], n + 1)
    return np.interp(s, d, z.real) + 1j * np.interp(s, d, z.imag)

def signed_area(z):
    return 0.5 * np.sum(z.real * np.roll(z.imag, -1) - np.roll(z.real, -1) * z.imag)

def ccw(z):
    return z if signed_area(z) > 0 else z[::-1]

def cross(u, v):
    return (np.conj(u) * v).imag

def soft_floor(y, level, eps=0.8):
    """Smooth max(y, level): flattens an outline against a wall at `level`."""
    a = y - (level + eps / 2)
    return level + (a + np.sqrt(a * a + eps * eps)) / 2


# ----------------------------------------------------------------- proteins
class Protein:
    """One BSA: outline, seams, kind ('mob' | 'anc' | 'ads'), contact hull."""
    def __init__(self, out, seams, kind, c_off):
        self.out = ccw(np.asarray(out, complex))
        self.seams = seams
        self.kind = kind
        xy = G._c2xy(self.out)
        self.poly = Polygon(xy).buffer(0)
        self.c = complex(*self.poly.centroid.coords[0])
        self.c_off = c_off
        self._hull = None

    def _make_hull(self):
        hull = self.poly.buffer(self.c_off, quad_segs=12).convex_hull
        h = np.asarray(hull.exterior.coords)[:-1]
        self._hull = (hull, ccw(ring_resample(h[:, 0] + 1j * h[:, 1])),
                      complex(*hull.centroid.coords[0]))

    @property
    def hull_poly(self):
        if self._hull is None: self._make_hull()
        return self._hull[0]

    @property
    def H(self):
        """Contact hull: convex hull of the outline offset by c_off, CCW, 0.1-nm steps."""
        if self._hull is None: self._make_hull()
        return self._hull[1]

    @property
    def cH(self):
        if self._hull is None: self._make_hull()
        return self._hull[2]

_BASE = G.bsa_outline(240)
_SEAMS = [G._seam_points(s) for s in G._BSA_SEAMS]

def make_bsa(xy, angle=0.0, mirror=False, squash=1.0, kind="mob", size=8.0,
             floor=None, ceiling=None, c_off=0.5):
    """BSA glyph geometry. floor/ceiling: flatten the outline against an oil
    surface at that y (adsorbed, partly unfolded molecule)."""
    out = G._xf(_BASE, xy, size, angle, mirror, squash)
    seams = [G._xf(s, xy, size, angle, mirror, squash) for s in _SEAMS]
    if floor is not None:
        f = lambda z: z.real + 1j * soft_floor(z.imag, floor)
        out = f(out); seams = [f(s) for s in seams]
    if ceiling is not None:
        f = lambda z: z.real - 1j * soft_floor(-z.imag, -ceiling)
        out = f(out); seams = [f(s) for s in seams]
    return Protein(out, seams, kind, c_off)

def transform_protein(p, fn, kind=None, c_off=0.5):
    """New Protein with outline and seams mapped by fn (complex -> complex)."""
    return Protein(fn(p.out), [fn(s) for s in p.seams], kind or p.kind, c_off)


# ----------------------------------------------------------------- scene
class Scene:
    """window: (x0, y0, x1, y1) of the drawing; region: shapely polygon in which
    PDDA centre-lines may run (already kept R_TUBE away from oil and from the
    dilute phase); open_edges: list of (z0, z1, outward normal) where chains
    may enter and leave."""
    def __init__(self, window, region, open_edges, c_off=0.5):
        self.window = window
        self.region = region
        self.open_edges = open_edges
        self.c_off = c_off
        self.prots = []
        self.chains = []            # list of dict(z=..., ends=(...), visited=[...])

    # ---- placement
    def fits(self, p, gap, allowed=None):
        if self.prots:
            c = np.array([q.c for q in self.prots])
            if np.abs(c - p.c).min() < 3.6:     # glyphs >= 3.6 nm apart at any squash used
                return False
        if allowed is not None and not allowed.contains(p.poly):
            return False
        for q in self.prots:
            if abs(q.c - p.c) < 12.0 and q.poly.distance(p.poly) < gap:
                return False
        return True

    def add(self, p):
        self.prots.append(p); return p

    def min_dist(self, p, kinds=None):
        d = [q.poly.distance(p.poly) for q in self.prots
             if abs(q.c - p.c) < 14 and (kinds is None or q.kind in kinds)]
        return min(d) if d else np.inf

    def rsa(self, rng, allowed, measure, phi, gap=0.8, squash=(0.82, 1.0),
            kind="mob", max_tries=40000, size=8.0):
        """Random sequential addition in `allowed` (shapely) until the BSA area
        fraction inside `measure` reaches phi. Returns the drawn fraction."""
        (x0, y0, x1, y1) = allowed.bounds
        A = measure.area
        cur = unary_union([q.poly for q in self.prots]).intersection(measure).area if self.prots else 0.0
        for _ in range(max_tries):
            if cur / A >= phi:
                break
            xy = (rng.uniform(x0, x1), rng.uniform(y0, y1))
            if self.prots and np.abs(np.array([q.c for q in self.prots]) - complex(*xy)).min() < 4.2:
                continue
            p = make_bsa(xy, rng.uniform(0, 360),
                         bool(rng.integers(2)), rng.uniform(*squash), kind, size, c_off=self.c_off)
            if self.fits(p, gap, allowed):
                self.add(p); cur += p.poly.intersection(measure).area
        return cur / A


# ----------------------------------------------------------------- tangents
def _tan(H, cH, x, side):
    """Index of the tangent point on convex ring H seen from outside point x,
    with H on the `side` (+1 left, -1 right) of the ray x -> point."""
    a = np.angle((H - x) * np.conj(cH - x))
    return int(np.argmin(a)) if side > 0 else int(np.argmax(a))

def outer_bridge(P, Q, s):
    """Outer common tangent P -> Q for rotation sense s on both (hull of union)."""
    pts = np.r_[P.H, Q.H]
    try:
        hv = ConvexHull(np.c_[pts.real, pts.imag]).vertices      # CCW
    except Exception:
        return None
    nP = len(P.H)
    isP = hv < nP
    if isP.all() or (~isP).all():
        return None
    order = hv if s > 0 else hv[::-1]
    flags = order < nP
    for k in range(len(order)):
        if flags[k] and not flags[(k + 1) % len(order)]:
            return int(order[k]), int(order[(k + 1) % len(order)] - nP)
    return None

def inner_bridge(P, sP, Q, sQ):
    """Inner common tangent (chain threads between P and Q). Hulls disjoint."""
    ip = int(np.argmin(np.abs(P.H - Q.cH)))
    iq = 0
    for _ in range(16):
        iq = _tan(Q.H, Q.cH, P.H[ip], sQ)
        ip2 = _tan(P.H, P.cH, Q.H[iq], -sP)
        if ip2 == ip:
            break
        ip = ip2
    p, q = P.H[ip], Q.H[iq]
    u = q - p
    if abs(u) < 1e-6:
        return None
    if (sP * cross(u, P.H - p)).min() < -0.05 or (sQ * cross(u, Q.H - q)).min() < -0.05:
        return None
    return ip, iq

def _longest_run(mask):
    best = cur = 0
    for v in mask:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    return best

def arc(H, ia, ib, s):
    N = len(H)
    n = (ib - ia) % N if s > 0 else (ia - ib) % N
    idx = (ia + s * np.arange(n + 1)) % N
    return H[idx], n / N


# ----------------------------------------------------------------- router
class Router:
    """Builds chains on a Scene. Parameters (nm):
    g_max      : proteins closer than this are neighbours (a chain can bridge)
    f_pref     : preferred wrap fraction per protein (contact ~ f x perimeter)
    contour_per_bsa : stop when drawn contour / BSA in view reaches this
    """
    def __init__(self, scene, rng, g_max=3.2, f_pref=0.22, f_max=0.55,
                 contour_per_bsa=8.0, p_edge_start=0.35, lateral_bias=0.0, pair_w=None,
                 start_filter=None):
        """pair_w(Pi, Pj) -> factor on a step between two proteins (e.g. favour
        the adsorbed/anchored contact so PDDA is sandwiched between the rows).
        start_filter(P) -> bool: proteins a chain may start at.
        Chains already on the scene are kept and avoided."""
        self.S = scene; self.rng = rng
        self.pair_w = pair_w
        self.start_ok = np.array([True if start_filter is None else bool(start_filter(p))
                                  for p in scene.prots])
        self.g_max = g_max; self.f_pref = f_pref; self.f_max = f_max
        self.target = contour_per_bsa; self.p_edge = p_edge_start
        self.lat = lateral_bias
        P = scene.prots; n = len(P)
        self.nb = [[] for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if abs(P[i].c - P[j].c) > 8.0 + g_max + 3:
                    continue
                g = P[i].poly.distance(P[j].poly)
                if g < g_max:
                    dis = P[i].hull_poly.disjoint(P[j].hull_poly)
                    self.nb[i].append((j, g, dis)); self.nb[j].append((i, g, dis))
        self.cov = np.zeros(n)
        self._raster()
        self.kd = None; self.kd_owner = None
        for ch in scene.chains:
            for v in contacts(scene, ch) | set(ch["visited"]):
                self.cov[v] += 1
        if scene.chains:
            pts = np.concatenate([c["z"][::3] for c in scene.chains])
            self.kd = cKDTree(np.c_[pts.real, pts.imag])

    def _raster(self):
        x0, y0, x1, y1 = self.S.window
        m = 6.0
        self.gx0, self.gy0 = x0 - m, y0 - m
        nx = int((x1 - x0 + 2 * m) / DS) + 1; ny = int((y1 - y0 + 2 * m) / DS) + 1
        self.lab = -np.ones((ny, nx), np.int32)        # protein cores
        xs = self.gx0 + DS * np.arange(nx); ys = self.gy0 + DS * np.arange(ny)
        for k, p in enumerate(self.S.prots):
            core = p.poly.buffer(-0.12)
            if core.is_empty:
                continue
            bx0, by0, bx1, by1 = core.bounds
            i0 = max(int((bx0 - self.gx0) / DS), 0); i1 = min(int((bx1 - self.gx0) / DS) + 2, nx)
            j0 = max(int((by0 - self.gy0) / DS), 0); j1 = min(int((by1 - self.gy0) / DS) + 2, ny)
            if i1 <= i0 or j1 <= j0:
                continue
            X, Y = np.meshgrid(xs[i0:i1], ys[j0:j1])
            ins = shapely.contains_xy(core, X, Y)
            sub = self.lab[j0:j1, i0:i1]; sub[ins] = k
        X, Y = np.meshgrid(xs, ys)
        inwin = (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1)
        self.ok = shapely.contains_xy(self.S.region, X, Y) | ~inwin
        # outside the window only the open edges' half-planes are allowed
        if self.S.open_edges:
            beyond = np.zeros_like(inwin)
            for z0, z1, nrm in self.S.open_edges:
                t = (X + 1j * Y - z0) * np.conj(z1 - z0) / abs(z1 - z0) ** 2
                s = ((X + 1j * Y - z0) * np.conj(nrm)).real
                beyond |= (s > 0) & (t.real > -0.05) & (t.real < 1.05)
            self.ok &= inwin | beyond
        else:
            self.ok &= inwin

    def _cells(self, z):
        i = np.clip(((z.real - self.gx0) / DS).astype(int), 0, self.lab.shape[1] - 1)
        j = np.clip(((z.imag - self.gy0) / DS).astype(int), 0, self.lab.shape[0] - 1)
        return j, i

    def _score_seg(self, seg, skip, own):
        """Penalty factor for a candidate piece: overlap with other proteins,
        leaving the allowed region, running on top of other chains or itself."""
        z = line_resample(seg, 0.15)
        j, i = self._cells(z)
        if not self.ok[j, i].all():
            return 0.0
        lab = self.lab[j, i]
        ov = np.isin(lab, list(skip), invert=True) & (lab >= 0)
        ov_len = ov.sum() * 0.15
        if ov_len > 3.5:
            return 0.0
        w = np.exp(-ov_len / 0.6)
        if self.kd is not None:
            d, _ = self.kd.query(np.c_[z.real, z.imag])
            c = d < 1.0
            if _longest_run(c) * 0.15 > 2.2:       # running along another strand, not crossing it
                return 0.0
            w *= np.exp(-6.0 * c.mean())
        if own is not None and len(own) > 30:
            kd = cKDTree(np.c_[own[:-15].real, own[:-15].imag])
            d, _ = kd.query(np.c_[z.real, z.imag])
            if (d < 1.0).mean() > 0.0:
                w *= np.exp(-12.0 * (d < 1.0).mean()) * 0.3
        return w

    def _wrap_w(self, f):
        return np.exp(-((f - self.f_pref) / 0.17) ** 2) + 0.05

    def _dir_w(self, u):
        """Optional orientation preference (lateral_bias > 0: along x)."""
        if not self.lat or abs(u) < 1e-9:
            return 1.0
        c2 = np.cos(2 * np.angle(u))
        return np.exp(self.lat * c2)

    def _edge_point(self, k):
        z0, z1, nrm = self.S.open_edges[k]
        return z0, z1, nrm

    def _far(self):
        """Weight per protein: distance to the nearest drawn strand, cubed."""
        if self.kd is None:
            return np.ones(len(self.S.prots))
        c = np.array([p.c for p in self.S.prots])
        d, _ = self.kd.query(np.c_[c.real, c.imag])
        return np.maximum(d - 2.0, 0.2) ** 3

    def _start(self):
        S = self.S; P = S.prots; rng = self.rng
        x0, y0, x1, y1 = S.window
        inview = np.array([(x0 + 2 < p.c.real < x1 - 2) and (y0 < p.c.imag < y1) for p in P])
        if S.open_edges and rng.random() < self.p_edge:
            L = np.array([abs(e[1] - e[0]) for e in S.open_edges])
            k = rng.choice(len(L), p=L / L.sum())
            z0, z1, nrm = S.open_edges[k]
            u = rng.uniform(0.05, 0.95, 12)
            Es = z0 + (z1 - z0) * u + 3.0 * nrm
            if self.kd is not None:          # favour entry points far from chains
                dE, _ = self.kd.query(np.c_[Es.real, Es.imag])
                E = Es[rng.choice(len(Es), p=dE ** 3 / (dE ** 3).sum())]
            else:
                E = Es[0]
            d = np.array([abs(p.cH - E) for p in P])
            w = np.where((d < 10.0) & self.start_ok, np.exp(-d / 3.0) / (1 + 2 * self.cov) ** 2, 0) * self._far()
            if w.sum() == 0:
                return None
            i1 = rng.choice(len(P), p=w / w.sum())
            return ("edge", E, None, i1)
        w = np.where(inview & self.start_ok, 1.0 / (1 + 2 * self.cov) ** 2, 0) * self._far()
        if w.sum() == 0:
            return None
        t0 = rng.choice(len(P), p=w / w.sum())
        if not self.nb[t0]:
            return None
        js = [j for j, g, _ in self.nb[t0]]
        wj = np.array([1 / (1 + 2 * self.cov[j]) ** 2 for j in js])
        i1 = js[rng.choice(len(js), p=wj / wj.sum())]
        return ("tuck", P[t0].c, t0, i1)

    def walk(self, max_steps=40):
        """One chain. Returns dict or None."""
        rng = self.rng; P = self.S.prots
        st = self._start()
        if st is None:
            return None
        kind, E, t0, i = st
        s = int(rng.choice([-1, 1]))
        ia = _tan(P[i].H, P[i].cH, E, s)
        entry = np.array([E, P[i].H[ia]])
        skip0 = {i} if t0 is None else {i, t0}
        w0 = self._score_seg(entry, skip0, None)
        if w0 <= 0:
            return None
        pieces = [entry]
        visited = [i] if t0 is None else [t0, i]
        target_steps = int(rng.integers(4, 13))
        steps = 0
        ends = [kind, None]
        while True:
            own = np.concatenate(pieces)
            cands = []
            Pi = P[i]
            # continue to a neighbour
            for j, g, dis in self.nb[i]:
                if j in visited:
                    continue
                for sj in (s, -s):
                    if sj != s and not dis:
                        continue
                    res = outer_bridge(Pi, P[j], s) if sj == s else inner_bridge(Pi, s, P[j], sj)
                    if res is None:
                        continue
                    ib, jq = res
                    az, f = arc(Pi.H, ia, ib, s)
                    if f > self.f_max:
                        continue
                    seg = np.r_[az, P[j].H[jq]]
                    w = self._score_seg(seg, {i, j}, own)
                    if w <= 0:
                        continue
                    bl = abs(P[j].H[jq] - Pi.H[ib])
                    w *= self._wrap_w(f) * np.exp(-bl / 2.0) / (1 + 3.0 * self.cov[j]) ** 2
                    w *= self._dir_w(P[j].c - Pi.c)
                    if self.pair_w is not None:
                        w *= self.pair_w(Pi, P[j])
                    if sj != s:
                        w *= 1.3          # threading = sandwiched glue contact
                    cands.append((w, "step", j, sj, ib, jq, az))
            late = steps >= target_steps
            # leave through an open edge
            for k, (z0, z1, nrm) in enumerate(self.S.open_edges):
                t = ((Pi.c - z0) * np.conj(z1 - z0)).real / abs(z1 - z0) ** 2
                dist = -((Pi.c - z0) * np.conj(nrm)).real
                if not (0.0 < t < 1.0) or dist > 9.0:
                    continue
                X = z0 + (z1 - z0) * t + (max(dist, 0.0) + 3.0) * nrm \
                    + (z1 - z0) / abs(z1 - z0) * rng.normal(0, 1.5)          # always beyond the edge
                ib = _tan(Pi.H, Pi.cH, X, -s)
                az, f = arc(Pi.H, ia, ib, s)
                if f > self.f_max:
                    continue
                seg = np.r_[az, X]
                w = self._score_seg(seg, {i}, own)
                if w <= 0:
                    continue
                w *= self._wrap_w(f) * (2.5 if late else 0.04)
                cands.append((w, "exit", k, None, ib, X, az))
            # run under a neighbour (out of plane)
            if steps >= 2:
                for j, g, dis in self.nb[i]:
                    if j in visited or P[j].kind == "ads" and False:
                        continue
                    X = P[j].c
                    ib = _tan(Pi.H, Pi.cH, X, -s)
                    az, f = arc(Pi.H, ia, ib, s)
                    if f > self.f_max:
                        continue
                    seg = np.r_[az, X]
                    w = self._score_seg(seg, {i, j}, own)
                    if w <= 0:
                        continue
                    w *= self._wrap_w(f) * (0.5 if late else 0.01) / (1 + self.cov[j])
                    cands.append((w, "tuck", j, None, ib, X, az))
            if not cands:
                return None
            ws = np.array([c[0] for c in cands])
            c = cands[rng.choice(len(cands), p=ws / ws.sum())]
            _, typ, j, sj, ib, X, az = c
            pieces.append(az)
            if typ == "step":
                visited.append(j); i, s, ia = j, sj, X
                steps += 1
                if steps > max_steps:
                    return None
                continue
            pieces.append(np.array([X]))
            if typ == "tuck":
                visited.append(j)
            ends[1] = typ
            break
        z = _bowed(pieces, rng)
        return dict(z=z, ends=tuple(ends), visited=visited)

    def contour_in_view(self, z):
        x0, y0, x1, y1 = self.S.window
        m = (z.real >= x0) & (z.real <= x1) & (z.imag >= y0) & (z.imag <= y1)
        return np.abs(np.diff(z))[m[:-1] & m[1:]].sum()

    def bsa_in_view(self):
        W = box(*self.S.window)
        return sum(p.poly.intersection(W).area / p.poly.area for p in self.S.prots)

    def run(self, max_chains=60, tries=400):
        """Add chains until drawn contour / BSA in view reaches the target
        (existing chains count) or max_chains new chains were added."""
        n_view = self.bsa_in_view()
        total = sum(self.contour_in_view(c["z"]) for c in self.S.chains)
        added = 0
        for _ in range(tries):
            if total / n_view >= self.target or added >= max_chains:
                break
            ch = self.walk()
            if ch is None:
                continue
            z = smooth_chain(ch["z"])
            Lv = self.contour_in_view(z)
            if Lv < 6.0 or hairpin(z):
                continue
            ch["z"] = z
            self.S.chains.append(ch)
            total += Lv; added += 1
            for v in contacts(self.S, ch) | set(ch["visited"]):
                self.cov[v] += 1
            pts = np.concatenate([c["z"][::3] for c in self.S.chains])
            self.kd = cKDTree(np.c_[pts.real, pts.imag])
        return dict(contour_nm=total, bsa_in_view=n_view, contour_per_bsa=total / n_view,
                    n_chains=len(self.S.chains))


def _bowed(pieces, rng, min_len=2.5, amp=0.10):
    """Join pieces; bridges longer than min_len get a sin^2 bow of amplitude
    ~amp x length (zero slope at both ends, so tangency is kept)."""
    out = [pieces[0]]
    for a, b in zip(pieces[:-1], pieces[1:]):
        p, q = a[-1], b[0]
        L = abs(q - p)
        if L > min_len:
            t = np.linspace(0, 1, int(L / DS) + 2)[1:-1]
            nrm = 1j * (q - p) / L
            A = rng.normal(0, amp) * L
            A = float(np.clip(A, -0.9, 0.9))
            out.append(p + (q - p) * t + nrm * A * np.sin(np.pi * t) ** 2)
        out.append(b)
    return np.concatenate(out)

def hairpin(z, sep=1.6, dmin=0.85):
    """True if the centre-line comes back within dmin nm of itself after more
    than sep nm of contour without having gone around anything (a fold-back
    the tube cannot make). Self-crossings further along are allowed."""
    zz = z[::2]
    k = int(sep / (2 * DS))
    m = int(6.0 / (2 * DS))
    for i in range(len(zz)):
        j = zz[i + k:i + m]
        if len(j) and np.abs(j - zz[i]).min() < dmin:
            return True
    return False

def smooth_chain(z, sigma=0.35):
    z = line_resample(z, DS)
    if len(z) < 8:
        return z
    zs = gaussian_filter1d(z.real, sigma / DS, mode="nearest") + \
        1j * gaussian_filter1d(z.imag, sigma / DS, mode="nearest")
    zs[0], zs[-1] = z[0], z[-1]
    return zs


# ----------------------------------------------------------------- analysis
def contacts(scene, chain, dmax=None):
    """Proteins touched by a chain: centre-line within c_off + 0.25 nm."""
    dmax = dmax or scene.c_off + 0.25
    z = chain["z"][::2]
    out = set()
    for k, p in enumerate(scene.prots):
        if np.min(np.abs(z - p.c)) > 9:
            continue
        ring = p.out[::2]
        d = np.min(np.abs(z[:, None] - ring[None, :]), axis=1)
        if (d <= dmax).any():
            out.add(k)
    return out

def orientation(scene, polygon):
    """Length-weighted 2D order of chain tangents inside polygon:
    S = <cos 2θ> (θ from the x axis = interface direction; +1 all parallel,
    -1 all normal, 0 isotropic) and |<exp 2iθ>|."""
    num = 0.0; den = 0.0
    for ch in scene.chains:
        z = ch["z"]
        mid = (z[1:] + z[:-1]) / 2
        m = shapely.contains_xy(polygon, mid.real, mid.imag)
        d = np.diff(z)[m]
        L = np.abs(d)
        num = num + (L * np.exp(2j * np.angle(d))).sum()
        den += L.sum()
    if den == 0:
        return dict(S=np.nan, mag=np.nan, L=0.0)
    q = num / den
    return dict(S=float(q.real), mag=float(abs(q)), L=float(den))


# ----------------------------------------------------------------- drawing
def chain_layers(scene, ch, rng, p_front=0.5, short=1.2, link=1.0, min_piece=1.4):
    """Pieces of a chain drawn in front of proteins (2D view of a 3D mesh).
    Overlap runs closer than `link` nm along the chain form one crossing and
    share one decision: a crossing that holds a tucked chain end stays under;
    a short one (< `short` nm, a tight contact) is drawn in front; longer ones
    go over or under at random. Front pieces shorter than `min_piece` nm are
    dropped (the chain then simply passes under)."""
    z = ch["z"]; n = len(z)
    owner = -np.ones(n, int)
    for k, p in enumerate(scene.prots):
        near = np.abs(z - p.c) < 7.0
        if near.any():
            idx = np.where(near)[0]
            ins = shapely.contains_xy(p.poly, z[idx].real, z[idx].imag)
            owner[idx[ins]] = k
    runs = []; i = 0
    while i < n:
        if owner[i] >= 0:
            j = i
            while j + 1 < n and owner[j + 1] == owner[i]:
                j += 1
            runs.append((i, j, owner[i])); i = j + 1
        else:
            i += 1
    clusters = []
    for r in runs:
        if clusters and (r[0] - clusters[-1][-1][1]) * DS < link:
            clusters[-1].append(r)
        else:
            clusters.append([r])
    front = []
    m = int(0.5 / DS)
    for cl in clusters:
        a, b = cl[0][0], cl[-1][1]
        tucked = (a == 0 and ch["ends"][0] == "tuck") or (b == n - 1 and ch["ends"][1] == "tuck")
        if tucked:
            continue
        L = sum(r[1] - r[0] for r in cl) * DS
        f = True if L <= short else bool(rng.random() < p_front)
        if f:
            front.append([max(a - m, 0), min(b + m, n - 1)])
    merged = []
    for p in sorted(front):
        if merged and p[0] <= merged[-1][1] + int(1.0 / DS):
            merged[-1][1] = max(merged[-1][1], p[1])
        else:
            merged.append(p)
    return [p for p in merged if (p[1] - p[0]) * DS >= min_piece]

def draw_scene(ax, scene, rng, width=0.8, clip=None, ppu=None, z0=2.0, outline_pt=None,
               casing_pt=0.28, gid=""):
    """Chains under proteins, proteins, then the over-pieces. clip: patch."""
    ppu = ppu or G.pt_per_unit(ax)
    arts = []
    for k, p in enumerate(scene.prots):
        _, a = G.draw_bsa_geom(ax, p.out, p.seams, style=p.kind, zorder=z0 + 1,
                               ppu=ppu, outline_pt=outline_pt, gid=f"{gid}bsa{k:02d}")
        arts += a
    for i, ch in enumerate(scene.chains):
        zb = z0 + 0.01 * i; zf = z0 + 2 + 0.01 * i
        _, a = G.draw_pdda(ax, ch["z"], width=width, zorder=zb, ppu=ppu, casing_pt=casing_pt,
                           node_spacing=0.25, gid=f"{gid}pdda{i:02d}")
        arts += a
        for q, (a0, a1) in enumerate(chain_layers(scene, ch, rng)):
            _, a = G.draw_pdda(ax, ch["z"][a0:a1 + 1], width=width, zorder=zf, ppu=ppu,
                               casing_pt=casing_pt, capstyle="butt", node_spacing=0.25,
                               gid=f"{gid}pdda{i:02d}_over{q:02d}")
            arts += a
    if clip is not None:
        for a in arts:
            a.set_clip_path(clip)
    return arts

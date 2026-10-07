"""Theoretical maximum capillary pressure of a particle-laden emulsion film vs.
measured critical pressures, on one log-log figure.

Theory (Denkov et al. 1992; Kaptay 2006, single layer, z = 0):
    Pmax = 2 p sigma (cos(theta) + z) / R

Writes pmax_vs_radius.svg (plain stdlib, no plotting library).
Render to PNG with:  node render.js
"""
import math

# ---------------------------------------------------------------- inputs
# Full "reasonable" range (outer band) and a typical range (inner band).
FULL = dict(p=(0.1, 1.0), sigma=(0.020, 0.050), theta=(30.0, 80.0))     # sigma in N/m, theta in deg
TYPICAL = dict(p=(0.2, 0.5), sigma=(0.030, 0.050), theta=(50.0, 70.0))
CENTRE = dict(p=0.3, sigma=0.035, theta=60.0)
Z_BILAYER = 0.633   # Kaptay 2006: close-packed double layer (his sign convention, theta > 90 deg)

# Measured critical pressures. Radius ranges are the plausible particle sizes
# for that system, NOT a reported single radius (see README).
MEASURED = [
    dict(label="Silica, decane/water, centrifuge", sub="Kruglyakov et al. (100 kPa)",
         P=1.0e5, R=(6e-9, 270e-9), color="#eb6834", theory=4.0e5,
         theory_label="their calculated Pc,max (~4×)"),
    dict(label="Carbon black 0.015 wt%, 0.6 M NaCl: 4.6 kPa", sub=None,
         P=4.6e3, R=(10e-9, 150e-9), color="#1baf7a"),
    dict(label="Carbon black 0.015 wt%, pH 3.3, no salt: 2.2 kPa", sub=None,
         P=2.2e3, R=(10e-9, 150e-9), color="#1baf7a"),
]


def pmax(p, sigma, theta_deg, R, z=0.0):
    return 2 * p * sigma * (math.cos(math.radians(theta_deg)) + z) / R


def envelope(rng, R, z=0.0):
    lo = pmax(rng["p"][0], rng["sigma"][0], rng["theta"][1], R, z)   # cos is smallest at max theta
    hi = pmax(rng["p"][1], rng["sigma"][1], rng["theta"][0], R, z)
    return lo, hi


# ---------------------------------------------------------------- layout
W, H = 1200, 780
ML, MR, MT, MB = 110, 40, 120, 90
X0, X1 = math.log10(5e-9), math.log10(1e-5)
Y0, Y1 = 1.0, 8.0

INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a8984"
GRID, SURF = "#e6e5e1", "#fcfcfb"
BLUE, BLUE_IN, BLUE_LINE = "#b7d3f6", "#6da7ec", "#184f95"


def sx(R):
    return ML + (math.log10(R) - X0) / (X1 - X0) * (W - ML - MR)


def sy(P):
    return MT + (Y1 - math.log10(P)) / (Y1 - Y0) * (H - MT - MB)


def path_band(rng, z=0.0, n=60):
    Rs = [10 ** (X0 + (X1 - X0) * i / n) for i in range(n + 1)]
    top = [(sx(R), sy(envelope(rng, R, z)[1])) for R in Rs]
    bot = [(sx(R), sy(envelope(rng, R, z)[0])) for R in reversed(Rs)]
    pts = top + bot
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"


out = []
a = out.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
  f'font-family="Inter, Helvetica, Arial, sans-serif">')
a(f'<rect width="{W}" height="{H}" fill="{SURF}"/>')
a(f'<defs><clipPath id="plot"><rect x="{ML}" y="{MT}" width="{W-ML-MR}" height="{H-MT-MB}"/></clipPath></defs>')

# title
a(f'<text x="{ML}" y="42" font-size="24" font-weight="600" fill="{INK}">'
  'Maximum capillary pressure of a particle-laden film vs. particle radius</text>')
a(f'<text x="{ML}" y="70" font-size="15" fill="{INK2}">'
  'Theory: P<tspan baseline-shift="sub" font-size="11">max</tspan> = 2pσ cosθ / R '
  '(Denkov 1992; Kaptay 2006, single layer). Points: critical pressures measured by centrifugation.</text>')

# grid + ticks
for d in range(int(Y0), int(Y1) + 1):
    y = sy(10 ** d)
    a(f'<line x1="{ML}" x2="{W-MR}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
    lab = {1: "10 Pa", 2: "100 Pa", 3: "1 kPa", 4: "10 kPa", 5: "100 kPa", 6: "1 MPa", 7: "10 MPa", 8: "100 MPa"}[d]
    a(f'<text x="{ML-12}" y="{y+5:.1f}" font-size="14" text-anchor="end" fill="{INK2}">{lab}</text>')
for R, lab in [(1e-8, "10 nm"), (1e-7, "100 nm"), (1e-6, "1 µm"), (1e-5, "10 µm")]:
    x = sx(R)
    a(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{MT}" y2="{H-MB}" stroke="{GRID}" stroke-width="1"/>')
    a(f'<text x="{x:.1f}" y="{H-MB+24}" font-size="14" text-anchor="middle" fill="{INK2}">{lab}</text>')
a(f'<line x1="{ML}" x2="{W-MR}" y1="{H-MB}" y2="{H-MB}" stroke="{MUTED}" stroke-width="1"/>')
a(f'<text x="{(ML+W-MR)/2:.0f}" y="{H-28}" font-size="15" text-anchor="middle" fill="{INK}">Particle radius R</text>')
a(f'<text transform="translate(30,{(MT+H-MB)/2:.0f}) rotate(-90)" font-size="15" text-anchor="middle" fill="{INK}">'
  'Pressure (Pa)</text>')

# theory bands
a('<g clip-path="url(#plot)">')
a(f'<path d="{path_band(FULL)}" fill="{BLUE}" fill-opacity="0.55"/>')
a(f'<path d="{path_band(TYPICAL)}" fill="{BLUE_IN}" fill-opacity="0.55"/>')
Rs = [10 ** (X0 + (X1 - X0) * i / 60) for i in range(61)]
line = " L".join(f"{sx(R):.1f},{sy(pmax(CENTRE['p'], CENTRE['sigma'], CENTRE['theta'], R)):.1f}" for R in Rs)
a(f'<path d="M{line}" fill="none" stroke="{BLUE_LINE}" stroke-width="2"/>')
a('</g>')

# label on the centre line
Rl = 4.0e-6
xl, yl = sx(Rl), sy(pmax(CENTRE['p'], CENTRE['sigma'], CENTRE['theta'], Rl))
ang = math.degrees(math.atan(((H - MT - MB) / (Y1 - Y0)) / ((W - ML - MR) / (X1 - X0))))
a(f'<text x="{xl:.1f}" y="{yl-10:.1f}" font-size="13" fill="{INK}" text-anchor="middle" '
  f'transform="rotate({ang:.1f} {xl:.1f} {yl:.1f})">p = 0.3, σ = 35 mN/m, θ = 60°</text>')

# measured values: horizontal bar over plausible radius range + centre marker
for i, m in enumerate(MEASURED):
    y = sy(m["P"])
    x_lo, x_hi = sx(m["R"][0]), sx(m["R"][1])
    xc = sx(math.sqrt(m["R"][0] * m["R"][1]))
    a(f'<line x1="{x_lo:.1f}" x2="{x_hi:.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{m["color"]}" '
      f'stroke-width="2" stroke-dasharray="6 4"/>')
    for xe in (x_lo, x_hi):
        a(f'<line x1="{xe:.1f}" x2="{xe:.1f}" y1="{y-6:.1f}" y2="{y+6:.1f}" stroke="{m["color"]}" stroke-width="2"/>')
    a(f'<circle cx="{xc:.1f}" cy="{y:.1f}" r="7" fill="{m["color"]}" stroke="{SURF}" stroke-width="2"/>')
    if "theory" in m:
        yt = sy(m["theory"])
        a(f'<line x1="{xc:.1f}" x2="{xc:.1f}" y1="{yt+7:.1f}" y2="{y-8:.1f}" stroke="{m["color"]}" stroke-width="1.5"/>')
        a(f'<circle cx="{xc:.1f}" cy="{yt:.1f}" r="7" fill="{SURF}" stroke="{m["color"]}" stroke-width="2"/>')
        a(f'<text x="{xc+14:.1f}" y="{yt+5:.1f}" font-size="13" fill="{INK2}">{m["theory_label"]}</text>')
    if m["sub"]:
        a(f'<text x="{x_hi+10:.1f}" y="{y-2:.1f}" font-size="14" fill="{INK}">{m["label"]}</text>')
        a(f'<text x="{x_hi+10:.1f}" y="{y+15:.1f}" font-size="12.5" fill="{INK2}">{m["sub"]}</text>')
    else:
        a(f'<text x="{x_hi+10:.1f}" y="{y+5:.1f}" font-size="14" fill="{INK}">{m["label"]}</text>')

# legend (top)
lx, ly = ML, 96
a(f'<rect x="{lx}" y="{ly-11}" width="22" height="14" rx="2" fill="{BLUE}"/>')
a(f'<text x="{lx+30}" y="{ly+1}" font-size="13" fill="{INK}">Theory, full range: p 0.1–1, σ 20–50 mN/m, θ 30–80°</text>')
lx2 = lx + 410
a(f'<rect x="{lx2}" y="{ly-11}" width="22" height="14" rx="2" fill="{BLUE_IN}"/>')
a(f'<text x="{lx2+30}" y="{ly+1}" font-size="13" fill="{INK}">Typical: p 0.2–0.5, σ 30–50, θ 50–70°</text>')
lx3 = lx2 + 300
a(f'<circle cx="{lx3+8}" cy="{ly-4}" r="6" fill="{INK2}"/>')
a(f'<line x1="{lx3+22}" x2="{lx3+50}" y1="{ly-4}" y2="{ly-4}" stroke="{INK2}" stroke-width="2" stroke-dasharray="6 4"/>')
a(f'<text x="{lx3+58}" y="{ly+1}" font-size="13" fill="{INK}">Measured; dashes = plausible R range</text>')

a('</svg>')

with open(__file__.replace("pmax_figure.py", "pmax_vs_radius.svg"), "w") as f:
    f.write("\n".join(out))

# console table of theory at a few radii
print(f"{'R':>8} | {'full lo':>9} {'full hi':>9} | {'typ lo':>9} {'typ hi':>9} | {'centre':>9}  (Pa)")
for R in (10e-9, 50e-9, 100e-9, 500e-9, 1e-6, 5e-6):
    fl, fh = envelope(FULL, R)
    tl, th = envelope(TYPICAL, R)
    c = pmax(CENTRE['p'], CENTRE['sigma'], CENTRE['theta'], R)
    print(f"{R*1e9:6.0f}nm | {fl:9.3g} {fh:9.3g} | {tl:9.3g} {th:9.3g} | {c:9.3g}")
print(f"bilayer factor (cos60+0.633)/cos60 = {(0.5+Z_BILAYER)/0.5:.2f}")

"""Generate the expected (simulated) data behind Figure 2. Every curve comes from an explicit, stated model;
anchors are taken from the deck where possible. Outputs are CSVs in data/simulated/. These are predictions
to design experiments against, not results."""
import os

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import curve_fit

import common as c

rng = np.random.default_rng(2026)
os.makedirs(c.SIM, exist_ok=True)


def write(name, header, rows, note):
    with open(os.path.join(c.SIM, name), "w") as fh:
        fh.write(f"# {note}\n")
        fh.write(",".join(header) + "\n")
        for r in rows:
            fh.write(",".join(f"{v:.6g}" if isinstance(v, (float, np.floating)) else str(v) for v in r) + "\n")


# ---------------------------------------------------------------- a: hypothesis x manipulation matrix
H = ["H1", "H2", "H3", "H4", "H5"]
M = [  # manipulation, predicted response per hypothesis (v down, ^ up, D altered, o unchanged)
    ("No plastic (ROS probe only)", "v o v o o"),
    ("O$_2$ only; no N$_2$ (same pO$_2$)", "o o o v o"),
    ("Dark instead of light", "v o o v o"),
    ("Reversed-potential salt", "o D o o o"),
    ("D$_2$O instead of H$_2$O", "^ o o ^ o"),
    ("•OH scavenger (TBA)", "o v v o v"),
    ("Glass instead of PFA vial", "o o o o v"),
]
write("hypothesis_matrix.csv", ["manipulation"] + H, [(m, *s.split()) for m, s in M],
      "Predicted response of ROS yield / PS oxidation rate in ice. H1 polymer photosensitizer (Tian 2022); "
      "H2 freezing potential (Song 2024); H3 plastic-water interface OH (Qian 2026); H4 freeze-exsolved "
      "nanobubbles, light-driven as drawn in the deck; H5 contact electrification with vial/particles.")

# ---------------------------------------------------------------- b: buoyant-mass sign test (Archimedes)
RHO_W = 1000.0                     # kg m-3
m = np.linspace(-4.5, 3.0, 751)    # buoyant mass, fg


def lognorm_pdf(x, med, s):
    out = np.zeros_like(x)
    p = x > 0
    out[p] = np.exp(-(np.log(x[p] / med)) ** 2 / (2 * s ** 2)) / (x[p] * s * np.sqrt(2 * np.pi))
    return out


vol = lambda d_nm: np.pi / 6 * (d_nm * 1e-9) ** 3                    # m3
fg = 1e18                                                              # kg -> fg
mb_bub = -RHO_W * vol(130) * fg                                        # -1.15 fg for a 130 nm air bubble
mb_frag = (1080 - RHO_W) * vol(300) * fg                               # +1.13 fg, oxidized PS fragment 300 nm
s_bub, s_frag = 3 * 0.25, 3 * 0.30                                     # sigma of ln(d) x 3 -> sigma of ln(m)
n_bub, n_frag = 3.0, 0.5                                               # 1e8 per mL (bubble count from deck)
bub = n_bub * lognorm_pdf(-m, -mb_bub, s_bub)
frag = n_frag * lognorm_pdf(m, mb_frag, s_frag)
write("buoyant_mass.csv", ["mb_fg", "melted_ice", "after_pressure"],
      zip(m, bub + frag, 0.03 * bub + frag),
      f"Expected buoyant-mass spectra (1e8 mL-1 fg-1). Air bubble 130 nm -> {mb_bub:.2f} fg; oxidized PS "
      f"fragment 300 nm (rho 1080) -> {mb_frag:.2f} fg. Pressure pulse (0.5 MPa) removes 97% of bubbles.")

# ---------------------------------------------------------------- c: oxidation vs nanobubble density at fixed pO2
R_AIR = 0.28          # initial dO/C per 100 h, 500 nm PS in air-saturated ice (deck p3 D)
N_AIR = 3.0           # 1e8 per mL (deck p2 B)
conds = [("1 MPa freeze", 0.3), ("O$_2$ only", 0.8), ("Air", 3.0), ("O$_2$+Ar", 4.5)]
rows = []
for lab, n in conds:
    nx = n * rng.lognormal(0, 0.10, 3)
    r = R_AIR * nx / N_AIR * rng.lognormal(0, 0.08, 3)
    rows.append((lab, nx.mean(), nx.std(ddof=1), r.mean(), r.std(ddof=1)))
write("dose_response.csv", ["condition", "nb_mean", "nb_sd", "rate_mean", "rate_sd"], rows,
      "Simulated n=3 per condition under H4 (rate proportional to bubble density at fixed pO2=0.21 bar). "
      f"Rival hypotheses predict a flat rate = {R_AIR} per 100 h.")

# ---------------------------------------------------------------- d: grain-size decoupling
BETA = 0.61                         # bubble density ~ d^-0.61 (deck p4 E, log-log fit)
SV_REF = 2 / 0.065                  # mm-1, pristine PS ice (d = 65 um, deck p4 D)
grain_med = lambda sv: R_AIR * (sv / SV_REF) ** BETA
rows = []
for series, d_um in [("anneal", [200, 120, 65, 40, 25]), ("spectator", [45, 30, 22])]:
    for d in d_um:
        sv = 2 / (d / 1000)
        r = grain_med(sv) * rng.lognormal(0, 0.08, 3)
        rows.append((series, sv, r.mean(), r.std(ddof=1)))
write("decoupling.csv", ["series", "sv_mm", "rate_mean", "rate_sd"], rows,
      "Expected initial oxidation rate of fresh h-PS vs grain-boundary density Sv=2/d. Grain size set by "
      "thermal annealing (no additive) or by pre-oxidized, hydroperoxide-reduced PS-d8 spectators. "
      "Grain-mediated feedback: both collapse on rate = R_air (Sv/Sv_ref)^0.61.")
sv = np.linspace(5, 105, 101)
write("decoupling_model.csv", ["sv_mm", "grain_mediated", "rooh_driven"],
      zip(sv, grain_med(sv), 1.5 * grain_med(sv)),
      "Model lines: grain-mediated feedback, and chemical autocatalysis (spectators carry ROOH: 1.5x).")

# ---------------------------------------------------------------- e: ratchet test across freeze-thaw cycles
g = c.deck("grain_vs_oc.csv")
dfun = lambda th, dinf, d0, lam: dinf + (d0 - dinf) * np.exp(-th / lam)
popt, _ = curve_fit(dfun, g["oc"], g["grain_um"], p0=(15, 65, 0.1), bounds=([5, 40, 0.01], [40, 90, 1.0]))
TH_MAX, TAU, T_FROZEN = 0.25, 100.0, 72.0   # tau, k0 reproduce deck p4 G cycle 0 (0.065 at 72 h, plateau 0.118)


def run(scenario, n_cycles=10, k=None):
    d0 = dfun(0, *popt)
    def nb(th):
        if scenario == "feedback":
            return (d0 / dfun(th, *popt)) ** BETA
        if scenario == "passivation":
            return 1 - 0.75 * th / TH_MAX
        return 1.0
    th, ks = 0.0, []
    for _ in range(n_cycles):
        sol = solve_ivp(lambda t, y: [k * nb(y[0]) * (1 - y[0] / TH_MAX) * np.exp(-t / TAU)],
                        (0, T_FROZEN), [th], rtol=1e-8)
        new = sol.y[0, -1]
        expo = TAU * (1 - np.exp(-T_FROZEN / TAU))
        ks.append(-TH_MAX * np.log((TH_MAX - new) / (TH_MAX - th)) / expo)   # exact inversion if nb const
        th = new
        if scenario == "replenish" and len(ks) == 1:
            print(f"cycle-1 O/C (replenish) = {th:.3f}")
    return np.array(ks) / ks[0]


k0 = 0.0016  # per h
cyc = np.arange(1, 11)
lines = {s: run(s, k=k0) for s in ("feedback", "replenish", "passivation")}
rep = np.array([lines["feedback"] * rng.lognormal(0, 0.06, len(cyc)) for _ in range(3)])
write("ratchet.csv", ["cycle", "feedback", "replenish", "passivation", "sim_mean", "sim_sd"],
      zip(cyc, lines["feedback"], lines["replenish"], lines["passivation"], rep.mean(0), rep.std(0, ddof=1)),
      f"Per-cycle rate constant k_n/k_1 = rate normalized to remaining sites. 72 h frozen per cycle, oxidant "
      f"pool decay tau={TAU} h reset at each refreeze, theta_max={TH_MAX}. Feedback: bubbles ~ d(theta)^-0.61 "
      f"with d(theta) fitted to deck p4 D (d_inf={popt[0]:.1f}, d0={popt[1]:.1f} um, lambda={popt[2]:.3f}). "
      "Simulated points: feedback scenario, n=3.")

# ---------------------------------------------------------------- f: Zener pinning bound
f = np.geomspace(1e-9, 1e-1, 200)
write("zener.csv", ["f", "d_um_r0.25", "d_um_r5"], zip(f, 4 * 0.25 / (3 * f), 4 * 5.0 / (3 * f)),
      "Zener-limited grain size d = 4r/(3f) for particle radius r = 0.25 um (500 nm PS) and 5 um (10 um MPs).")
write("zener_bands.csv", ["band", "lo", "hi"],
      [("natural", 1e-9, 1e-7), ("lab", 1e-5, 1e-3), ("deck_grain_um", 20, 200)],
      "Natural ice/snow: <=~5e-8 even for the most contaminated Arctic sea ice (1.2e4 particles/L, ~20 um). "
      "Typical lab dosing 10-1000 mg/L PS. Deck grain sizes 20-200 um.")

# ---------------------------------------------------------------- g: 13C carbon budget
ftc = np.linspace(0, 120, 121)
pools = {"np": 4.0 * (1 - np.exp(-ftc / 60)), "doc": 1.5 * (1 - np.exp(-ftc / 80)),
         "co2": 0.002 * ftc, "water": 0.05 * (1 - np.exp(-ftc / 30))}
write("carbon_budget_model.csv", ["ftc"] + list(pools), zip(ftc, *pools.values()),
      "Illustrative magnitudes (% of added 13C-PS). Hypothesis encoded: fragmentation and DOC release dominate, "
      "mineralization stays <0.5%. Water control: all mobile pools combined.")
pts = [0, 15, 30, 60, 90, 120]
rows = []
for n in pts:
    i = int(n)
    rows.append((n, *[pools[k][i] * rng.lognormal(0, 0.10) for k in ("np", "doc", "co2")]))
write("carbon_budget_points.csv", ["ftc", "np", "doc", "co2"], rows, "Simulated sampling points, n=1 each.")

# ---------------------------------------------------------------- i: field FTC dose-response
stations = {"low": 25, "mid": 110, "high": 40}           # season-total FTC at each station (expected)
ps = lambda n: 0.20 * (1 - np.exp(-n / 50))
pe = lambda n: 0.05 * (1 - np.exp(-n / 70))
ctl = lambda n: 0.005 + 0 * n
rows = []
for st, ntot in stations.items():
    for frac in (1 / 3, 2 / 3, 1):
        n = ntot * frac
        for trt, fun in (("ps_ftc", ps), ("pe_ftc", pe), ("ps_unfrozen", ctl)):
            v = fun(n) + rng.normal(0, 0.006)
            rows.append((st, trt, n, max(v, 0.0)))
write("field_points.csv", ["station", "treatment", "ftc", "d_oc"], rows,
      "Expected season retrievals (1/3, 2/3, end) of dark cassettes. Unfrozen control is paired with each "
      "station and plotted at that station's FTC count. If FTC count (not elevation or UV) drives oxidation, "
      "all stations collapse on one curve.")
n = np.linspace(0, 120, 121)
write("field_model.csv", ["ftc", "ps_ftc", "pe_ftc", "ps_unfrozen"], zip(n, ps(n), pe(n), ctl(n)),
      "Model curves: dO/C = a(1-exp(-n/n0)); PS a=0.20, n0=50; PE a=0.05, n0=70; unfrozen control flat.")

# ---------------------------------------------------------------- j: meltwater first flush
F = np.linspace(0, 1, 101)
pulse = lambda tau: np.exp(-F / tau) / (tau * (1 - np.exp(-1 / tau)))
curves = {"chloride": pulse(0.30), "products": pulse(0.33), "nanoplastics": pulse(0.60), "microplastics": 3 * F ** 2}
write("meltwater_model.csv", ["F"] + list(curves), zip(F, *curves.values()),
      "Concentration factor C/Cmean vs fraction of snowpack melted. Grain-boundary solutes elute first "
      "(ionic pulse, tau=0.30); oxidized products expected to track chloride; nanoplastics partly retained "
      "(tau=0.60); intact MPs filtered by the snowpack and released late (3F^2). Each integrates to 1.")
Fp = np.arange(0.05, 1.0, 0.1)
write("meltwater_points.csv", ["F", "products"],
      zip(Fp, np.exp(-Fp / 0.33) / (0.33 * (1 - np.exp(-1 / 0.33))) * rng.lognormal(0, 0.10, len(Fp))),
      "Simulated lysimeter fractions for oxidized products (DOC from 13C-PS), n=1 per fraction.")
print("simulated datasets written to", c.SIM)

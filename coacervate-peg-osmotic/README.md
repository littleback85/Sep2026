# PDDA/BSA coacervate under PEG osmotic stress: osmotic modulus

`analysis.py` holds the inputs, the fits and the figure. `results.md` has the full tables.
Re-run with `python3 analysis.py`.

![figure](coacervate_osmotic_modulus.png)

## Method

The layer can only change height, so V/V0 = h/h0. At equilibrium the PEG pressure Π equals the coacervate's own osmotic pressure. The osmotic modulus is therefore

K = c ∂Π/∂c = dΠ/dε, with ε = −ln(h/h0).

- Heights are the 80 h values for each sample, digitised from the per-sample panels. The group means match panel A to within 0.002.
- The primary fit regresses ε on Π (Π is set, ε is measured) and inverts the slope. Fitting Π on the group means, as the original panel did, gives 1.39 MPa, which this script reproduces.
- **20% sample 2 is excluded.** Its h/h0 of 0.88 is less compressed than any 15% sample.
- **Π(20%) is extrapolated** (0.77 MPa) from a Rand-type fit through the 5/10/15% values. Set `PI_20_OVERRIDE` if you have a calibrated value.

## Results

| Fit | n | K (MPa) | 95% CI |
|---|---|---|---|
| 0–15% PEG | 12 | **1.45 ± 0.14** | 1.13–1.76 |
| 0–20% PEG, 20% sample 2 excluded | 14 | **0.85 ± 0.07** | 0.68–1.01 |

Step moduli between neighbouring concentrations are 0.97, 1.03, 2.12 and then **0.51** MPa (15→20%). Up to 15% the coacervate stiffens as it is compressed, which is normal for a concentrated polymer or protein fluid. From 15% to 20% it suddenly softens: h/h0 drops to 0.38. That drop does not fit the 0–15% equation of state. It points either to a densification or phase change, or to an artifact where the height no longer reports volume (persistent wall climbing). The 20% data should not be used for a single modulus.

## How compressible is ~1 MPa?

- **Not incompressible in the mechanical sense.** Liquid water has a bulk modulus of 2.2 GPa, about 1500× higher. The ~1 MPa here is an *osmotic* modulus: the coacervate gives up water against a reservoir.
- **About as stiff as the PEG solution compressing it.** A 15% PEG solution has K ≈ 0.9 MPa by the same Π(w) curve, and a 20% solution about 1.7 MPa.
- **Comparable to a very concentrated BSA solution.** A hard-sphere estimate gives K ≈ 0.2–0.4 MPa at 300 g/L and 0.7–2.4 MPa at 400 g/L. At 100–200 g/L the estimate is only 0.01–0.08 MPa.

The coacervate therefore behaves like a dense protein/polyelectrolyte fluid at roughly 350–400 g/L protein-equivalent crowding. It is osmotically stiff compared with dilute or moderately concentrated protein solutions, but it is far from incompressible.

## Caveats

- The PEG pressures are nominal. Partial PEG uptake into the coacervate, or salt redistribution, would lower the effective Π.
- At 15% the layer rebounds slightly between 32 h and 80 h. Using the minimum height instead of the 80 h value would lower the 15% secant modulus by about 8%.
- The BSA curve is a model estimate (Carnahan–Starling, effective specific volume 1.2–1.5 mL/g), not measured data. Replace it with measured Π(c) for your buffer if you need a quantitative comparison.

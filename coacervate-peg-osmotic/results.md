# Osmotic modulus of the PDDA/BSA coacervate under PEG stress

## Inputs (h/h0 at 80 h, digitised)

| PEG | Pi (MPa) | sample 1 | sample 2 | sample 3 | mean eps = -ln(h/h0) | SD |
|---|---|---|---|---|---|---|
| 0% | 0.000 | 1.017 | 1.010 | 1.018 | -0.015 | 0.004 |
| 5% | 0.052 | 1.005 | 0.924 | 0.958 | 0.039 | 0.042 |
| 10% | 0.181 | 0.889 | 0.831 | 0.826 | 0.165 | 0.041 |
| 15% | 0.412 | 0.763 | 0.740 | 0.780 | 0.273 | 0.026 |
| 20% | 0.769 (extrapolated) | 0.367 | ~~0.882~~ (excluded) | 0.385 | 0.978 | 0.034 |

Pi(20%) extrapolation: Rand form log10 Pi = -4.75 + 2.47 w^0.21 gives 0.77 MPa; a pure power law (Pi ~ w^1.87) gives 0.69 MPa.

## Osmotic modulus K = dPi/d(-ln h)

| Data set | n | K (MPa), eps-on-Pi fit | 95% CI | R² | K, Pi-on-eps on means (original method) |
|---|---|---|---|---|---|
| 0-15% PEG | 12 | **1.45** ± 0.14 | 1.13 to 1.76 | 0.91 | 1.39 (R² 0.96) |
| 0-20% PEG (20% sample 2 excluded) | 14 | **0.85** ± 0.07 | 0.68 to 1.01 | 0.91 | 0.76 (R² 0.94) |

## Local (step) moduli between neighbouring concentrations

| Step | dPi (MPa) | d eps | K_step (MPa) |
|---|---|---|---|
| 0% to 5% | 0.052 | 0.054 | 0.97 |
| 5% to 10% | 0.129 | 0.126 | 1.03 |
| 10% to 15% | 0.231 | 0.109 | 2.12 |
| 15% to 20% | 0.357 | 0.705 | 0.51 |

## Reference osmotic moduli (MPa)

| System | K_osm (MPa) |
|---|---|
| PEG solution 5% (from the same Pi(w) curve) | 0.09 |
| PEG solution 10% (from the same Pi(w) curve) | 0.35 |
| PEG solution 15% (from the same Pi(w) curve) | 0.87 |
| PEG solution 20% (from the same Pi(w) curve) | 1.72 |
| BSA 100 g/L, hard-sphere (phi_eff 0.12-0.15; Pi 0.006-0.007 MPa) | 0.01 to 0.01 |
| BSA 200 g/L, hard-sphere (phi_eff 0.24-0.30; Pi 0.022-0.030 MPa) | 0.05 to 0.08 |
| BSA 300 g/L, hard-sphere (phi_eff 0.36-0.45; Pi 0.062-0.105 MPa) | 0.19 to 0.40 |
| BSA 400 g/L, hard-sphere (phi_eff 0.48-0.60; Pi 0.170-0.407 MPa) | 0.71 to 2.39 |
| Liquid water, bulk modulus | 2200 |

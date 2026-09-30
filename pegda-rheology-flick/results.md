# PEGDA rheology -> load-bearing strands -> comparison with FLICK

Constants: rho = 1.12 g/cm3, T = 298.15 K (rho*RT = 2.776 MPa kg/mol), <R0^2>/M(PEO, theta) = 0.805 A^2 mol/g, PEG/water Rg = 0.0215 M^0.583 nm.

## 1. Fits of G'(Q)

| Mn | a = G'(Q=1) from G=a/Q (Pa) | R^2 | free exponent b in G=aQ^b |
|---|---|---|---|
| 5000 | 160,639 ± 9,997 | 0.883 | -1.29 ± 0.24 |
| 10000 | 92,810 ± 4,051 | 0.964 | -1.23 ± 0.04 |
| 20000 | 65,975 ± 8,422 | 0.630 | -0.69 ± 0.29 |

## 2. Effective (load-bearing) strands

| Mn | nu_e dry (mol/m3) | Mc,eff affine (g/mol) | Mc,eff phantom f=4 | Mc/Mn affine | Mc/Mn phantom | load-bearing fraction omega (aff / ph4) | per-sample Mc,aff (g/mol) |
|---|---|---|---|---|---|---|---|
| 5000 | 64.8 | 17,283 ± 1,076 | 8,641 | 3.46 | 1.73 | 0.29 / 0.58 | 16,295, 16,841, 16,893, 23,241 |
| 10000 | 37.4 | 29,913 ± 1,306 | 14,957 | 2.99 | 1.50 | 0.33 / 0.67 | 28,167, 31,220, 31,757, 35,905 |
| 20000 | 26.6 | 42,081 ± 5,372 | 21,040 | 2.10 | 1.05 | 0.48 / 0.95 | 49,680, 31,524, 32,657, 49,607 |

## 3. Length scales (nm)

| Mn | precursor Re theta / water | eff. strand R0 theta (aff; ph4) | eff. strand Re water (aff) | mesh xi=(kT/G)^1/3 range | Canal-Peppas xi range |
|---|---|---|---|---|---|
| 5000 | 6.34 / 7.55 | 11.80; 8.34 | 15.56 | 6.5-8.8 | 26.5-32.1 |
| 10000 | 8.97 / 11.31 | 15.52; 10.97 | 21.43 | 7.8-11.2 | 34.8-46.2 |
| 20000 | 12.69 / 16.94 | 18.41; 13.01 | 26.14 | 9.4-14.0 | 41.3-61.6 |

## 4. Junction fluctuations: phantom prediction vs FLICK (per-axis sigma, nm)

| Mn | phantom f=3 (theta / water) | phantom f=4 (theta / water) | phantom f=10 | affine | FLICK sigma | H = (sigma_FLICK/sigma_ph4)^2 theta / water / FLICK-as-3D | strand mass FLICK implies, f=3 / f=4 (g/mol) |
|---|---|---|---|---|---|---|---|
| 5000 | 3.21 / 4.24 | 2.95 / 3.89 | 2.04 | 0 | 12.58 | 18.2 / 10.5 / 6.1 | 88,466 / 157,273 |
| 10000 | 4.22 / 5.83 | 3.88 / 5.36 | 2.69 | 0 | 14.73 | 14.4 / 7.6 / 4.8 | 121,289 / 215,625 |
| 20000 | 5.01 / 7.12 | 4.60 / 6.54 | 3.19 | 0 | 16.09 | 12.2 / 6.1 / 4.1 | 144,720 / 257,280 |

FLICK variance decomposition: sigma^2 = sigma0^2 + alpha*Mc,eff  ->  sigma0 = 9.51 nm, alpha = 4.06e-3 nm^2 mol/g, R^2 = 0.9927  (vs Mn instead: R^2 = 0.9203).
Phantom-theory slopes (theta strands): f=3: 0.60e-3, f=4: 0.50e-3, f=10: 0.24e-3  -> measured/phantom(f=3) = 6.8x (1-D), 2.3x if sigma is 3-D rms.

Scaling with Mn: Mc,eff ~ Mn^0.64; R0(Mc,eff) ~ Mn^0.32; median xi_G ~ Mn^0.22; FLICK sigma ~ Mn^0.18; precursor Re ~ Mn^0.50 (theta) / Mn^0.58 (water).

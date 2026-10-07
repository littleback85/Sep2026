# Osmotic modulus of the PDDA/BSA coacervate under PEG stress

## Inputs (h/h0 at 80 h, digitised; 0–15% PEG)

| PEG | Π (MPa) | sample 1 | sample 2 | sample 3 | mean ε = −ln(h/h0) | SD |
|---|---|---|---|---|---|---|
| 0% | 0.000 | 1.012 | 1.012 | 1.021 | -0.015 | 0.005 |
| 5% | 0.052 | 1.003 | 0.923 | 0.959 | 0.040 | 0.042 |
| 10% | 0.181 | 0.890 | 0.828 | 0.826 | 0.165 | 0.042 |
| 15% | 0.412 | 0.764 | 0.738 | 0.779 | 0.274 | 0.027 |

## Fits (n = 12 samples, strain regressed on Π)

| Model | K (MPa) | 95% CI | R² or note |
|---|---|---|---|
| Linear in log strain, Π = K(ε − ε₀) | **1.44** ± 0.14 | 1.13–1.76 | R² 0.91 |
| Linear in engineering strain, Π = K(1 − h/h₀ − e₀) | 1.65 ± 0.18 | 1.26–2.04 | R² 0.90 |
| Stiffening EOS, K = K₀ + αΠ | K₀ = 0.67 ± 0.25, α = 4.5 ± 2.0 | K(15%) = 2.51 | ΔAICc vs linear = -1.8 |
| Π on ε, group means (original panel) | 1.39 | – | – |

Step moduli between neighbouring group means: 0→5% 0.95 MPa, 5→10% 1.03 MPa, 10→15% 2.12 MPa.

## Benchmarks (MPa)

| Group | System | K or G (MPa) | Type |
|---|---|---|---|
| This work | PDDA/BSA coacervate | 1.13–1.76 | osmotic/compressive |
| PEG bath | PEG 5% | 0.087 | osmotic/compressive |
| PEG bath | PEG 10% | 0.351 | osmotic/compressive |
| PEG bath | PEG 15% | 0.868 | osmotic/compressive |
| Protein | BSA 200 g/L | 0.0479–0.0765 | osmotic/compressive |
| Protein | BSA 300 g/L | 0.186–0.402 | osmotic/compressive |
| Protein | BSA 400 g/L | 0.705–2.39 | osmotic/compressive |
| Salt | 150 mM NaCl | 0.692–0.744 | osmotic/compressive |
| Biological | Cell (osmometer) | 0.899–1.2 | osmotic/compressive |
| Biological | Articular cartilage | 0.08–2.1 | osmotic/compressive |
| Gels | Synthetic gels | 0.001–0.1 | osmotic/compressive |
| Gels | PEGDA gels G′ (this lab) | 0.0015–0.015 | shear |
| Coacervate | Complex coacervate G′ | 0.0001–0.01 | shear |

20% PEG (SI only): Π extrapolated to 0.77 MPa; h/h0(80 h) = 0.367, 0.882, 0.385 (sample 2 excluded).

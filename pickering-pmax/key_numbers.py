"""Key numbers quoted in the report (writes key_numbers.md)."""
import numpy as np
import pore_model as pm
out = []
P = lambda s: out.append(s)
P("| θ (°) | mono, close packed | bilayer, close packed | mono, vacancy | bilayer, coincident vacancy | bilayer, one-layer vacancy |")
P("|---|---|---|---|---|---|")
for t in [30, 50, 60, 70, 80, 85, 89]:
    th = np.radians(t)
    v = [pm.phat_bridge(pm.L_HEX, th), pm.phat_bilayer(pm.L_HEX, pm.L_HEX, th),
         pm.phat_bridge(2.0, th), pm.phat_bilayer(2.0, 2.0, th), pm.phat_bilayer(2.0, pm.L_HEX, th)]
    P(f"| {t} | " + " | ".join(f"{x:.3f}" for x in v) + " |")
P("")
th = np.radians(70); g = 0.030
P("Absolute values, γ = 30 mN/m, θ = 70°")
for R in [10e-9, 100e-9, 0.5e-6, 1e-6, 5e-6]:
    sc = 2 * g / R / 1e3
    P(f"R = {R*1e9:.0f} nm: mono hex {pm.phat_bridge(pm.L_HEX, th)*sc:.3g} kPa, bilayer hex {pm.phat_bilayer(pm.L_HEX, pm.L_HEX, th)*sc:.3g} kPa, "
      f"mono vacancy {pm.phat_bridge(2.0, th)*sc:.3g} kPa, mono h=3R {pm.phat_bridge(4.0, th)*sc:.3g} kPa")
P("")
P("Stretched bond, θ-independent ratio (16-d^2)/(3d^2):")
for s in [0.1, 0.2, 0.4, 0.6, 0.8]:
    d = 2 + s
    P(f"s = {s}R: h = {pm.L_stretched_bond(d)-1:.3f}R, ratio {(16-d*d)/(3*d*d):.3f}")
P("Uniform lattice spacing:")
for r in [1.0, 1.05, 1.1, 1.2, 1.4]:
    d = 2 * r
    P(f"d/2R = {r}: coverage {0.9069/r**2:.3f}, mono {pm.phat_bridge_exact(pm.L_uniform(d), th):.3f}, bilayer {pm.phat_bilayer(pm.L_uniform(d), pm.L_uniform(d), th):.3f}")
P("Critical opening h* (monolayer, closed form), θ = 70°:")
for ar in [20, 100, 1000]:
    P(f"a/R = {ar}: h*/R = {-1+np.sqrt(1+2*ar*np.cos(th)):.2f}")
P("p_eff = P_max R/(2 γ cosθ) for monolayer = 2/(h(h+2)):")
for h in [pm.L_HEX - 1, 0.5, 1, 2, 3]:
    P(f"h = {h:.3f}R: p_eff = {2/(h*(h+2)):.3f}")
open("key_numbers.md", "w").write("\n".join(out) + "\n")
print("\n".join(out))

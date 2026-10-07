"""Pore-scale model for the maximum capillary pressure of a particle-laden emulsion film.

Geometry (all lengths in units of the particle radius R):
  a ring of spheres around a pore axis, sphere centres at distance L from the axis;
  clear opening radius h = L - 1. The oil/water meniscus in the pore is a spherical cap
  that meets each sphere at the water-side contact angle theta. psi is the meniscus slope
  at the contact line, so the contact line sits at polar angle alpha = theta + psi.

Dimensionless pressure  Phat = P R / (2 gamma) = sin(psi) / (L - sin(theta + psi)).

Failure of a film happens at the first of two events while P is raised quasi-statically:
  meet  - the meniscus reaches the plane where it meets the meniscus from the other oil;
  mech  - P passes the maximum of Phat(psi): the contact line slides past the particle.
"""
import numpy as np

H_NEST = 2 * np.sqrt(2 / 3)       # centre-plane spacing of a nested (hcp) bilayer, units of R
L_HEX = 2 / np.sqrt(3)            # close-packed hexagonal monolayer: pore-centre to sphere-centre


def _branch(L, th, n=200_000):
    psi = np.linspace(1e-6, np.pi - th - 1e-6, n)
    a = th + psi
    rho = L - np.sin(a)
    ok = rho > 1e-9
    psi, a, rho = psi[ok], a[ok], rho[ok]
    return psi, a, rho, np.sin(psi) / rho


def phat_film(L, th, gap):
    """Failure pressure (P R / 2 gamma) of one layer whose meniscus must sag `gap` below the
    particle centre plane to meet the opposing meniscus. gap = 0: bridging monolayer.
    Returns (Phat, mode) with mode 'meet' or 'mech'."""
    psi, a, rho, P = _branch(L, th)
    sag = rho * np.tan(psi / 2)
    zc = np.cos(a)
    im = int(np.argmax(P))
    hit = np.nonzero(sag >= zc + gap)[0]
    if hit.size and hit[0] < im:
        return float(P[hit[0]]), "meet"
    return float(P[im]), "mech"


def phat_bridge_exact(L, th):
    """Closed form for the bridging monolayer (meet criterion): P = 4 gamma R cos(theta)/(L^2 - R^2)."""
    return 2 * np.cos(th) / (L * L - 1)


def phat_bridge(L, th):
    return phat_film(L, th, 0.0)[0]


def phat_bilayer(L1, L2, th, H=H_NEST):
    """Bilayer, layer-1 pore L1 and the partner-layer pore L2 facing it.
    Oil 1 must first yield through its own layer (penetration, gap H/2 measured to the
    mid-plane), and the partner layer then acts as a bridging monolayer. Either oil may go first."""
    pen1, pen2 = phat_film(L1, th, H / 2)[0], phat_film(L2, th, H / 2)[0]
    br1, br2 = phat_bridge(L1, th), phat_bridge(L2, th)
    return min(max(pen1, br2), max(pen2, br1))


def L_from_h(h):
    return 1.0 + h


def L_stretched_bond(d):
    """Pore next to one bond stretched to centre spacing d (units R); circumradius of the
    (2, 2, d) centre triangle. Valid while the triangle is acute, d < 2*sqrt(2)."""
    return 4.0 / np.sqrt(16.0 - d * d)


def L_uniform(d):
    """Hexagonal lattice with uniform centre spacing d."""
    return d / np.sqrt(3)


def meniscus_profile(L, th, P):
    """Cap profile for drawing: given Phat, return (psi, Rc, rho, z_contact). None if no static cap."""
    psi, a, rho, Pp = _branch(L, th)
    im = int(np.argmax(Pp))
    if P > Pp[im]:
        return None
    i = int(np.argmin(np.abs(Pp[:im + 1] - P)))
    return psi[i], rho[i] / np.sin(psi[i]), rho[i], np.cos(a[i])


if __name__ == "__main__":
    # self-checks: closed form vs numerics, failure mode across theta and h
    worst = 0
    for th_deg in range(5, 90, 5):
        th = np.radians(th_deg)
        for h in [0.155, 0.2, 0.3, 0.5, 1, 2, 3, 5]:
            p, m = phat_film(1 + h, th, 0.0)
            ex = phat_bridge_exact(1 + h, th)
            worst = max(worst, abs(p / ex - 1))
            if m != "meet":
                print("mech first:", th_deg, h)
    print(f"max rel. deviation closed form vs numeric: {worst:.2e}")
    th = np.radians(70)
    for name, L in [("hex", L_HEX), ("vac", 2.0)]:
        print(name, "bridge", round(phat_bridge(L, th), 3),
              "bilayer", round(phat_bilayer(L, L, th), 3),
              "bilayer one-layer defect", round(phat_bilayer(L, L_HEX, th), 3))

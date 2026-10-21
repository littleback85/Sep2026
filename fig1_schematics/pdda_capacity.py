"""pdda_capacity.py — how many BSA one PDDA chain (Mw 1.0-1.5 MDa) can glue,
and what that means for the four tight layers between two oil drops.

    python pdda_capacity.py          # prints the table, writes out/pdda_capacity.json

All inputs are in INPUTS; every number in the README and on the schematics
comes from here.
"""
import json, os
import numpy as np

NA = 6.02214076e23
INPUTS = dict(
    Mw_PDDA=(1.0e6, 1.5e6),     # g/mol, as given
    M0=161.67,                  # g/mol, DADMAC repeat unit (chloride form), 1 charge each
    b0=0.50,                    # nm contour per repeat unit (5-ring cyclopolymer, ~2 charges/nm)
    lp=3.0,                     # nm, intrinsic persistence length (salt-screened)
    M_BSA=66430.0,              # g/mol
    Z_BSA=(13.0, 18.0),         # |net charge| of BSA, pH 7.0 -> 7.4
    c_BSA=260.0,                # mg/mL BSA in the coacervate (Fig. 3)
    d_layer=7.7,                # nm, SANS correlation distance = lateral pitch of a BSA layer
    hb=20.0,                    # nm, film thickness when the anchored layers meet (premise)
    n_layers_hb=4,              # BSA layers between the two oil surfaces at hb
    h_comp=(10.8, 13.0),        # nm, film at 0.86 MPa (0.54-0.65 hb)
    rho_BSA=1.36,               # g/cm3, dry protein (1/0.735)
    rho_PDDA=1.2,               # g/cm3, dry PDDA chloride (approx.)
)


def calc(I=INPUTS):
    lo_hi = lambda f: (f(0), f(1))
    r = {}
    N = [m / I["M0"] for m in I["Mw_PDDA"]]                     # charges per chain
    L = [n * I["b0"] for n in N]                                # contour, nm
    bK = 2 * I["lp"]
    Rg = [np.sqrt(l * bK / 6) for l in L]                       # ideal coil (coacervate ~ theta)
    Ree = [np.sqrt(l * bK) for l in L]
    r["charges_per_chain"] = N
    r["contour_um"] = [l / 1000 for l in L]
    r["kuhn_segments"] = [l / bK for l in L]
    r["Rg_nm"] = Rg
    r["Ree_nm"] = Ree
    # bulk coacervate
    nB = I["c_BSA"] * 1e-3 / 1e21 / I["M_BSA"] * NA               # BSA per nm3
    r["nB_per_nm3"] = nB
    r["BSA_spacing_nm"] = nB ** (-1 / 3)
    # (1) charge matching: BSA glued per chain
    n_glue = [N[0] / I["Z_BSA"][1], N[1] / I["Z_BSA"][0]]
    r["BSA_per_chain_charge_matched"] = n_glue
    r["BSA_per_chain_central"] = (sum(N) / 2) / (sum(I["Z_BSA"]) / 2)
    r["contour_per_BSA_nm"] = [z * I["b0"] for z in I["Z_BSA"]]
    # PDDA content of a charge-matched coacervate and its mesh
    cP = [nB * z * I["M0"] / NA * 1e21 * 1e3 for z in I["Z_BSA"]]  # mg/mL
    r["c_PDDA_mg_per_mL_if_matched"] = cP
    rhoL = [nB * z * I["b0"] for z in I["Z_BSA"]]                # nm contour per nm3
    r["mesh_nm"] = [x ** -0.5 for x in rhoL][::-1]
    # (2) pervaded volume: BSA inside one coil, and coil overlap
    Vc = [4 / 3 * np.pi * g ** 3 for g in Rg]
    r["BSA_in_coil_volume"] = [v * nB for v in Vc]
    r["chains_sharing_a_coil_volume"] = [Vc[0] * nB / (N[0] / sum(I["Z_BSA"]) * 2),
                                          Vc[1] * nB / (N[1] / sum(I["Z_BSA"]) * 2)]
    # (3) the four tight layers at hb
    G_layer = 1 / I["d_layer"] ** 2                              # BSA per nm2 per layer
    G_film = I["n_layers_hb"] * G_layer
    r["Gamma_per_layer_mg_m2"] = G_layer * I["M_BSA"] / NA * 1e21   # mg/m2 (1 nm2 = 1e-18 m2)
    r["Gamma_film_BSA_per_nm2"] = G_film
    foot = [n / G_film for n in n_glue]
    r["chain_footprint_nm2"] = foot
    r["chain_footprint_diameter_nm"] = [2 * np.sqrt(a / np.pi) for a in foot]
    r["coil_lateral_diameter_nm"] = [2 * g * np.sqrt(2 / 3) for g in Rg]
    # confined chain: blobs of size hb
    g_blob = (I["hb"] / bK) ** 2                                  # Kuhn segments per blob
    r["film_crossings_per_chain"] = [l / bK / g_blob for l in L]
    r["contour_per_crossing_nm"] = g_blob * bK
    # dry thickness and volume fractions
    dry_B = G_film * I["M_BSA"] / NA / (I["rho_BSA"] * 1e-21)     # nm
    dry_P = [G_film * z * I["M0"] / NA / (I["rho_PDDA"] * 1e-21) for z in I["Z_BSA"]]
    dry = [dry_B + p for p in dry_P]
    r["dry_thickness_4_layers_nm"] = dry
    r["phi_dry_bulk"] = I["c_BSA"] * 1e-3 / I["rho_BSA"] + cP[0] * 1e-3 / I["rho_PDDA"]
    r["phi_dry_at_hb"] = [d / I["hb"] for d in dry]
    r["phi_dry_at_0.86MPa"] = [dry[0] / I["h_comp"][1], dry[1] / I["h_comp"][0]]
    r["layer_pitch_at_hb_nm"] = I["hb"] / I["n_layers_hb"]
    r["layer_pitch_at_0.86MPa_nm"] = [h / I["n_layers_hb"] for h in I["h_comp"]]
    r["rest_film_nm"] = I["hb"] + 4 * I["d_layer"]
    return r


def fmt(v, nd=0):
    if isinstance(v, (list, tuple)):
        parts = [fmt(x, nd) for x in v]
        return parts[0] if len(set(parts)) == 1 else "–".join(parts)
    return f"{v:,.{nd}f}"


if __name__ == "__main__":
    r = calc()
    os.makedirs("out", exist_ok=True)
    with open(os.path.join("out", "pdda_capacity.json"), "w") as f:
        json.dump(dict(inputs=INPUTS, results=r), f, indent=1)
    rows = [
        ("Charges (repeat units) per chain", fmt(r["charges_per_chain"])),
        ("Contour length (µm)", fmt(r["contour_um"], 1)),
        ("Kuhn segments (b = 2lp = 6 nm)", fmt(r["kuhn_segments"])),
        ("Coil Rg, ideal (nm)", fmt(r["Rg_nm"])),
        ("BSA glued per chain, charge-matched", fmt(r["BSA_per_chain_charge_matched"])),
        ("  central value (1.25 MDa, |Z| = 15.5)", fmt(r["BSA_per_chain_central"])),
        ("PDDA contour per glued BSA (nm)", fmt(r["contour_per_BSA_nm"], 1)),
        ("PDDA in coacervate if matched (mg/mL)", fmt(r["c_PDDA_mg_per_mL_if_matched"], 1)),
        ("Mesh from contour density (nm)", fmt(r["mesh_nm"], 1)),
        ("BSA inside one coil volume (bulk)", fmt(r["BSA_in_coil_volume"])),
        ("Chains sharing a coil volume (bulk)", fmt(r["chains_sharing_a_coil_volume"], 1)),
        ("Γ per BSA layer (mg/m²)", fmt(r["Gamma_per_layer_mg_m2"], 2)),
        ("Film footprint glued by one chain, 4 layers (nm, diameter)", fmt(r["chain_footprint_diameter_nm"])),
        ("Coil lateral diameter 2Rg√(2/3) (nm)", fmt(r["coil_lateral_diameter_nm"])),
        ("Times one chain crosses the 20-nm film", fmt(r["film_crossings_per_chain"])),
        ("Dry thickness of the 4 layers (nm)", fmt(r["dry_thickness_4_layers_nm"], 1)),
        ("φ_dry bulk / at hb / at 0.86 MPa", f'{r["phi_dry_bulk"]:.2f} / {fmt(r["phi_dry_at_hb"], 2)} / '
                                             f'{fmt(r["phi_dry_at_0.86MPa"], 2)}'.replace(",", "")),
        ("Layer pitch at hb / at 0.86 MPa (nm)", f'{r["layer_pitch_at_hb_nm"]:.1f} / '
                                                f'{fmt(r["layer_pitch_at_0.86MPa_nm"], 1)}'),
    ]
    w = max(len(a) for a, _ in rows)
    for a, b in rows:
        print(f"{a:<{w}}  {b}")

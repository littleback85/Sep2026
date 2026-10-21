# Fig. 1 molecular schematics: PDDA/BSA corona and film states, v1 (21 Oct 2026)

`python make_fig1_schematics.py` rebuilds everything in `out/` in about 30 s (numpy, scipy,
matplotlib, shapely). `python pdda_capacity.py` prints the PDDA numbers.

| file | what |
|---|---|
| `out/fig1a_zoom.*` | Fig. 1a zoom, 27 × 42 mm, 1 nm = 0.6 mm, labels as in the v2 draft |
| `out/fig1a_zoom_break.*` | same with a break in the mobile layer (recommended, see below) |
| `out/fig1a_zoom_art.*` | no text, for compositing |
| `out/fig1c_film_states.*` | Fig. 1c top strip, 98 × 50 mm, 1 nm = 0.44 mm in all four windows |
| `out/fig1c_film_states_art.*` | same molecules, no text |
| `out/legend.*` | colour key |
| `out/fig1_schematics_pack.pdf` | **download pack**: p1 all panels, labelled and text-free, with keys (colour, symbols, scale) and draft legend text, 1:1 on A4; p2 the numbers |
| `out/sheet.pdf/.png` | review sheet: both schematics + numbers |
| `out/stats.json`, `out/pdda_capacity.json` | what was drawn; the capacity calculation |

Code: `coac_glyphs.py` (glyph library from Glyphs_BSA_PDDA_v1, palette changed, charged
variants unused), `pdda_glue.py` (PDDA routing), `scenes.py` (the two scenes),
`make_fig1_schematics.py` (layout). `draw_zoom()` and `draw_strip()` take a figure and mm
positions, so fig1.py can call them directly.

## Colours
BSA is green, in three shades that encode mobility (from the Fig. 1 v2 draft):
dark `#0B5E44` adsorbed at the oil, mid `#2E9E76` anchored (glued) row, light `#A3DAC0` mobile.
PDDA is grey `#A6A6A6` with a `#555555` casing. Coacervate `#D2EDE1`, oil `#F5D2E5`,
dilute `#EEF5FB` (draft tints). Compressed film background `#BFE3D2` (less water).

## PDDA, Mw 1.0–1.5 MDa: how many BSA one chain glues

| quantity | value |
|---|---|
| charges (repeat units, 161.7 g/mol, +1 each) | 6,185–9,278 |
| contour length (0.50 nm per unit) | 3.1–4.6 µm |
| coil Rg, ideal (l_p = 3 nm) | 56–68 nm |
| **BSA glued per chain, charge-matched (BSA net −13 to −18)** | **344–714 (≈ 500)** |
| PDDA contour per glued BSA | 6.5–9.0 nm ≈ one BSA diameter |
| PDDA in the coacervate if charge-matched (260 mg/mL BSA) | 8–11 mg/mL |
| mesh from that contour density | 6.9–8.1 nm (SANS ξ ≈ 9 nm, d = 7.7 nm) |
| BSA inside one coil volume (bulk) | 1,700–3,100 → 4–5 chains interpenetrate |

The tight layers at h_b = 20 nm (4 BSA layers, 2 per oil surface):

| quantity | value |
|---|---|
| Γ per layer at 7.7-nm pitch | 1.9 mg/m² (≈ a protein monolayer) |
| layer pitch at h_b / at 0.86 MPa | 5.0 nm (side-on BSA, 3–4 nm, + PDDA) / 2.7–3.2 nm |
| film area one chain neutralises, all 4 layers | disc 81–116 nm across |
| the chain's own lateral coil width | 91–111 nm |
| times one chain crosses the 20-nm film (blobs of size h_b) | ~46–70 |
| dry thickness of the 4 layers | 5.7 nm |
| φ_dry: bulk / at h_b / at 0.86 MPa | 0.20 / 0.28–0.29 / 0.44–0.53 |

What this means for the drawing: one chain holds about as many BSA as sit in a 100-nm patch of
the four tight layers, and that patch is about the chain's own coil width. So each chain is a
flattened sheet that weaves through all four layers and crosses the film tens of times. The two
anchored layers are stitched into one sheet, which a pressure can densify but not drain.

The answer scales linearly with Mw: if the PDDA is 100–150 kDa, divide the counts by 10
(34–71 BSA per chain, Rg 18–21 nm). Measured coacervate PDDA content c_P replaces charge matching:
BSA per chain = (Mw / 66.4 kDa) × (c_BSA / c_P).

## Drawing rules
- **PDDA glues.** Each chain is routed from protein to protein. It wraps part of every BSA it
  glues (in contact), then leaves along a common tangent. A tangent between opposite senses threads
  the chain between two BSA (sandwiched, one strand on both); a same-sense tangent spans the gap.
  The tangent construction keeps the line smooth; contact per glued BSA is a median 19 % of its
  perimeter (10–90 %: 5–44 %).
- **Flexibility and randomness.** l_p ≈ 3 nm against an 8-nm protein, so the chain turns by a large
  angle at every protein: a random walk on the protein scale. Long bridges sag slightly.
- **Isotropic.** The next protein is chosen with no direction preference. Measured on the drawings:
  S = ⟨cos 2θ⟩ = +0.06 (zoom, mobile) and −0.05 (rest core); over 12 zoom layouts 0.04 ± 0.09.
  In the anchored layer S = +0.4 to +0.6: chains lie along the oil, as confinement requires.
- **No chain ends.** A 3–4.6 µm chain has no end inside a 50-nm window. Chains leave through a window
  edge or run under a BSA (out of the drawing plane).
- **Amount.** Drawn PDDA contour is 8.4–9.2 nm per BSA in view, close to the charge-matched
  6.5–9 nm.
- **Anchored layer = 2 rows ≈ h_b/2.** Adsorbed row: flattened onto the oil (partly spread).
  Glued row: sits in the hollows, ~1.1 nm above, with a PDDA strand sandwiched between them.
  Anchored thickness drawn: 10.0 nm.

## Panel c strategy
Windows run left to right in order of h, like the Π(h) axis below: ③ 13 nm, ② 20 nm,
stepwise thinning (h_b + d | h_b + 2d), ① 51 nm. All are at one scale, so thickness reads directly.
- ① rest, h = h_b + 4d: two anchored layers plus a mobile core that is bulk coacervate
  (random BSA, φ = 0.43, isotropic PDDA). Brackets: h_b/2 + 4d + h_b/2.
- Stepwise thinning: a front between one and two mobile layers moves toward the thick side; one
  layer leaves per step (the oscillatory branches). This window has no number; add a marker on the
  Π(h) curve if you want one.
- ② h = h_b: only the four anchored rows remain. They are the same molecules at the same x
  positions as in ①. They meet at the midplane, where PDDA stitches across (5 crossings in view).
- ③ h = 0.65 h_b: the same molecules and chains as ② squeezed normal to the film. Nothing is added
  or removed; only water and ions leave (darker background).
- Pressure arrows scale with log Π.

## Open choices
- **Zoom break:** molecules are to scale; the mobile layer is truncated. The break version says so
  and matches "amount set by V_C"; the caption can then say "molecules to scale, mobile layer
  shortened" instead of "not to scale".
- **h_b = 20 nm and 4 layers** remain premises (cryo-SEM pending). If h_b changes, edit `HB` in
  `scenes.py` and the `ROWS` squash so the anchored layer is h_b/2.
- Seeds: `--zoom-seed`, `--film-seed` give other layouts with the same statistics.

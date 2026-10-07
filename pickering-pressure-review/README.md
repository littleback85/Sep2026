# Pickering emulsions and foams: stability expressed as a pressure

Literature survey, October 2026. The master table is also in [`pressure_table.csv`](pressure_table.csv).

**How this was gathered:** this environment's network policy blocked full-text access (pubs.rsc.org, sciencedirect, ncbi/PMC, mdpi, arxiv.org and the Russian journal mirrors). Every number below therefore comes from abstracts, publisher metadata and search-engine excerpts of reviews. Each row is tagged so you can see how firm it is:

| Tag | Meaning |
|---|---|
| **A** | Stated in the paper's own abstract or metadata |
| **S** | Taken from a secondary source (a review or a later paper) quoting the work; still needs checking against the primary paper |
| **C** | My calculation from a published formula; inputs are listed |
| **K** | From my background knowledge; not re-checked in this session |
| **N** | The paper reports numbers but I couldn't reach them; I need the PDF |

---

## 1. Bottom line

1. **The "experiment ≈ ¼ of theory" result.** The ≈100 kPa breakdown pressure, about 25% of the calculated P<sub>c,max</sub>, comes from the Penza group (Kruglyakov, Nushtaeva, Vilkova). It is n-decane-in-water stabilised by modified silica, squeezed on a porous plate or in a centrifuge (JCIS 2004; Elsevier chapter 2004). The authors give two reasons for the gap: **(i) a sharp drop in the capillary part of the film's elasticity** when the film is stretched locally (the particles move apart), and **(ii) defects in how the particle layer is packed** [S]. Their companion model-film work found that a perfectly packed film matches theory. Experiments with glass spheres packed hexagonally agreed with the calculated P<sub>c</sub>(h) and P<sub>c,max</sub> at several contact angles [A]. So, as the authors themselves frame it, defects (together with stretching) are what separate the ideal case from the real one.

2. **Are defects the main reason in general?** In the broad sense, mostly yes: anything that leaves a pore larger than in the ideal lattice lowers the pressure. That includes vacancies, grain boundaries, random rather than crystalline packing, polydispersity, aggregates, and gaps that open when a drop deforms. The film fails at its *largest* pore, so the weakest-link statistics favour failure well below the ideal value. Surface Evolver simulations show the same thing: randomly packed particle films follow the same trends as regular arrays but always rupture at **lower** capillary pressure, because irregular packing leaves larger patches of bare film (Morris, Neethling & Cilliers 2011, 2014) [A]. Three caveats:
   * **The factor of 4 can't be pinned on defects alone.** P<sub>c,max</sub> ∝ cos θ / R. Moving θ from 70° to 80° halves cos θ (0.342 → 0.174). For fumed or colloidal silica, the particle radius R itself is uncertain by about ×4–16, because aggregates are much larger than primary particles (Aerosil 12 nm → about 200 nm aggregates; Ludox 15 nm → about 60 nm). The theory carries an uncertainty about as large as the gap it is meant to explain.
   * **In many data sets the gap is far larger than ×4.** For nanoparticle layers, theory predicts MPa (§3), yet measured failure pressures are often only a few kPa. Examples: carbon-black emulsions demulsify at 4.6 kPa; armoured bubbles collapse at ΔP ≈ 1.57 γ/R<sub>bubble</sub>, *independent of particle size*; micropipette failure of particle-coated drops is "set by the fluid surface tension". In these cases the failure scales with the **drop** size, not the particle size. That points to particles being rearranged, expelled or buckled (plastic failure of the armour), not to fluid squeezing through an intact lattice. Tcholakova, Denkov & Lips (2008) surveyed the data and concluded that **particle-stabilised emulsions are not exceptionally resistant to coalescence**. What particles do achieve is a complete stop to Ostwald ripening.
   * **Many stable Pickering emulsions have no dense layer at all.** Some are stable at under 3% coverage, held by particle "crowns" that bridge the contact points between drops (Adv. Sci. 2025). Others rely on networks of particles that are not attached to the interface (Hatchell 2022). For these, the "perfect layer minus defects" picture doesn't apply.

3. **Can packing be perfect, and what would it withstand?**
   * **On a flat model film with large, monodisperse spheres, locally yes.** The Penza glass-sphere film is the example.
   * **On a real droplet, no.** A triangular lattice on a sphere *must* contain at least 12 five-fold disclinations. Above about 300 particles per drop (R/d ≈ 5), these grow into grain-boundary "scars" of 3–6 dislocations each (Bausch et al., Science 2003) [A]. A 20 µm drop covered with 200 nm particles carries about 36,000 particles, so scars are unavoidable.
   * **Other limits on perfect packing:**
     - Irreversible random adsorption jams at 54.7% coverage. Getting near 90.7% (hexagonal close packing) needs compression, for example by limited coalescence.
     - More than about 10% size spread turns the layer amorphous.
     - Squeezing a drop into a polyhedron at fixed volume needs about **+10% surface area**: a Kelvin cell has 1.099× the area of a sphere of equal volume [C]. A layer that starts close-packed at 0.907 is therefore pulled down to about 0.83 coverage, which opens gaps unless particles rearrange or the shell wrinkles. Compression itself creates defects.
   * **Ideal pressure** (§3): roughly **MPa for 10–100 nm particles, tens of kPa for 1 µm, a few kPa for 10 µm, and hundreds of Pa for the 50 µm-scale glass spheres** used in model films.

---

## 2. Turning each kind of measurement into a pressure

| Measurement | Pressure it gives | Formula / note |
|---|---|---|
| Porous plate, or applied pressure drop on a film or foam layer (APDT/FPDT) | Capillary pressure P<sub>c</sub> = P<sub>dispersed</sub> − P<sub>continuous</sub> | Applied directly. Note: a set-up driven by vacuum is limited to about 100 kPa. |
| Thin-film pressure balance | Disjoining/capillary pressure at rupture | Applied directly. Measures one film, so the result depends on film size. |
| Centrifuge (cream or sediment layer) | Osmotic pressure at the top of the cream, Π<sub>max</sub> | Π ≈ Δρ · (G·g) · h<sub>cream</sub> · φ̄. Hatchell et al. use P<sub>demuls</sub> = Δρ g<sub>k</sub>(V<sub>oil</sub> − V<sub>released</sub>)/A. |
| Same, worked numbers [C] | Δρ = 200 kg m⁻³, h = 1 cm | 1,000 g → 19.6 kPa; 5,000 g → 98 kPa; 10,000 g → 196 kPa. A decane-like Δρ = 270 gives ×1.35. |
| Critical osmotic pressure scaled by drop radius (Tcholakova) | Π<sub>cr</sub>·R (Pa·m) | Lets you compare different drop sizes. Surfactant and protein emulsions: 0.1–0.3 Pa·m. |
| Bubble or drop collapse and buckling | External overpressure ΔP<sub>collapse</sub> | Compare it with Laplace pressure 2γ/R<sub>drop</sub>. |
| Micropipette aspiration | Suction ΔP<sub>c</sub> | Set by about 2γ/R<sub>pipette</sub>. |
| Surface pressure of a particle monolayer, Π<sub>s</sub> (mN/m) | Drop pressure 2(γ − Π<sub>s</sub>)/R | When Π<sub>s</sub> → γ, ΔP → 0 and the drop buckles or facets. |
| Rheology (yield stress, critical shear stress) | Stress in Pa | Already a pressure. Compare it with the osmotic pressure. |

---

## 3. What a perfect layer could withstand (my calculation)

**Scale factor.** Every P<sub>c,max</sub> model has the form P<sub>c,max</sub> = p · 2γ cos θ / R, where p is a packing factor. The table below gives P\* = 2γ cos θ / R for γ = 50 mN/m (alkane–water) [C], in kPa:

| Particle radius R | θ = 60° | θ = 70° | θ = 80° |
|---|---|---|---|
| 6 nm (Aerosil primary particle) | 8,333 | 5,700 | 2,894 |
| 50 nm | 1,000 | 684 | 347 |
| 100 nm (Aerosil aggregate, ~200 nm diameter) | 500 | 342 | 174 |
| 270 nm (S-3 silica, 540 nm diameter) | 185 | 127 | 64 |
| 1 µm | 50 | 34 | 17 |
| 10 µm | 5.0 | 3.4 | 1.7 |
| 50 µm (model-film glass spheres) | 1.0 | 0.7 | 0.3 |

**Kaptay's close-packed bilayer.** The equation is P<sub>c,max</sub> = 2pσ(cos θ + z)/R, with p = 4.27, z = 0.405 for θ < 90°, and p = 2.73, z = 0.633 for 90° < θ < 129.3° [S]. As a check, p·z is about 1.73 on both branches, so the two forms join smoothly at θ = 90°. Values in kPa [C]:

| R | θ = 60° | 70° | 80° | 100° | 120° |
|---|---|---|---|---|---|
| 100 nm | 3,864 | 3,190 | 2,471 | 1,254 | 363 |
| 1 µm | 386 | 319 | 247 | 125 | 36 |
| 10 µm | 39 | 32 | 25 | 13 | 3.6 |

**Single touching hexagonal monolayer (bridging), my rough estimate.** Treat the throat between three touching spheres as a circular pore of the inscribed radius, (2/√3 − 1)R = 0.155R. A meniscus moving inward then needs P<sub>c</sub>(φ) = (2γ/R) · cos(θ + φ)/(1.155 − cos φ). This rises steadily until the menisci from the two faces meet at the equator, giving **p ≈ 6.5** (≈ 2.4 for a square array) [C]. This is an *upper bound*. A real triangular throat has a larger effective radius, and random packing lowers the value further (Morris et al.).

So a perfect layer of 10–100 nm particles would in principle hold **0.1–10 MPa**. Ordinary centrifuges reach only **10–200 kPa** at the top of a 1 cm cream (§2), so most "survived centrifugation" claims give only a *lower bound*. The Penza value implies a calculated P<sub>c,max</sub> of about 400 kPa (100 kPa ÷ 0.25). That matches P\* for R ≈ 100 nm with p ≈ 1, which suggests (not confirmed) that they used aggregate-scale radii. The PDF would settle it.

---

## 4. Master table

| ID | Kind | System | Method: what the pressure means | Reported pressure / result | Theory or comparison | Tag | Reference |
|---|---|---|---|---|---|---|---|
| T1 | Theory | Close-packed particle layer in an emulsion film | Cell model; P<sub>c</sub> needed to drain the film between particles | P<sub>c,max</sub> rises as R falls and as θ falls | First quantitative P<sub>c,max</sub> mechanism | A | Denkov, Ivanov, Kralchevsky, Wasan, *JCIS* 150 (1992) 589 |
| T2 | Theory | Monolayer or bilayer; o/w, w/o, foams | P<sub>c,max</sub> = ±2pσ(cos θ ± z)/R | z = 0 (monolayer). Bilayer: p = 4.27, z = 0.405 (θ < 90°); p = 2.73, z = 0.633 (90–129.3°). Optimum θ about 70–86° for foams | Values in §3 | A (formula) / S (p, z) / N (monolayer p) | Kaptay, *Colloids Surf A* 230 (2003) 67; 282–283 (2006) 387 |
| T3 | Theory | Monodisperse spheres, dense hexagonal layer | P<sub>c</sub>(h) isotherm; threshold rupture pressure | P<sub>c,max</sub>(θ, R) calculated | Basis of the Penza "theory" value | A; values N | Nushtaeva & Kruglyakov, *Mendeleev Commun* 11 (2001) 235; *Colloid J* 65 (2003) 341 |
| T4 | Theory (Surface Evolver) | Regular 2D/3D arrays in a film | Rupture P<sub>c</sub> versus spacing, θ, packing pattern | Rupture P<sub>c</sub> rises as spacing between particles shrinks | — | A | Morris, Pursell, Neethling, Cilliers, *JCIS* 327 (2008) 138 |
| T5 | Theory (Surface Evolver) | Random packing, up to 20 particles per cell | Rupture P<sub>c</sub> versus packing density and θ | **Same trends, but always lower than regular packing** (larger free-film areas) | Direct theoretical support for the "defect" explanation | A | Morris, Neethling, Cilliers, *Langmuir* 27 (2011) 11475 |
| T6 | Theory (about 3,500 simulations) | Random packings | Closed-form P<sub>c,crit</sub>(film loading, θ) | Simple equation (needs PDF) | Usable for real coverage values | A; equation N | Morris, Neethling, Cilliers, *Langmuir* 30 (2014) 995 |
| T7 | Theory / experiment | Silica in emulsion films | Bilayer versus bridging monolayer | Bilayer turns into a bridging monolayer at *low* P<sub>c</sub> | Bridging can stabilise even sparse layers | S | Horozov & Binks, *Angew Chem* 45 (2006) 773; Horozov, *COCIS* 13 (2008) 134 |
| T8 | Theory | Solid-coated bubbles | Allowed P<sub>c</sub> | Coated bubbles can sustain "anomalous" (zero or negative) capillary pressure | Explains why ripening stops | K | Kam & Rossen, *JCIS* 213 (1999) 329 |
| E1 | Emulsion | n-decane / water, modified silica | Porous plate and centrifuge; P<sub>c</sub> applied by lowering continuous-phase pressure; lifetime versus P<sub>c</sub> and θ | **≈100 kPa breaks the emulsion** | **≈25% of calculated P<sub>c,max</sub>** (implies about 400 kPa) | A (method) / S (numbers) | Kruglyakov, Nushtayeva, Vilkova, *JCIS* 276 (2004) 465, doi:10.1016/j.jcis.2004.03.059 |
| E2 | Emulsion (review chapter) | Same group | — | Experimental P<sub>max</sub> ≈ 0.25 × theory | **Put down to a sharp fall in the capillary part of film elasticity, plus packing defects** | S | Kruglyakov & Nushtaeva, ch. 16 in Petsev (ed.), *Emulsions: Structure, Stability and Interactions*, Elsevier 2004, 641–676 |
| E3 | Thin-layer emulsion | Aerosil 12 nm (**aggregates ~200 nm**); Ludox HS 15 nm (**aggregates ~60 nm**); S-3 silica 540 ± 120 nm | Stability versus P<sub>c</sub>, θ, degree of aggregation | Values N | Aggregation sets the effective R | A; N | Kruglyakov & Nushtayeva, *Colloids Surf A* 263 (2005) 330, doi:10.1016/j.colsurfa.2005.04.004 |
| E4 | Model emulsion film | Hexagonally packed transparent glass spheres; several hydrophobicities | Measured P<sub>c</sub>(h) and P<sub>c,max</sub> | Values N | **Good agreement with theory when packing is perfect** | A | Nushtaeva & Kruglyakov 2001 / 2003 (as T3); also *Colloid J* 66 (2004) 456 |
| E5 | Model film | Particle-stabilised emulsion film being stretched | P<sub>c</sub> change on stretching ("capillary part of elasticity") | P<sub>c</sub> at maximum capillary elasticity ≈ ½ P<sub>c,max</sub> | Mechanism (i) in E2 | S | *Colloid J* 70(3) (2008), doi:10.1134/S1061933X08030046 |
| E6 | W/O film | Modified Al(OH)₃ | Applied pressure drop: slow versus sudden ramp | Sudden ramps rupture the film **thicker/earlier** | Put down to **particle repacking**, a dynamic defect | A | Nushtaeva, *Soft* 3 (2014) 1 (SCIRP) |
| E7 | Emulsion | Octane / water, carbon black 0.015 wt% + 0.6 M NaCl | Centrifuge demulsification pressure | **4.6 kPa** | Centrifuge ranking predicts stability in capillary-tube flow | S / A | Hatchell et al., *Colloids Surf A* 586 (2020), "A comparison of the static and dynamic stability of Pickering emulsions" |
| E8 | Emulsion | Carbon black versus salinity | Same | Values N | Salt → networks of *unattached* particles between drops → more stable | A; N | Hatchell et al., *JCIS* 608 (2022) 2321 |
| E9 | Emulsion | PEG-coated silica | Same | Values N | Mildly aggregated particles (0.5–1.0 µmol m⁻² PEG) are the most stable | A; N | Hatchell et al., *JCIS* (2022), PII S0021979722011742 |
| E10 | Concentrated emulsion | Monodisperse O/W, solid-stabilised | Osmotic resistance Π versus φ above φ\* ≈ 0.64 | Π/(γ/R) **substantially higher** than for surfactant emulsions | Drop deformation governed by **surface rigidity / yield stress, not Laplace pressure** | A; values N | Arditty, Schmitt, Lequeux, Leal-Calderon, *EPJ B* 44 (2005) 381; see also *JCIS* 275 (2004) 659 |
| E11 | Survey | Surfactant, protein and particle emulsions | Critical osmotic pressure from centrifugation | Surfactant above CMC, ~3 µm drops: **20–60 kPa**; P·R ≈ **0.1–0.3 Pa·m** | **No evidence that particle emulsions are exceptionally resistant to coalescence**; particles do stop Ostwald ripening | A / S | Tcholakova, Denkov, Lips, *PCCP* 10 (2008) 1608, doi:10.1039/B715933C |
| E12 | Concentrated emulsion | Silanised silica | Rheology (yield stress) | Values N | Elastic solids that coalesce when they yield; elasticity tracks salt and aggregation | A; N | Whitby & Krebsz, *Soft Matter* 10 (2014) 4848 |
| E13 | Emulsion (microfluidic) | Model particles, coverage under 3% | Coalescence in a chip | Stable ≥12 h | Bridging "crowns" at drop contacts; no dense layer needed | A | *Adv Sci* (2025), doi:10.1002/advs.202409903 |
| E14 | Emulsion | Silica, latex, cubes | Coverage versus stability | Kinetically stable at **very low coverage** | Not a P<sub>c,max</sub> mechanism | A | Destribats et al., *Prog Colloid Polym Sci* 137 (2010) 13 |
| F1 | Foam / single film (surfactant) | — | FPDT versus a single film | Critical P<sub>c</sub> **depends on film size** | Statistical / weakest-link baseline | A | Khristov, Exerowa, Minkov, *Colloids Surf A* 210 (2002) 159 |
| F2 | Foam / foam film | Silica + hexylamine; Ludox + hexylamine | Single-film P<sub>cr,film</sub> versus foam P<sub>cr,foam</sub> (FPDT, porous-plate cell) | Same below **~20 kPa**; **diverge above ~20 kPa** | Spread of film sizes in a real foam → earlier failure | S | Vilkova, Elaneva, Kruglyakov, Karakashev, *Mendeleev Commun* (2011) doi:10.1016/j.mencom.2011.11.018; (2012) doi:10.1016/j.mencom.2012.07.003; Kruglyakov et al., *ACIS* 165 (2011) 108 |
| F3 | Foam film | PNIPAM microgels | Thin-film pressure balance (drainage, adhesion) | 1 wt%: bilayer, not adhesive; 0.1 wt%: monolayer, bridging, adhesive | — | A | Keal et al., *Soft Matter* (2017), doi:10.1039/c6sm00873a |
| F4 | Granular soap film | Particles of a few hundred µm, above random close packing | Liquid pressure versus hole-opening behaviour | Critical pressure **∝ γ/d** | Holes between particles don't make a dense film fail | A | Retailleau, Khidas, Rouyer, *RSC Adv* 13 (2023) 30905 |
| F5 | Foam film | PNIPAM microgels | Spatially resolved thin-film pressure balance | Network of thick zones with ~30 nm microgel-depleted thin zones | Built-in heterogeneity, i.e. "defects" | A | arXiv:2608.11999 (2026) |
| D1 | Armoured bubble | PS particles on air bubbles | Dissolution | Faceted bubble: **Laplace overpressure → 0**; dissolution stops | — | A | Abkarian et al., *PRL* 99 (2007) 188301 |
| D2 | Armoured bubble | PS beads; particle diameter varied ×9 | Ambient overpressure until collapse | **ΔP<sub>collapse</sub> ≈ 1.57 γ/R<sub>bubble</sub>**, *independent of particle size* | Plastic failure: single particles are displaced ("dislocations") | S / A | Taccoen, Lequeux, Gunes, Baroud, *PRX* 6 (2016) 011010 |
| D3 | Armoured drop | Water drops; a/R = 0.02–0.2 | Deflation until collapse | Crumpling → faceting → granular arch; **collapse pressure rises with a/R** | — | A; values N | Pitois, Buisson, Chateau, *EPJ E* 38 (2015) 48 |
| D4 | Particle-coated drop | Hexadecane/water, amphiphilic dumbbell particles | Micropipette suction | Drips, then buckles; **critical pressures set by γ**; strength only modestly higher than a bare drop; SDS-coated drops are weaker than bare ones | — | A | Samudrala et al., *PRE* 95 (2017) 012805 |
| D5 | Drop in a pore | Pickering drops | Flow through a constriction | Particles expelled when surface pressure builds and buckling is blocked; depends on Ca, a/pore and R/a | — | A | De Soete et al., arXiv:2210.09799 |
| S1 | Structure | Colloids on drops | Imaging | ≥12 disclinations; scars above ~300 particles; 3–6 dislocations per scar | Perfect order on a drop is impossible | A | Bausch et al., *Science* 299 (2003) 1716 |
| S2 | Structure (simulation) | Polydisperse adsorbed layers | Packing and fracture | Amorphous above ~10.5% size spread; bimodal mixtures are weaker and more brittle | — | A | arXiv:1201.5493 |
| S3 | Structure (theory) | Irreversible random adsorption of disks | Jamming coverage | **0.547**, compared with 0.907 for hexagonal close packing | Close packing needs lateral compression | A | Random sequential adsorption, e.g. arXiv:cond-mat/9906428 |

---

## 5. Why theory overestimates, ranked by how much evidence I found

1. **Packing defects and irregularity.** The authors invoke this themselves (E2). Simulations show it directly (T5, T6). The model film agrees with theory only when packing is perfect (E4). Topology guarantees defects on a drop (S1). Polydispersity and random adsorption add more (S2, S3).
2. **Local stretching or area dilation.** Particles separate, so the capillary part of the elasticity falls; P<sub>c</sub> at maximum elasticity is about ½ P<sub>c,max</sub> (E5). Compressing a drop into a polyhedron needs about 10% extra area [C]. Sudden pressure ramps trigger repacking and early rupture (E6).
3. **Weakest-link statistics.** An emulsion fails at its first ruptured film. Critical P<sub>c</sub> depends on film size (F1), and multi-film foams fail below single films above ~20 kPa (F2).
4. **Uncertain inputs.** Aggregate size versus primary size (E3), and θ near 90° where cos θ changes quickly. This alone can account for a factor of about 2–16.
5. **Plastic failure of the armour.** Collapse pressure is set by γ/R<sub>drop</sub>, not by particle size (D2, D4). This applies when failure happens by particles being expelled or buckling, not by fluid squeezing through the pores.
6. **A different mechanism altogether.** Sparse bridging (E13, E14, T7) or networks of unattached particles (E8). Here P<sub>c,max</sub> theory isn't the right yardstick.

**Inconsistency to resolve with the PDFs.** Whitby & Wanless (2016) report that Tcholakova et al. found Kruglyakov's *scaled* critical pressure to be "about an order of magnitude lower" than the 0.1–0.3 Pa·m typical of surfactant and protein emulsions, assuming r<sub>d</sub> ≈ 20 µm. But 100 kPa × 20 µm = 2 Pa·m, which is about 10× *higher*. Either the 100 kPa refers to a different quantity or set-up, or one of the secondary summaries has the direction wrong. Note also that about 100 kPa is the ceiling of a porous-plate set-up driven by vacuum, so it is worth checking whether it is a true breakdown value or an instrument limit.

---

## 6. PDFs I'd like, in priority order

1. Kruglyakov, Nushtayeva, Vilkova, *JCIS* 276 (2004) 465: lifetime versus P<sub>c</sub> data; which R, θ and formula gave the "theory"; porous plate versus centrifuge.
2. Kruglyakov & Nushtaeva, Elsevier 2004, ch. 16: the 25% statement and the elasticity/defect explanation.
3. Kruglyakov & Nushtayeva, *Colloids Surf A* 263 (2005) 330: values for each particle type and degree of aggregation.
4. Nushtaeva & Kruglyakov, *Colloid J* 65 (2003) 341 and *Mendeleev Commun* 11 (2001) 235: glass-sphere size and measured P<sub>c,max</sub>.
5. *Colloid J* 70 (2008), the stretching paper (½ P<sub>c,max</sub>).
6. Tcholakova, Denkov, Lips, *PCCP* 10 (2008) 1608: their compiled P<sub>cr</sub> table and how they scaled Kruglyakov's value.
7. Kaptay, *Colloids Surf A* 282–283 (2006) 387: monolayer p values.
8. Hatchell et al. (2020 *Colloids Surf A*; 2022 *JCIS* ×2): demulsification-pressure tables.
9. Arditty et al., *EPJ B* 44 (2005) 381: Π(φ) data.
10. Taccoen et al., *PRX* 2016 and Pitois et al., *EPJ E* 2015: collapse-pressure data to digitise.
11. Vilkova et al., *Mendeleev Commun* 2011/2012: values of P<sub>cr,film</sub> and P<sub>cr,foam</sub>.
12. Denkov et al., *JCIS* 1992: p(θ) curves.
13. Golemanov et al., *Langmuir* 22 (2006) 4968 and Destribats et al., *Langmuir* 29 (2013) 12367: to check whether they report pressures from centrifuge compression.
14. Whitby & Wanless, *Materials* 9 (2016) 626 (open access; I just couldn't fetch it): to check the wording above.

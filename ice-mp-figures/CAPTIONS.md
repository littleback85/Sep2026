# Ice-driven microplastic oxidation: two planning figures

Built from the 2026-10-23 deck (5 figure pages). Fig. 1 replots the deck's own data, digitized from the
PDF (±2–5% reading error). Fig. 2 shows **expected** outcomes of experiments not yet done: every curve
there comes from a stated model in `simulate_expectations.py`. No Fig. 2 panel is a measurement.

**Key message (to test):** freezing turns ice grain boundaries into a self-reinforcing oxidation reactor
for microplastics. Gas pushed out by the ice forms nanobubbles; the MPs they touch are oxidized; oxidized,
hydrophilic MPs inhibit recrystallization, so the next freeze gives finer ice with more boundary and more
bubbles. The products end up in meltwater.

---

## Figure 1 | The story as it stands

**Logic arc.** a states the mechanism. b lists the five claims it rests on and rates the evidence for
each. c–i give one data panel per claim, taken from the deck, so a reader sees how strong each link is.

**a**, Proposed mechanism. Left: coarse ice with pristine MPs and a few nanobubbles at grain boundaries
(S2). Centre: close-up of one liquid vein. Bubbles touching an MP deliver ROS and oxidize its surface
(–OH, C=O). A bubble further than the ¹O₂ diffusion length (~150 nm, lifetime ~3.5 µs in water) cannot
reach it (S3). Chain scission releases small molecules (S5). Right: oxidized MPs inhibit recrystallization,
giving finer ice (S4). Blue arrow: the proposed feedback.
**b**, Logic spine. Harvey balls rate the current evidence: full = supported, half = correlational or
partial, empty = unproven or missing. Arrows point to the panel that carries each step.
**c**, S1. XPS O/C after incubation in water (20 °C) or ice (−20 °C). Black bars: stoichiometric O/C of
the repeat unit. For PA, PMMA and PET the ice values match the stoichiometric O/C, so the "increase" there
may be loss of adventitious carbon rather than oxidation. Only PE, PP, PS and PVC show oxidation above
their formula. †PVA is water-soluble and a known ice-recrystallization inhibitor; drop it or treat it as a
positive control.
**d**, S2. Nanobubble count (NTA) through three freeze–melt cycles; shading = frozen. NTA cannot tell
bubbles from nanoplastic fragments; this is the identity test in Fig. 2b.
**e**, S3. O/C against PS bead diameter. Rising O/C with size is the opposite of what ice-front
engulfment theory predicts; the size trend needs a physical explanation.
**f**, S4, first link. Ice grain size falls as the O/C of embedded PS rises.
**g**, S4, second link. Bubble density against grain size, log–log. Grey lines: scaling with
grain-boundary area (d⁻¹) and triple-junction length (d⁻²). The data follow neither (fit slope −0.6; a
plateau, then a step near 100 µm).
**h**, S4, kinetics. PS O/C at −20 °C, with melt–refreeze at 72 h and 217 h (dotted lines). Every curve
slows down and levels off; a self-amplifying loop would accelerate. Refreeze bumps can equally come from
re-oxygenation and new bubbles (tested in Fig. 2e).
**i**, S5. Change in Mw after degradation. Grey band: ±10%, an assumed typical run-to-run GPC
reproducibility. Only PS (−52%) clearly exceeds it.
Status tags (S1–S5 plus a Harvey ball) repeat the spine in each panel.

**Left out of Fig. 1, on purpose:** the fluorescence ROS images (DCF and Rh-6G both concentrate in the
veins, so co-localization is expected whatever the mechanism), the TEMP–EPR trace (non-specific without
D₂O and azide controls), the SEM pictures, and the 3-point O/C-vs-bubble plot (range 2.9–3.1 ×10⁸ mL⁻¹,
within NTA precision; Fig. 2c shows how it should be done).

---

## Figure 2 | What would make it a Nature Water paper (expected outcomes)

**Logic arc.** (1) Pin down the oxidant: a–c. (2) Prove the feedback and bound it: d–f. (3) Follow the
carbon: g. (4) Show it in natural ice and meltwater: h–j. Each panel says what result supports the story
and what result would falsify it.

**a**, Discrimination matrix. Five candidate ROS sources: H1 polymer photosensitizer (Tian et al., Angew.
2022); H2 freezing (Workman–Reynolds) potential at the ice–liquid interface (Song et al., ES&T 2024); H3
spontaneous •OH at the hydrophobic plastic–water interface, amplified by freeze-concentration (Qian et
al., Nature 2026); H4 freeze-exsolved nanobubbles, the deck's mechanism (light-driven as drawn; if it runs
in the dark, the "Dark" cell becomes ○); H5 contact electrification with vial or particles. Each column
has a unique signature, so seven manipulations are enough to tell them apart. Readout: ROS-probe yield
and PS oxidation rate at −20 °C.
**b**, Is the NTA signal a bubble? Resonant-mass (Archimedes) measurement gives the sign of buoyant mass.
A 130 nm air bubble is −1.15 fg; a 300 nm oxidized PS fragment is +1.1 fg. A pressure pulse removes
bubbles but not particles. Check the instrument's detection limit at 100–150 nm.
**c**, Does oxidation track bubble number at fixed pO₂? Bubble density is varied 15-fold without changing
dissolved O₂ (1 MPa freezing; O₂ only, no N₂; air; O₂ + Ar). H4 predicts a line through the origin; all
rivals predict a flat line. Grey band: the 7% range the deck spans. n = 3 simulated per condition,
mean ± s.d.
**d**, Is the feedback set by grain structure or by hydroperoxide chemistry? Initial oxidation rate of
fresh h-PS against grain-boundary density Sᵥ = 2/d. Grain size is set two ways: by thermal annealing (no
additives, because ice-binding proteins and PVA quench ROS) and by pre-oxidized PS-d8 "spectators"
reduced with PPh₃ so they carry no hydroperoxide; the probe is read by C–H vs C–D. If both series fall on
one curve (rate ∝ Sᵥ^0.61, the exponent from Fig. 1g), the feedback runs through the ice. Spectators
sitting above the curve would point to ROOH autocatalysis instead.
**e**, Ratchet test. Per-cycle rate constant normalized to remaining sites (kₙ/k₁) over 10 freeze–thaw
cycles at fixed O₂. The kinetics are calibrated to Fig. 1h (k = 0.0016 h⁻¹, oxidant-pool τ = 100 h,
θ_max = 0.25). Three possible outcomes: rising (net positive feedback, bubbles ∝ d(θ)^−0.61), flat
(re-oxygenation only), falling (hydrophilized surfaces nucleate fewer bubbles). Only "rising" supports the
title claim.
**f**, Zener bound. Particle pinning limits grain size to d = 4r/3f. Reaching the deck's 20–200 µm grains
(blue band) takes MP volume fractions of 10⁻³–10⁻²; natural ice and snow sit at ≤10⁻⁷ (dark band), lab
dosing at 10⁻⁵–10⁻³ (light band). Either the feedback works through something stronger than pinning
(dissolved oxidized oligomers acting like PVA — test by refreezing the particle-free filtrate), or it is
limited to high-loading hotspots.
**g**, Carbon budget with ¹³C-PS. Nanoplastics, ¹³C-DOC and ¹³CO₂ against freeze–thaw cycles; dashed:
water control. **The magnitudes are illustrative.** The hypothesis encoded is that ice *transforms* MPs
(fragments and DOC) rather than mineralizing them, which makes this a water-quality story rather than a
clean-up story.
**h**, Field design. An elevation transect brackets freeze–thaw exposure: low station = few cycles; mid =
most cycles; high = mostly frozen with high UV. Each station gets a cassette trio of reference MPs
(¹³C-PS, PE, PET; known t₀): exposed, dark (removes photo-oxidation) and unfrozen (+2 °C, removes
freezing). Temperature and light loggers count cycles. A snow/firn pit at the high station checks native
MPs against layer age. A lysimeter collects meltwater (j). A lab twin replays the logged record to
separate climate from site. Red ×: a single summit sample measured over time has no known starting state,
arrives already UV-aged, and has no counterfactual.
**i**, Expected field result. ΔO/C of dark cassettes against cumulative field freeze–thaw cycles.
Markers = station. If cycle count, not elevation or UV, drives oxidation, all stations fall on one curve
and the unfrozen controls stay flat. PE is the critical test against ES&T 2025, which found no PE
oxidation in freeze–thaw soils.
**j**, Meltwater first flush. Concentration factor against fraction of snowpack melted. Material at grain
boundaries elutes early (ionic pulse; chloride as tracer). Oxidized products should follow chloride;
nanoplastics are partly retained; intact MPs >10 µm come out late. This links grain-boundary chemistry to
what spring melt delivers to streams and reservoirs: the Nature Water "so what".

---

## Should you just sample summit ice and track degradation over time?

No, not on its own. A single summit ice sample has no counterfactual. Summit MPs arrive after
atmospheric transport under strong UV, so their starting state is unknown and their aging may have
happened before deposition. Summit ice also sees few freeze–thaw cycles, which is the variable the
mechanism depends on. Counts are tens to hundreds of particles per litre, and contamination dominates.
Whatever trend you measure, a referee can attribute it to UV, deposition history or sample handling.

What works (panel h): **deploy reference MPs you made**, with a known starting state, across a gradient
of freeze–thaw exposure, paired at every station with dark and unfrozen controls, and with logged
temperature. Add a **lab twin** that replays the field temperature record. Use **native MPs from a snow
pit only as a secondary archive**. One winter season at an alpine site (or a seasonally frozen soil or
lake-ice site) is enough to produce panel i.

---

### Reproduce
```bash
pip install matplotlib numpy scipy
```
```bash
python3 simulate_expectations.py
```
```bash
python3 fig1_current_spine.py
```
```bash
python3 fig2_roadmap.py
```
Outputs are written to `out/` (vector PDF with live text, SVG for Illustrator, PNG preview). The figures
were built with Liberation Sans, which is metric-compatible with Arial. On a machine with Arial installed
the scripts use Arial automatically.

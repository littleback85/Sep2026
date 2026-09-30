# Fig. 5 — Cooperative excursions beyond the harmonic cage

| File | What it is |
|---|---|
| `out/fig5_document.pdf` | Figure with its legend (p. 1), focus, panel logic and data flags (pp. 2–3), draft of §5 (pp. 4–5), answers to the editorial questions (pp. 6–7) |
| `out/fig5.pdf`, `out/fig5.svg`, `out/fig5.png` | The figure alone at final size (183 × 162 mm). The PDF and SVG are vector with live text, for Illustrator |
| `out/fit_parameters.csv` | Per-condition core width, Δ*, U*, λ, two-state p and s, ε, E_3σ, with s.e. |
| `out/null_model_flagged_fraction.csv` | Panel i: simulated fraction of junctions flagged non-Gaussian against trajectory length |
| `section5_draft.md`, `fig5_legend.md` | Plain-text copies of the section draft and the legend |
| `make_fig5.py` | Builds the figure and the CSVs from `data/` |
| `build_doc.py` | Assembles the PDF document from `out/fig5.svg` and `text/*.html`, printed with Chromium |
| `data/digitized_origin_plots.json` | Markers and fit curves digitised from the Origin EMF plots in the working deck (`emfrender.py`, `digit.py`, `extract.py`) |

Rebuild: `python3 make_fig5.py && python3 build_doc.py` (needs matplotlib, scipy and playwright).

Panel c (split-half σ_i) and the "this study" band in panel i are estimates, and are marked as such in the figure and the legend. Replace them with the real values before submission, and re-run on the raw histograms rather than on the digitised ones.

# 02 — Figure generation

One matplotlib script per manuscript figure. All scripts import shared colours and rcParams
from `00_style_setup.py` — change plot styling there, not in an individual `figN_*.py` file, so
all 12 figures stay visually consistent.

| Script | Figure content |
|---|---|
| `00_style_setup.py` | Shared colour palette (Okabe-Ito colourblind-safe) and matplotlib rcParams — imported by every figure below, not a figure itself |
| `fig1_network.py` | KO/module-level network backbone diagram |
| `fig2_degree_threshold.py` | Edge-count/degree sensitivity across a range of \|rho\| thresholds |
| `fig3_modcorr_heatmap.py` | 15x15 module-module Spearman correlation heatmap |
| `fig4_boxplots.py` | Module-score distributions by source type |
| `fig5_ordination.py` | PCA ordination scatter (PC1 vs PC2) |
| `fig6_betadisp.py` | Beta-dispersion-style within-group distance comparison |
| `fig7_edgecount_heatmap.py` | Module-pair edge-count heatmap |
| `fig8_composition.py` | Electron carrier balance x Recombination repair network/composition detail |
| `fig9_power.py` | Bootstrap power analysis |
| `fig10_arg_heatmap.py` | SARG Type x Module and Mechanism x Module correlation heatmaps |
| `fig11_arg_scatter.py` | Stringent response module score vs. total ARG burden scatter |
| `fig12_taxonomic_dominance.py` | Per-sample taxon-contribution / dominance-check visualisation |

Each script's `outdir` variable controls where the PNG/PDF is written — check/update it before
running if you have moved this repository. Full detail on what each figure visualises and which
upstream analysis it draws from: see `../REPRODUCIBILITY_AND_PARAMETERS.txt`, section
"02_figure_generation".

**Note on `fig1_network.py`:** this figure's design was still under revision as of the last
commit — see the reproducibility notes and manuscript handoff file for the open design
question (what the network backbone figure's single main visual takeaway should be) before
making further changes to it.

# 00 — Core network pipeline

The primary analysis: builds the 15 module scores from the raw 903-KO abundance matrix,
computes the KO-level and module-level Spearman correlation networks, runs Kruskal-Wallis
group tests, PCA/PERMANOVA ordination, and Benjamini-Hochberg FDR correction. This is the
pipeline behind the manuscript's Tables 1-6 and Figures 1-9.

Run order:
1. `recompute_module_scores.py` — module scores (sumlog + legacy meanraw), KO counts per module
2. `step2_module_correlation_and_kruskalwallis.py` — 15x15 module correlation matrix, Kruskal-Wallis by source type/city
3. `step3_crosscheck_original_module_map.py` — sanity check against the pre-freeze module map
4. `step4_KO_level_network_construction.py` — the full 903-KO Spearman network, topology stats, Erdos-Renyi null comparison
5. `debug_fdr_denominator_check.py` — checks zero-variance KOs before FDR correction
6. `step6_fdr_correction_v1.py`, `step6_fdr_correction_v2_final.py` — BH-FDR correction (v2_final is the version cited in the manuscript)
7. `step5_pca_permanova_ordination.py`, `step5b_permanova_distance_metric_sensitivity.py` — ordination and PERMANOVA

Full parameter documentation (thresholds, exact FDR procedure, seeds): see
`../REPRODUCIBILITY_AND_PARAMETERS.txt`, section "00_core_network_pipeline".

Reads the raw abundance matrix (see repository root README, "Data availability"). Writes to
`../_reference_frozen_outputs/`.

# Reference frozen outputs

Not scripts — these are the exact frozen intermediate CSV/JSON outputs from
`../00_core_network_pipeline/`, committed so anyone can check the numbers behind any table or
figure without re-running the pipeline from the raw abundance file (which is not included in
this repository; see the top-level README's "Data availability" section).

| File | Contents |
|---|---|
| `sample_meta.csv` | 18-sample environment/city/replicate metadata table |
| `module_ko_counts_frozen.csv` | KOs per module (Table 1) |
| `module_scores_sumlog_frozen.csv` | Module scores, sum-of-logs definition (used throughout the manuscript) |
| `module_scores_meanraw_frozen.csv` | Module scores, legacy mean-raw definition (cross-check only) |
| `module_corr_sumlog_frozen.csv` | 15x15 module-module Spearman correlation matrix (Figure 3) |
| `module_corr_pairs_sorted.csv` | The same matrix, unrolled and sorted by strength |
| `kw_environment_sumlog_frozen.csv` | Kruskal-Wallis results per module by source type |
| `network_edges.csv` | Full KO-KO network edge list (rho only; see `Supplementary_Tables.xlsx` for the version with p/q values) |
| `network_degree.csv` | Per-KO degree in the network |
| `network_summary.json` | Headline network topology statistics (edge count, density, clustering enrichment, giant-component size, etc.) |
| `VALIDATED_NUMBERS.md` | Running scratch log of every headline number as it was independently re-derived and checked during manuscript preparation. A working record, not a manuscript source — use the manuscript text itself as the citable source for any number. |

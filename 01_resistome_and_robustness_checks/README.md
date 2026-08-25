# 01 — Resistome linkage and robustness checks

Everything downstream of the core network: links the network to SARG-based antibiotic-
resistance-gene (ARG) burden (the manuscript's headline finding), plus every robustness and
sensitivity check run against that finding. This is the pipeline behind Results 3.7-3.9,
Tables 4-8, and Figures 8-12.

Run order (unprefixed `00`/`01`/`02` files are authoritative; `_old_*` files are earlier
duplicates kept only for traceability — do not build new work on them):
1. `00_data_prep_module_definitions.py` — the 15-module -> KO-list map, source of truth
2. `01_sarg_data_prep.py` — loads/cleans the SARG annotation for the 18 samples
3. `02_arg_network_link.py` — total ARG burden vs. module scores, the headline correlation
4. `05_arg_source_type_and_envfit.py` — full Type x Module and Mechanism x Module matrices, leave-one-out sensitivity, envfit-style ordination fit
5. `06_source_type_confound_check.py` — **authoritative** source-type/city confound check (cited in Methods)
6. `07_taxonomic_dominance_check.py` — **authoritative** taxonomic dominance check (cited in Methods/Results)
7. `08_permutation_fdr_check.py` — independent FDR robustness check
8. `09_clr_resistome_sensitivity_check.py` — compositional-data (CLR) sensitivity check

`03_confound_check_alt.py` and `04_taxonomic_dominance_check_figscript_version.py` are earlier
working versions of items 5 and 6 above, kept for traceability only.

Full parameter documentation: see `../REPRODUCIBILITY_AND_PARAMETERS.txt`, section
"01_resistome_and_robustness_checks". Note the important terminology convention documented
there: the taxonomic table used in step 6 is "taxon-stratified", not "species-stratified".

Reads the raw SARG annotation tables (see repository root README, "Data availability") and the
core pipeline's frozen outputs in `../_reference_frozen_outputs/`.

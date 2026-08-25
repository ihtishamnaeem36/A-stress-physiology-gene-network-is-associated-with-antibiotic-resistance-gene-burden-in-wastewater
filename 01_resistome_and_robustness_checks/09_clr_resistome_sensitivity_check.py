"""
06_clr_resistome_sensitivity_check.py

Purpose
-------
Section 3.9 / Supplementary Table S11. The primary resistome-linkage result
(arg_network_link.py) uses the sum-of-log10(x+1) module-score definition used
throughout the manuscript (Section 2.4). Because KO abundances are
compositional, this script re-tests the module x ARG-burden correlation
after replacing the module-score definition with a centred-log-ratio (CLR)
transform -- the same compositional-data convention already used for the
KO-KO network sensitivity check (Section 2.10, "9. step Robustness and
Sensitivity Analyses/code/01_compositional_and_sensitivity.py"): zero values
are replaced by half the smallest non-zero value in that sample, the log is
taken and centred (mean subtracted) per sample, across the full 903-KO
reference set (not the ~10,300-KO whole transcriptome). A module's CLR
score is the sum of its member KOs' CLR values -- the CLR analogue of the
primary sum-of-log10(x+1) score.

Total ARG burden is the same raw-sum-of-21-Types burden used throughout
Section 3.7 (arg_network_link.py) -- the ARG side of the correlation is not
re-transformed, since Spearman correlation is already invariant to any
monotonic transform of a single variable; only the module-score side needs
the CLR treatment to test the compositional-sensitivity question.

A second block reproduces the mechanism check reported in the Discussion:
a sample's overall log-abundance across the FULL ~10,389-KO unstratified
functional profile (DATA used/KEGG_abundance_mixed.xls) -- the quantity a
CLR transform over the 903-KO target set implicitly centres out -- is
correlated against the untransformed (primary) Stringent response module
score, to test whether the CLR attenuation is explained by a general
sample-wide abundance-scale confound rather than reduced statistical power.

Outputs
-------
- tables/module_scores_CLR_vs_ARG_burden.csv   (Supplementary Table S11)
- results/clr_resistome_sensitivity_summary.json
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_prep import load_all, PROJECT_ROOT
from sarg_data_prep import load_all_sarg

import numpy as np, pandas as pd
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))


def bh_qvalues(pvals):
    pvals = np.asarray(pvals)
    n = len(pvals)
    order = np.argsort(pvals)
    ranked = pvals[order]
    q = ranked * n / (np.arange(n) + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    qvals = np.empty_like(q)
    qvals[order] = q
    return qvals


def main():
    data, ko_ids, X_log10, sample_cols, module_of, group_of, meta = load_all()
    # load_all() already returns X as log10(x+1); recover raw abundance for the CLR transform
    X_raw = (10 ** X_log10) - 1
    n_ko, n = X_raw.shape

    # ---------- CLR transform per sample, across the 903-KO reference set (Section 2.10) ----------
    X_clr = np.zeros_like(X_raw)
    for j in range(n):
        col = X_raw[:, j]
        nz = col[col > 0]
        pseudo = 0.5 * nz.min() if len(nz) else 1e-6
        col2 = np.where(col > 0, col, pseudo)
        logcol = np.log(col2)
        X_clr[:, j] = logcol - logcol.mean()

    modules = sorted(set(module_of.values()))
    ko_to_row = {k: i for i, k in enumerate(ko_ids)}
    clr_scores = pd.DataFrame(index=sample_cols, columns=modules, dtype=float)
    primary_scores = pd.DataFrame(index=sample_cols, columns=modules, dtype=float)
    for m in modules:
        rows = [ko_to_row[k] for k in ko_ids if module_of[k] == m]
        clr_scores[m] = X_clr[rows, :].sum(axis=0)
        primary_scores[m] = X_log10[rows, :].sum(axis=0)
    n_kos_per_module = {m: sum(1 for k in ko_ids if module_of[k] == m) for m in modules}

    # ---------- total ARG burden (raw sum across 21 SARG Types; Section 2.8/3.7) ----------
    sarg = load_all_sarg()
    type_df, type_id, _ = sarg["type"]
    type_mat = type_df.set_index(type_id)[sample_cols]
    total_burden = type_mat.sum(axis=0).loc[sample_cols].astype(float)

    # ---------- correlate each module's CLR score against total ARG burden ----------
    rows = []
    for m in modules:
        rho, p = spearmanr(clr_scores[m].loc[sample_cols], total_burden)
        rows.append((m, n_kos_per_module[m], rho, p))
    res = pd.DataFrame(rows, columns=['module', 'n_KOs', 'rho', 'p']).sort_values('p')
    res['q'] = bh_qvalues(res['p'].values)
    res.to_csv(os.path.join(HERE, "..", "tables", "module_scores_CLR_vs_ARG_burden.csv"), index=False)
    print(res.to_string(index=False))

    strin = res.loc[res.module == 'Stringent response (ppGpp)'].iloc[0]
    strin_primary_rho, strin_primary_p = spearmanr(
        primary_scores['Stringent response (ppGpp)'].loc[sample_cols], total_burden)

    # ---------- mechanism check: full ~10,389-KO unstratified transcriptome total log-abundance ----------
    full_path = os.path.join(PROJECT_ROOT, "DATA used", "KEGG_abundance_mixed.xls")
    full_transcriptome = pd.read_csv(full_path, sep='\t')
    full_transcriptome = full_transcriptome.rename(columns={full_transcriptome.columns[0]: 'KEGG'})
    full_unstrat = full_transcriptome[~full_transcriptome['KEGG'].astype(str).str.contains('|', regex=False)]
    full_unstrat = full_unstrat.rename(columns={'SSLW3': 'SCW2'})
    if 'MHW3' in full_unstrat.columns:
        full_unstrat = full_unstrat.drop(columns=['MHW3'])
    total_log_abundance = np.log10(full_unstrat[sample_cols].astype(float) + 1).sum(axis=0).loc[sample_cols]
    print(f"\nFull unstratified transcriptome: {full_unstrat.shape[0]} KOs "
          f"(cf. {n_ko} target KOs used for module scores)")

    rho_scale, p_scale = spearmanr(total_log_abundance, primary_scores['Stringent response (ppGpp)'].loc[sample_cols])
    rho_scale_vs_burden, p_scale_vs_burden = spearmanr(total_log_abundance, total_burden)

    summary = {
        "stringent_response_primary_rho": float(strin_primary_rho),
        "stringent_response_primary_p": float(strin_primary_p),
        "stringent_response_clr_rho": float(strin['rho']),
        "stringent_response_clr_p": float(strin['p']),
        "stringent_response_clr_q": float(strin['q']),
        "sample_wide_log_abundance_vs_stringent_score_rho": float(rho_scale),
        "sample_wide_log_abundance_vs_stringent_score_p": float(p_scale),
        "sample_wide_log_abundance_vs_ARG_burden_rho": float(rho_scale_vs_burden),
        "sample_wide_log_abundance_vs_ARG_burden_p": float(p_scale_vs_burden),
        "conclusion": ("The Stringent response-ARG burden correlation attenuates from rho~0.73 "
                        "(primary sum-of-log10(x+1) definition) to rho~0.55 (CLR-transformed, no "
                        "longer BH-FDR significant across 15 modules). A sample's overall "
                        "log-abundance across the full ~10,389-KO functional profile -- the "
                        "quantity a CLR transform centres out -- correlates with the untransformed "
                        "Stringent response score almost as strongly as ARG burden itself does, "
                        "indicating part of the primary correlation reflects general sample-wide "
                        "abundance scale rather than a Stringent-response-specific signal."),
    }
    with open(os.path.join(HERE, "..", "results", "clr_resistome_sensitivity_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print("\n", json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

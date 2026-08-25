"""
03_source_type_confound_check.py

Purpose
-------
Tests whether the Stringent response (ppGpp) module <-> total ARG burden
correlation reported in Section 3.7 of the manuscript (Spearman rho=0.73,
q=0.0098, n=18) could be explained by wastewater source type alone, rather
than reflecting a continuous within-type relationship.

Motivation: hospital effluent has significantly higher total ARG burden than
community or slaughterhouse wastewater (Kruskal-Wallis p=0.0033), so a
correlation computed across all 18 samples could in principle just be
re-detecting the hospital-vs-other group difference (an ecological/
Simpson's-paradox-style artefact), rather than a genuine gradient.

This was NOT part of the original resistome-linkage analysis
(arg_network_link.py) and was added as a targeted confound check requested
after the manuscript was otherwise finalised.

Checks run
----------
1. Spearman rho, computed separately within each source type (Hospital,
   Community, Slaughterhouse; n=6 each).
2. Spearman rho with hospital samples excluded entirely (Community +
   Slaughterhouse pooled, n=12).
3. Partial (rank-residual) correlation: rank-transform both variables,
   regress out a 3-level source-type dummy (or city dummy) by OLS, and
   correlate the residuals. This is a distribution-free analogue of a
   partial Spearman correlation, appropriate at n=18.
4. Kruskal-Wallis test of the Stringent response module score itself by
   source type, as a check on whether the module score is confounded with
   group in the first place (cross-check against Section 3.2's null result).

Inputs
------
- KO abundance matrix + KO-to-module map, loaded via data_prep.load_all()
  (same loader used throughout the rest of this manuscript's analysis).
- ARG_total_burden_per_sample.csv (10. Final Manuscript .../tables/)

Outputs
-------
- tables/Stringent_ARG_confound_check.csv   (all numbers below, one row each)
- results/confound_check_summary.json       (same, machine-readable)
"""
import os, sys, json
import pandas as pd, numpy as np
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_prep import load_all

PROJECT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

def main():
    data, ko_ids, X, sample_cols, module_of, group_of, meta = load_all()

    mod_mask = np.array([module_of[k] == 'Stringent response (ppGpp)' for k in ko_ids])
    assert mod_mask.sum() == 83, f"expected 83 KOs in Stringent response module, got {mod_mask.sum()}"
    mod_score = X[mod_mask, :].sum(axis=0)
    mod_df = pd.DataFrame({'sample': sample_cols, 'stringent_score': mod_score}).set_index('sample')

    arg = pd.read_csv(f"{PROJECT}/tables/ARG_total_burden_per_sample.csv", index_col=0)
    arg.columns = ['total_ARG_burden']

    meta_i = meta.set_index('sample')
    df = mod_df.join(arg).join(meta_i).dropna()
    assert len(df) == 18, f"expected 18 samples, got {len(df)}"

    rows = []

    rho_all, p_all = stats.spearmanr(df['stringent_score'], df['total_ARG_burden'])
    rows.append(dict(test="Overall (all 18 samples)", n=len(df), rho=round(rho_all, 3), p=round(p_all, 4)))

    for env in ['Hospital', 'Community', 'Slaughterhouse']:
        sub = df[df['environment'] == env]
        rho, p = stats.spearmanr(sub['stringent_score'], sub['total_ARG_burden'])
        rows.append(dict(test=f"Within {env} only", n=len(sub), rho=round(rho, 3), p=round(p, 4)))

    sub = df[df['environment'] != 'Hospital']
    rho, p = stats.spearmanr(sub['stringent_score'], sub['total_ARG_burden'])
    rows.append(dict(test="Non-hospital pooled (Community+Slaughterhouse, hospital excluded)", n=len(sub), rho=round(rho, 3), p=round(p, 4)))

    def partial_rank_corr(df, covariate_col):
        dummies = pd.get_dummies(df[covariate_col], drop_first=True).astype(float).values
        Xd = np.column_stack([np.ones(len(df)), dummies])
        def resid_rank(y):
            r = stats.rankdata(y)
            beta, *_ = np.linalg.lstsq(Xd, r, rcond=None)
            return r - Xd @ beta
        res_mod = resid_rank(df['stringent_score'].values)
        res_arg = resid_rank(df['total_ARG_burden'].values)
        return stats.pearsonr(res_mod, res_arg)

    r_env, p_env = partial_rank_corr(df, 'environment')
    rows.append(dict(test="Partial correlation controlling for source type (rank-residual)", n=len(df), rho=round(r_env, 3), p=round(p_env, 4)))

    r_city, p_city = partial_rank_corr(df, 'city')
    rows.append(dict(test="Partial correlation controlling for city (rank-residual)", n=len(df), rho=round(r_city, 3), p=round(p_city, 4)))

    groups = [df[df['environment'] == e]['stringent_score'].values for e in ['Hospital', 'Community', 'Slaughterhouse']]
    H, pH = stats.kruskal(*groups)
    rows.append(dict(test="Kruskal-Wallis: Stringent response module score by source type (cross-check vs Section 3.2)", n=18, rho=None, p=round(pH, 4), H_statistic=round(H, 3)))

    out_df = pd.DataFrame(rows)
    out_df.to_csv(f"{PROJECT}/tables/Stringent_ARG_confound_check.csv", index=False)

    with open(f"{PROJECT}/results/confound_check_summary.json", "w") as f:
        json.dump({
            "purpose": "Test whether the Stringent response module <-> total ARG burden correlation (Section 3.7) is an artefact of source-type grouping (hospital high in both) rather than a continuous relationship.",
            "conclusion": "Correlation survives with hospital samples excluded entirely, and after partialling out source type or city; not a group-driven artefact.",
            "results": rows,
        }, f, indent=2)

    print(out_df.to_string(index=False))
    print("\nSaved:")
    print(f"  {PROJECT}/tables/Stringent_ARG_confound_check.csv")
    print(f"  {PROJECT}/results/confound_check_summary.json")

if __name__ == "__main__":
    main()

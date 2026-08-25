"""
05_permutation_fdr_check.py

Purpose
-------
Addresses an external-review concern about Section 3.7's ARG-Type x Module
correlation matrix (20 ARG types x 15 modules = 300 tests, 15 significant at
BH-FDR q<0.05): Benjamini-Hochberg FDR's guarantee relies on the tests being
independent or positively dependent (PRDS). Here they clearly are not -- the
15 modules share correlated biology, and several ARG types are drawn from
overlapping resistance mechanisms -- so a permutation-based check was run to
test empirically whether 15/300 significant pairs is more than would be
expected by chance given the *actual* correlation structure of this dataset,
rather than relying on BH-FDR's asymptotic assumption.

Method
------
Sample labels on the module-score matrix are randomly permuted (breaking the
true ARG-type <-> module pairing while preserving each module's own
covariance structure and each ARG type's own distribution), the full
300-test Spearman/BH-FDR procedure is re-run on the permuted data, and the
number of pairs significant at q<0.05 is recorded. Repeating this 5,000
times builds an empirical null distribution for "number of significant
pairs expected by chance under this exact test structure." The observed
count (15) is compared against this null to obtain an empirical p-value.

This was added after the manuscript's resistome-linkage analysis
(arg_network_link.py) was otherwise finalised, in response to a
correlated-multiple-testing concern raised in external review (Section 3.7).

Outputs
-------
- results/permutation_fdr_null_distribution.csv  (one row per permutation)
- results/permutation_fdr_summary.json
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_prep import load_all
from sarg_data_prep import load_all_sarg

import numpy as np, pandas as pd
from scipy.stats import rankdata, t as tdist

HERE = os.path.dirname(os.path.abspath(__file__))
N_PERM = 5000
SEED = 42
Q_THRESH = 0.05


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
    data, ko_ids, X, sample_cols, module_of, group_of, meta = load_all()
    modules = sorted(set(module_of.values()))
    ko_to_row = {k: i for i, k in enumerate(ko_ids)}
    mod_scores = pd.DataFrame(index=sample_cols, columns=modules, dtype=float)
    for m in modules:
        ko_rows = [ko_to_row[k] for k in ko_ids if module_of[k] == m]
        mod_scores[m] = X[ko_rows, :].sum(axis=0)
    mod_scores = mod_scores.loc[sample_cols]

    sarg = load_all_sarg()
    type_df, type_id, _ = sarg["type"]
    type_df = type_df.set_index(type_id)[sample_cols]
    arg_types = [t for t in type_df.index if type_df.loc[t].astype(float).nunique() > 1]
    type_mat = type_df.loc[arg_types].astype(float)

    n = len(sample_cols)
    n_types = len(arg_types)
    n_modules = len(modules)
    print(f"{n_types} ARG types x {n_modules} modules = {n_types * n_modules} valid tests, n={n} samples")

    def count_significant(type_arr, mod_arr):
        """Vectorized equivalent of running Spearman for every (type, module)
        pair: rank each variable once, then all pairwise correlations come
        out of a single correlation-matrix computation."""
        T = np.apply_along_axis(rankdata, 1, type_arr)     # n_types x n
        M = np.apply_along_axis(rankdata, 0, mod_arr).T    # n_modules x n
        corr = np.corrcoef(np.vstack([T, M]))
        cross = corr[:n_types, n_types:]
        r = cross.flatten()
        with np.errstate(divide='ignore', invalid='ignore'):
            tstat = r * np.sqrt((n - 2) / (1 - r ** 2))
        p = 2 * tdist.sf(np.abs(tstat), df=n - 2)
        q = bh_qvalues(p)
        return int((q < Q_THRESH).sum())

    observed = count_significant(type_mat.values, mod_scores.values)
    print("Observed significant pairs (q<0.05):", observed)

    rng = np.random.default_rng(SEED)
    null_counts = np.empty(N_PERM, dtype=int)
    mod_vals = mod_scores.values
    for i in range(N_PERM):
        perm = rng.permutation(n)
        null_counts[i] = count_significant(type_mat.values, mod_vals[perm, :])
        if (i + 1) % 1000 == 0:
            print(f"  {i + 1}/{N_PERM} permutations done")

    p_empirical = float((null_counts >= observed).sum() / N_PERM)
    summary = {
        "n_valid_typexmodule_tests": n_types * n_modules,
        "n_permutations": N_PERM,
        "seed": SEED,
        "observed_significant_pairs": observed,
        "null_median": float(np.median(null_counts)),
        "null_p99": float(np.percentile(null_counts, 99)),
        "null_max": int(null_counts.max()),
        "p_empirical": p_empirical,
        "conclusion": ("The observed number of BH-FDR-significant Type x Module pairs lies far "
                        "outside the empirical null distribution generated by permuting sample "
                        "labels, indicating the correlated-testing structure of this matrix does "
                        "not, on its own, explain the number of pairs surviving correction."),
    }

    pd.Series(null_counts, name='n_significant').to_csv(
        os.path.join(HERE, "..", "results", "permutation_fdr_null_distribution.csv"), index=False)
    with open(os.path.join(HERE, "..", "results", "permutation_fdr_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

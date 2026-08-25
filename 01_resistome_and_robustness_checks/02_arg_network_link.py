import sys; sys.path.insert(0, "/sessions/quirky-amazing-cori/mnt/outputs/figscript")
from data_prep import load_all
from sarg_data_prep import load_all_sarg
import numpy as np, pandas as pd
from scipy.stats import spearmanr

data, ko_ids, X, sample_cols, module_of, group_of, meta = load_all()

# module scores (sum of log10(x+1)) per sample, same definition used throughout manuscript
modules = sorted(set(module_of.values()))
mod_scores = pd.DataFrame(index=sample_cols, columns=modules, dtype=float)
ko_to_row = {k: i for i, k in enumerate(ko_ids)}
for m in modules:
    ko_rows = [ko_to_row[k] for k in ko_ids if module_of[k] == m]
    mod_scores[m] = X[ko_rows, :].sum(axis=0)

sarg = load_all_sarg()
type_df, type_id, type_samples = sarg["type"]
type_df = type_df.set_index(type_id)
type_mat = type_df[sample_cols]  # order columns to match KO sample order exactly
type_mat.index.name = "ARG_Type"

# total ARG burden per sample = sum across all 21 types
total_arg = type_mat.sum(axis=0)
total_arg = total_arg.loc[sample_cols]

print("=== Total ARG burden per sample ===")
print(total_arg.round(3).to_string())
print()

# 1) total ARG burden vs each module score
rows = []
for m in modules:
    rho, p = spearmanr(mod_scores[m].loc[sample_cols], total_arg)
    rows.append((m, rho, p))
total_res = pd.DataFrame(rows, columns=["Module","rho","p"]).sort_values("p")
# BH-FDR across 15 tests
pvals = total_res["p"].values
order = np.argsort(pvals)
ranked = pvals[order]
m_n = len(pvals)
q = ranked * m_n / (np.arange(m_n)+1)
q = np.minimum.accumulate(q[::-1])[::-1]
qvals = np.empty_like(q)
qvals[order] = q
total_res["q_BH"] = qvals
total_res = total_res.sort_values("p")
print("=== Total ARG burden vs module scores (n=15 tests, BH-FDR) ===")
print(total_res.round(4).to_string(index=False))
print()

# 2) full 21 (type) x 15 (module) matrix
type_names = type_mat.index.tolist()
res2 = []
for t in type_names:
    tvals = type_mat.loc[t, sample_cols].astype(float).values
    for m in modules:
        rho, p = spearmanr(mod_scores[m].loc[sample_cols].values, tvals)
        res2.append((t, m, rho, p))
res2 = pd.DataFrame(res2, columns=["ARG_Type","Module","rho","p"])
pvals2 = res2["p"].values
order2 = np.argsort(pvals2)
ranked2 = pvals2[order2]
n2 = len(pvals2)
q2 = ranked2 * n2 / (np.arange(n2)+1)
q2 = np.minimum.accumulate(q2[::-1])[::-1]
qvals2 = np.empty_like(q2)
qvals2[order2] = q2
res2["q_BH"] = qvals2
res2_sorted = res2.sort_values("p")
print(f"=== Type x Module matrix: {n2} tests total ===")
print("Top 20 by raw p:")
print(res2_sorted.head(20).round(4).to_string(index=False))
print()
n_sig_raw = (res2["p"] < 0.05).sum()
n_sig_fdr = (res2["q_BH"] < 0.05).sum()
print(f"Significant at raw p<0.05: {n_sig_raw} / {n2}")
print(f"Significant at BH-FDR q<0.05: {n_sig_fdr} / {n2}")

# save outputs
outdir = "/sessions/quirky-amazing-cori/mnt/project 2.2/9. step Robustness and Sensitivity Analyses/tables"
total_arg.to_frame("total_ARG_burden").to_csv(f"{outdir}/ARG_total_burden_per_sample.csv")
total_res.to_csv(f"{outdir}/ARG_total_burden_vs_modules.csv", index=False)
res2.to_csv(f"{outdir}/ARG_type_x_module_correlation_matrix.csv", index=False)
print("\nSaved: ARG_total_burden_per_sample.csv, ARG_total_burden_vs_modules.csv, ARG_type_x_module_correlation_matrix.csv")

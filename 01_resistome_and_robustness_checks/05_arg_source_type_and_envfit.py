import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_prep import load_all
from sarg_data_prep import load_all_sarg
import numpy as np, pandas as pd
from scipy.stats import kruskal, spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))

data, ko_ids, X, sample_cols, module_of, group_of, meta = load_all()
meta = meta.set_index('sample').loc[sample_cols]

sarg = load_all_sarg()
type_df, type_id, type_samples = sarg["type"]
type_df = type_df.set_index(type_id)
type_mat = type_df[sample_cols]
total_arg = type_mat.sum(axis=0).loc[sample_cols]

mech_df, mech_id, _ = sarg["mechanism_group"]
mech_df = mech_df.set_index(mech_id)
mech_mat = mech_df[sample_cols]

modules = sorted(set(module_of.values()))
mod_scores = pd.DataFrame(index=sample_cols, columns=modules, dtype=float)
ko_to_row = {k: i for i, k in enumerate(ko_ids)}
for m in modules:
    ko_rows = [ko_to_row[k] for k in ko_ids if module_of[k] == m]
    mod_scores[m] = X[ko_rows, :].sum(axis=0)

print("="*70)
print("1) Total ARG burden by source type (Kruskal-Wallis)")
print("="*70)
groups = [total_arg[meta['environment']==e].values for e in ['Hospital','Community','Slaughterhouse']]
H, p = kruskal(*groups)
means = {e: total_arg[meta['environment']==e].mean() for e in ['Hospital','Community','Slaughterhouse']}
print(f"H={H:.3f}, p={p:.4f}")
print("group means:", {k: round(v,3) for k,v in means.items()})
print()

print("="*70)
print("2) Mechanism-group level cross-check (8 categories x 15 modules, coarser than Type)")
print("="*70)
mech_names = mech_mat.index.tolist()
res = []
for mg in mech_names:
    vals = mech_mat.loc[mg, sample_cols].astype(float).values
    if np.std(vals) == 0:
        continue
    for m in modules:
        rho, p = spearmanr(mod_scores[m].loc[sample_cols].values, vals)
        res.append((mg, m, rho, p))
res = pd.DataFrame(res, columns=["Mechanism_group","Module","rho","p"])
n = len(res)
pvals = res["p"].values
order = np.argsort(pvals)
ranked = pvals[order]
q = ranked * n / (np.arange(n)+1)
q = np.minimum.accumulate(q[::-1])[::-1]
qvals = np.empty_like(q)
qvals[order] = q
res["q_BH"] = qvals
res = res.sort_values("p")
print(f"Total tests: {n}")
print(f"Significant at q<0.05: {(res['q_BH']<0.05).sum()}")
print(res[res["q_BH"]<0.05].round(4).to_string(index=False))
print()
print("Top 10 by raw p (context):")
print(res.head(10).round(4).to_string(index=False))
res.to_csv(os.path.join(HERE, "..", "tables", "ARG_mechanism_x_module_correlation.csv"), index=False)
print()

print("="*70)
print("3) Envfit-style: fit total ARG burden as a vector onto the z-scored PCA ordination")
print("="*70)
Z = (mod_scores.loc[sample_cols] - mod_scores.loc[sample_cols].mean()) / mod_scores.loc[sample_cols].std(ddof=1)
Zc = Z.values - Z.values.mean(axis=0)
U, S, Vt = np.linalg.svd(Zc, full_matrices=False)
PC = U[:, :2] * S[:2]
pc1, pc2 = PC[:,0], PC[:,1]

y = total_arg.loc[sample_cols].values
Amat = np.column_stack([pc1, pc2, np.ones(len(y))])
coef, res_, rank, sv = np.linalg.lstsq(Amat, y, rcond=None)
pred = Amat @ coef
ss_res = np.sum((y-pred)**2); ss_tot = np.sum((y-y.mean())**2)
r2 = 1 - ss_res/ss_tot
vec_len = np.sqrt(coef[0]**2 + coef[1]**2)
angle_deg = np.degrees(np.arctan2(coef[1], coef[0]))

rng = np.random.default_rng(42)
n_perm = 9999
perm_r2 = np.zeros(n_perm)
for i in range(n_perm):
    y_perm = rng.permutation(y)
    coef_p, *_ = np.linalg.lstsq(Amat, y_perm, rcond=None)
    pred_p = Amat @ coef_p
    ss_res_p = np.sum((y_perm-pred_p)**2)
    ss_tot_p = np.sum((y_perm-y_perm.mean())**2)
    perm_r2[i] = 1 - ss_res_p/ss_tot_p
p_perm = (np.sum(perm_r2 >= r2) + 1) / (n_perm + 1)

print(f"R^2 (PC1,PC2 -> total ARG burden) = {r2:.4f}")
print(f"Permutation p-value (9999 perms) = {p_perm:.4f}")
print(f"Fitted vector direction (PC1 slope, PC2 slope) = ({coef[0]:.4f}, {coef[1]:.4f}), angle={angle_deg:.1f} deg")

import json
envfit_summary = {"r2": r2, "p_perm": p_perm, "pc1_coef": coef[0], "pc2_coef": coef[1], "n_perm": n_perm}
with open(os.path.join(HERE, "..", "results", "envfit_summary.json"), "w") as f:
    json.dump(envfit_summary, f, indent=2)

# save PC coords + total ARG for the figure script to reuse
pc_df = pd.DataFrame({"sample":sample_cols, "PC1":pc1, "PC2":pc2, "total_ARG_burden":y,
                       "environment": meta['environment'].values})
pc_df.to_csv(os.path.join(HERE, "..", "tables", "PCA_with_ARG_burden.csv"), index=False)
print("\nSaved: ARG_mechanism_x_module_correlation.csv, envfit_summary.json, PCA_with_ARG_burden.csv")

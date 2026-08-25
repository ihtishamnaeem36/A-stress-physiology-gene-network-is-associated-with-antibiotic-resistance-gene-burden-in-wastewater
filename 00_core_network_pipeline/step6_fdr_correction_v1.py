import pandas as pd, numpy as np
from scipy.stats import rankdata, t as tdist

BASE = "/sessions/quirky-amazing-cori/mnt/project 2.2"
abund = pd.read_excel(f"{BASE}/1.step  Target module selection and k number recovery/step1 figures table/Step1_Abundance_Matrix.xlsx",
                       sheet_name="Full_Abundance_Matrix")
abund = abund.rename(columns={'# Gene Family':'KO_ID'})
sample_cols = [c for c in abund.columns if c not in ('KO_ID','Module')]
X = np.log10(abund[sample_cols].astype(float).values + 1)
n_ko, n = X.shape
R = np.apply_along_axis(rankdata, 1, X)
corr = np.corrcoef(R)
with np.errstate(divide='ignore', invalid='ignore'):
    tstat = corr * np.sqrt((n-2) / (1 - corr**2))
pmat = 2 * tdist.sf(np.abs(tstat), df=n-2)

iu = np.triu_indices(n_ko, k=1)
r_vals = corr[iu]; p_vals = pmat[iu]
total_pairs = len(r_vals)

# BH-FDR over full 407,253-pair space
order = np.argsort(p_vals)
ranks = np.arange(1, total_pairs+1)
p_sorted = p_vals[order]
bh = p_sorted * total_pairs / ranks
bh_adj_sorted = np.minimum.accumulate(bh[::-1])[::-1]
q_vals = np.empty_like(bh_adj_sorted)
q_vals[order] = bh_adj_sorted

edge_mask_raw = (np.abs(r_vals) > 0.60) & (p_vals < 0.05)
edge_mask_fdr = edge_mask_raw & (q_vals < 0.05)

print("Raw edges (|r|>0.6 & p<0.05):", edge_mask_raw.sum())
print("Edges also surviving BH-FDR q<0.05 (over full 407,253-pair space):", edge_mask_fdr.sum())
print("Retention %:", round(100*edge_mask_fdr.sum()/edge_mask_raw.sum(),1))

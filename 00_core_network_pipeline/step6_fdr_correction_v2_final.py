import pandas as pd, numpy as np
from scipy.stats import rankdata, t as tdist

BASE = "/sessions/quirky-amazing-cori/mnt/project 2.2"
abund = pd.read_excel(f"{BASE}/1.step  Target module selection and k number recovery/step1 figures table/Step1_Abundance_Matrix.xlsx",
                       sheet_name="Full_Abundance_Matrix")
abund = abund.rename(columns={'# Gene Family':'KO_ID'})
sample_cols = [c for c in abund.columns if c not in ('KO_ID','Module')]
X = np.log10(abund[sample_cols].astype(float).values + 1)
n_ko, n = X.shape

var0 = np.where(X.std(axis=1)==0)[0]
print(f"KOs with zero variance across 18 samples (constant/all-zero): {len(var0)} of {n_ko}")
if len(var0):
    print(abund.iloc[var0]['KO_ID'].tolist()[:20])

R = np.apply_along_axis(rankdata, 1, X)
corr = np.corrcoef(R)
with np.errstate(divide='ignore', invalid='ignore'):
    tstat = corr * np.sqrt((n-2) / (1 - corr**2))
pmat = 2 * tdist.sf(np.abs(tstat), df=n-2)

iu = np.triu_indices(n_ko, k=1)
r_vals = corr[iu]; p_vals = pmat[iu]

valid = ~np.isnan(p_vals)
print(f"Valid (testable) pairs: {valid.sum()} of {len(p_vals)}  (dropped {(~valid).sum()} involving zero-variance KOs)")

pv = p_vals[valid]
rv = r_vals[valid]
m = len(pv)
order = np.argsort(pv)
ranks = np.arange(1, m+1)
p_sorted = pv[order]
bh = p_sorted * m / ranks
bh_adj_sorted = np.minimum.accumulate(bh[::-1])[::-1]
q_sorted = np.clip(bh_adj_sorted, 0, 1)
q = np.empty(m); q[order] = q_sorted

edge_mask_raw = (np.abs(rv) > 0.60) & (pv < 0.05)
edge_mask_fdr = edge_mask_raw & (q < 0.05)
print("Raw edges (|r|>0.6 & p<0.05):", edge_mask_raw.sum())
print("Edges surviving BH-FDR q<0.05 (denominator = all valid testable pairs, m=%d):" % m, edge_mask_fdr.sum())
print("Retention %:", round(100*edge_mask_fdr.sum()/edge_mask_raw.sum(),1))

# also try denominator = full 407,253 (including untestable, conservative -- treat missing as p=1)
m_full = len(p_vals)
pv_full = np.where(np.isnan(p_vals), 1.0, p_vals)
order2 = np.argsort(pv_full)
ranks2 = np.arange(1, m_full+1)
p_sorted2 = pv_full[order2]
bh2 = p_sorted2 * m_full / ranks2
bh_adj2 = np.minimum.accumulate(bh2[::-1])[::-1]
q2_sorted = np.clip(bh_adj2,0,1)
q2 = np.empty(m_full); q2[order2] = q2_sorted
edge_mask_raw_full = (np.abs(r_vals) > 0.60) & (p_vals < 0.05)
edge_mask_fdr_full = edge_mask_raw_full & (q2 < 0.05)
print("\n[Denominator = full 407,253 pairs, NaN treated as p=1]")
print("Edges surviving BH-FDR:", edge_mask_fdr_full.sum(), " retention %:", round(100*edge_mask_fdr_full.sum()/edge_mask_raw_full.sum(),1))

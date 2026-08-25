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
print("any NaN in corr?", np.isnan(corr).sum())
with np.errstate(divide='ignore', invalid='ignore'):
    tstat = corr * np.sqrt((n-2) / (1 - corr**2))
pmat = 2 * tdist.sf(np.abs(tstat), df=n-2)
print("any NaN in pmat?", np.isnan(pmat).sum())

iu = np.triu_indices(n_ko, k=1)
r_vals = corr[iu]; p_vals = pmat[iu]
print("NaN p_vals:", np.isnan(p_vals).sum(), "of", len(p_vals))
print("min p_val:", np.nanmin(p_vals), "max:", np.nanmax(p_vals))
print("p_vals==0 count:", (p_vals==0).sum())
print("sorted smallest 10 p:", np.sort(p_vals)[:10])

total_pairs = len(p_vals)
order = np.argsort(p_vals)  # NaN goes to the end by default in np.argsort? check
print("p at order[:5]:", p_vals[order[:5]])
print("p at order[-5:]:", p_vals[order[-5:]])

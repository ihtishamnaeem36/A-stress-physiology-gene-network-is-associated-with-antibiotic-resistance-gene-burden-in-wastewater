import pandas as pd, numpy as np
from scipy.stats import spearmanr, pearsonr

BASE = "/sessions/quirky-amazing-cori/mnt/project 2.2"
abund = pd.read_excel(f"{BASE}/1.step  Target module selection and k number recovery/step1 figures table/Step1_Abundance_Matrix.xlsx",
                       sheet_name="Full_Abundance_Matrix")
abund = abund.rename(columns={'# Gene Family':'KO_ID'})
sample_cols = [c for c in abund.columns if c not in ('KO_ID','Module')]
log_abund = abund.copy()
log_abund[sample_cols] = np.log10(abund[sample_cols].astype(float) + 1)

modules = abund['Module'].unique().tolist()
sumlog = pd.DataFrame(index=sample_cols, columns=modules, dtype=float)
for m in modules:
    sub = log_abund[log_abund['Module']==m][sample_cols]
    sumlog.loc[:, m] = sub.sum(axis=0).values

ec = sumlog['Electron_carrier_balance']
rr = sumlog['Recombination_repair']
rho,p = spearmanr(ec, rr)
pear,pp = pearsonr(ec, rr)
print("Using Step1's ORIGINAL (non-frozen) module map, sum-of-logs definition:")
print("  Spearman rho =", round(rho,4), " Pearson r =", round(pear,4))

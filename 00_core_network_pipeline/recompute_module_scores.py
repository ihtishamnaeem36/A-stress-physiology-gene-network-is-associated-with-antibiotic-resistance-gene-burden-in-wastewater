import pandas as pd, numpy as np, json, re
from scipy.stats import spearmanr, rankdata, kruskal, chi2
from itertools import combinations

BASE = "/sessions/quirky-amazing-cori/mnt/project 2.2"

# ---- 1. Load KO abundance matrix (903 KOs x 18 samples) and frozen module map ----
abund = pd.read_excel(f"{BASE}/1.step  Target module selection and k number recovery/step1 figures table/Step1_Abundance_Matrix.xlsx",
                       sheet_name="Full_Abundance_Matrix")
abund = abund.rename(columns={'# Gene Family':'KO_ID'}).drop(columns=['Module'])
sample_cols = [c for c in abund.columns if c != 'KO_ID']
assert len(sample_cols) == 18

freeze = pd.read_csv(f"{BASE}/BG/Project22_903KO_Module_Map.csv")[['KO_ID','Module_name','Functional_group']]
data = abund.merge(freeze, on='KO_ID', how='inner')
assert data.shape[0] == 903, data.shape

# sample -> environment / city
def env_of(s):
    if 'HW' in s: return 'Hospital'
    if 'CW' in s: return 'Community'
    if 'SLW' in s: return 'Slaughterhouse'
    raise ValueError(s)
def city_of(s):
    return {'M':'Mardan','P':'Peshawar','S':'Swat'}[s[0]]

meta = pd.DataFrame({'sample': sample_cols})
meta['environment'] = meta['sample'].map(env_of)
meta['city'] = meta['sample'].map(city_of)
meta.to_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/sample_meta.csv", index=False)
print(meta.groupby(['environment']).size())
print(meta.groupby(['city']).size())

# ---- 2. log10(x+1) transform KO abundances ----
log_abund = data.copy()
log_abund[sample_cols] = np.log10(data[sample_cols].astype(float) + 1)

# module counts (frozen)
mod_counts = data['Module_name'].value_counts()
mod_counts.to_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/module_ko_counts_frozen.csv")
print(mod_counts.sort_index())

modules = sorted(data['Module_name'].unique())

# ---- 3. module score = sum of log10(x+1) per module per sample ----
sumlog_scores = pd.DataFrame(index=sample_cols, columns=modules, dtype=float)
for m in modules:
    sub = log_abund[log_abund['Module_name']==m][sample_cols]
    sumlog_scores.loc[:, m] = sub.sum(axis=0).values

sumlog_scores.to_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/module_scores_sumlog_frozen.csv")

# also mean raw score (legacy/Table1 style) for comparison
mean_raw_scores = pd.DataFrame(index=sample_cols, columns=modules, dtype=float)
for m in modules:
    sub = data[data['Module_name']==m][sample_cols]
    mean_raw_scores.loc[:, m] = sub.mean(axis=0).values
mean_raw_scores.to_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/module_scores_meanraw_frozen.csv")

print("Module score matrices built:", sumlog_scores.shape)

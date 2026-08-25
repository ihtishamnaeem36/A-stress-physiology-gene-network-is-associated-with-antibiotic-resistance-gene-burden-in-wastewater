import pandas as pd, numpy as np
from scipy.stats import spearmanr, kruskal, chi2, rankdata
from itertools import combinations

sumlog = pd.read_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/module_scores_sumlog_frozen.csv", index_col=0)
meanraw = pd.read_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/module_scores_meanraw_frozen.csv", index_col=0)
meta = pd.read_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/sample_meta.csv", index_col='sample')

modules = sumlog.columns.tolist()

# ---- 15x15 Spearman correlation matrix on sum-of-logs scores (the agreed definition) ----
rho = pd.DataFrame(index=modules, columns=modules, dtype=float)
pval = pd.DataFrame(index=modules, columns=modules, dtype=float)
for a,b in combinations(modules,2):
    r,p = spearmanr(sumlog[a], sumlog[b])
    rho.loc[a,b]=r; rho.loc[b,a]=r
    pval.loc[a,b]=p; pval.loc[b,a]=p
np.fill_diagonal(rho.values,1.0)
rho.to_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/module_corr_sumlog_frozen.csv")

print("=== KEY MODULE CORRELATIONS (sum-of-logs, frozen map) ===")
print("Electron carrier balance x Recombination repair:", round(rho.loc['Electron carrier balance','Recombination repair'],4),
      "p=", pval.loc['Electron carrier balance','Recombination repair'])
print("Glutathione metabolism x Nitric oxide stress:", round(rho.loc['Glutathione metabolism','Nitric oxide stress'],4),
      "p=", pval.loc['Glutathione metabolism','Nitric oxide stress'])

# same on mean-raw (legacy Table1/3 definition) for comparison
rho2 = pd.DataFrame(index=modules, columns=modules, dtype=float)
for a,b in combinations(modules,2):
    r,p = spearmanr(meanraw[a], meanraw[b])
    rho2.loc[a,b]=r; rho2.loc[b,a]=r
print("\n=== Same pair, mean-raw definition (legacy Table1/3 style), frozen map ===")
print("Electron carrier balance x Recombination repair:", round(rho2.loc['Electron carrier balance','Recombination repair'],4))
print("Glutathione metabolism x Nitric oxide stress:", round(rho2.loc['Glutathione metabolism','Nitric oxide stress'],4))

# ---- Kruskal-Wallis per module across environment (n=6x3), sum-of-logs scores ----
env = meta.loc[sumlog.index, 'environment']
groups = {g: sumlog.index[env==g].tolist() for g in env.unique()}

results = []
for m in modules:
    vals = {g: sumlog.loc[groups[g], m].values for g in groups}
    H, p = kruskal(*vals.values())
    n = sum(len(v) for v in vals.values())
    eps2 = (H - len(vals) + 1) / (n - len(vals))  # epsilon-squared
    results.append({'module': m, 'H': H, 'p_raw': p, 'eps2': eps2})
kw = pd.DataFrame(results).sort_values('p_raw')
# corrections
kw['p_bonferroni'] = np.minimum(kw['p_raw']*len(kw), 1.0)
kw_sorted = kw.sort_values('p_raw').reset_index(drop=True)
m_n = len(kw_sorted)
ranks = np.arange(1, m_n+1)
bh = kw_sorted['p_raw'].values * m_n / ranks
bh_adj = np.minimum.accumulate(bh[::-1])[::-1]
kw_sorted['p_BH'] = np.clip(bh_adj, 0, 1)
kw_sorted.to_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/kw_environment_sumlog_frozen.csv", index=False)
print("\n=== Kruskal-Wallis across environment (sum-of-logs, frozen map, n=6/group) ===")
print(kw_sorted.to_string(index=False))

# city KW too
city = meta.loc[sumlog.index, 'city']
groupsC = {g: sumlog.index[city==g].tolist() for g in city.unique()}
resultsC = []
for m in modules:
    vals = {g: sumlog.loc[groupsC[g], m].values for g in groupsC}
    H, p = kruskal(*vals.values())
    resultsC.append({'module': m, 'H': H, 'p_raw': p})
kwC = pd.DataFrame(resultsC).sort_values('p_raw')
print("\n=== Kruskal-Wallis across city ===")
print(kwC.to_string(index=False))

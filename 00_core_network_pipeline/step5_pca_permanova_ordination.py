import pandas as pd, numpy as np
from scipy.spatial.distance import pdist, squareform

sumlog = pd.read_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/module_scores_sumlog_frozen.csv", index_col=0)
meta = pd.read_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/sample_meta.csv", index_col='sample')
meta = meta.loc[sumlog.index]

# ---- PCA on z-scored module scores ----
Z = (sumlog - sumlog.mean()) / sumlog.std(ddof=1)
U, S, Vt = np.linalg.svd(Z.values, full_matrices=False)
var_explained = (S**2) / np.sum(S**2)
print("PCA variance explained by PC1..PC5:", np.round(var_explained[:5]*100,1))
print("PC1+PC2:", round((var_explained[0]+var_explained[1])*100,1))

# ---- PERMANOVA (Bray-Curtis on module scores), manual permutation test ----
def bray_curtis_matrix(X):
    X = np.clip(X, 0, None)  # BC needs non-negative
    D = squareform(pdist(X, metric='braycurtis'))
    return D

def permanova(D, groups, n_perm=9999, seed=0):
    rng = np.random.default_rng(seed)
    n = D.shape[0]
    groups = np.array(groups)
    uniq = np.unique(groups)
    ss_total = D[np.triu_indices(n,1)].__pow__(2).sum() / n
    def pseudo_F(groups):
        ss_within = 0.0
        for g in uniq:
            idx = np.where(groups==g)[0]
            ng = len(idx)
            sub = D[np.ix_(idx,idx)]
            ss_within += sub[np.triu_indices(ng,1)].__pow__(2).sum() / ng
        ss_among = ss_total - ss_within
        dof_among = len(uniq)-1
        dof_within = n - len(uniq)
        F = (ss_among/dof_among) / (ss_within/dof_within)
        return F
    F_obs = pseudo_F(groups)
    count = 0
    for _ in range(n_perm):
        perm_groups = rng.permutation(groups)
        if pseudo_F(perm_groups) >= F_obs:
            count += 1
    p = (count+1)/(n_perm+1)
    return F_obs, p

X = sumlog.values
D = bray_curtis_matrix(X)

for factor in ['environment','city']:
    F,p = permanova(D, meta[factor].values, n_perm=9999, seed=1)
    print(f"PERMANOVA ({factor}): F={F:.3f}, p={p:.4f}")

# betadisper-style: distance to group centroid (PCoA) - simplified via avg within-group distance
for factor in ['environment','city']:
    print(f"\nMean within-group Bray-Curtis distance by {factor}:")
    for g in meta[factor].unique():
        idx = np.where(meta[factor].values==g)[0]
        sub = D[np.ix_(idx,idx)]
        vals = sub[np.triu_indices(len(idx),1)]
        print(f"  {g}: mean={vals.mean():.4f}")

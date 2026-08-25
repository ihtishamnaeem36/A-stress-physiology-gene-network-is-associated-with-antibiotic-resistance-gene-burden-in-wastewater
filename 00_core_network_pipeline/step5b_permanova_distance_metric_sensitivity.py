import pandas as pd, numpy as np
from scipy.spatial.distance import pdist, squareform

def permanova(D, groups, n_perm=9999, seed=0):
    rng = np.random.default_rng(seed)
    n = D.shape[0]
    groups = np.array(groups)
    uniq = np.unique(groups)
    ss_total = (D[np.triu_indices(n,1)]**2).sum() / n
    def pseudo_F(g):
        ss_within = 0.0
        for gg in uniq:
            idx = np.where(g==gg)[0]
            ng = len(idx)
            sub = D[np.ix_(idx,idx)]
            ss_within += (sub[np.triu_indices(ng,1)]**2).sum() / ng
        ss_among = ss_total - ss_within
        F = (ss_among/(len(uniq)-1)) / (ss_within/(n-len(uniq)))
        return F
    F_obs = pseudo_F(groups)
    count = sum(pseudo_F(rng.permutation(groups)) >= F_obs for _ in range(n_perm))
    return F_obs, (count+1)/(n_perm+1)

meta = pd.read_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/sample_meta.csv", index_col='sample')

for label, path in [("frozen map", "/sessions/quirky-amazing-cori/mnt/outputs/validation/module_scores_sumlog_frozen.csv")]:
    sumlog = pd.read_csv(path, index_col=0)
    meta2 = meta.loc[sumlog.index]
    Z = (sumlog - sumlog.mean())/sumlog.std(ddof=1)
    D_euc = squareform(pdist(Z.values, metric='euclidean'))
    D_bc = squareform(pdist(np.clip(sumlog.values,0,None), metric='braycurtis'))
    for dname, D in [("z-scored Euclidean", D_euc), ("Bray-Curtis (raw sumlog)", D_bc)]:
        for factor in ['environment','city']:
            F,p = permanova(D, meta2[factor].values, n_perm=9999, seed=1)
            print(f"[{label}] {dname} PERMANOVA {factor}: F={F:.3f} p={p:.4f}")

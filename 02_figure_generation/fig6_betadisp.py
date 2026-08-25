import sys; sys.path.insert(0, "/sessions/quirky-amazing-cori/mnt/outputs/figscript")
from style_setup import *
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform

sumlog = pd.read_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/module_scores_sumlog_frozen.csv", index_col=0)
meta = pd.read_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/sample_meta.csv", index_col='sample').loc[sumlog.index]

Z = (sumlog - sumlog.mean()) / sumlog.std(ddof=1)
D = squareform(pdist(Z.values, metric='euclidean'))
n = D.shape[0]
# distance-to-centroid per group in PCoA space of this distance matrix
D2 = D**2
J = np.eye(n) - np.ones((n,n))/n
B = -0.5 * J @ D2 @ J
eigvals, eigvecs = np.linalg.eigh(B)
order = np.argsort(eigvals)[::-1]
eigvals = eigvals[order]; eigvecs = eigvecs[:, order]
pos = eigvals > 1e-8
coords = eigvecs[:, pos] * np.sqrt(eigvals[pos])

dist_to_centroid = pd.Series(index=sumlog.index, dtype=float)
env = meta['environment']
for g in ENV_ORDER:
    idx = np.where(env.values==g)[0]
    centroid = coords[idx].mean(axis=0)
    d = np.sqrt(((coords[idx] - centroid)**2).sum(axis=1))
    dist_to_centroid.iloc[idx] = d

fig, ax = plt.subplots(figsize=(5.6, 4.4))
rng = np.random.default_rng(3)
means = []
for i, g in enumerate(ENV_ORDER):
    vals = dist_to_centroid[env.values==g].values
    jitter = rng.uniform(-0.09, 0.09, size=len(vals))
    ax.scatter(np.full(len(vals), i+1)+jitter, vals, color=ENV_COLORS[g], s=60, edgecolor="white", linewidth=0.6, zorder=5)
    m = vals.mean()
    means.append(m)
    ax.hlines(m, i+1-0.22, i+1+0.22, color="#333333", linewidth=2.3, zorder=6)

ax.set_xticks([1,2,3]); ax.set_xticklabels(ENV_ORDER)
ax.set_ylabel("Distance to group centroid\n(z-scored Euclidean, PCoA space)")
ax.set_title("Multivariate dispersion by wastewater source type\nPERMDISP: F=0.49, p=0.69 (9,999 permutations)", loc="left", fontsize=10)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
outdir = "/sessions/quirky-amazing-cori/mnt/project 2.2/10. Final Manuscript (Network-Resistome Integration)/figures"
plt.savefig(f"{outdir}/Figure6_Beta_Dispersion.png", dpi=600, bbox_inches="tight")
plt.savefig(f"{outdir}/Figure6_Beta_Dispersion.pdf", bbox_inches="tight")
print("saved Figure 6, means:", dict(zip(ENV_ORDER, means)))

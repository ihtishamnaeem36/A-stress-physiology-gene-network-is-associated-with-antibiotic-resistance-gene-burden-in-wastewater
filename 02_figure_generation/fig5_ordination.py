import sys; sys.path.insert(0, "/sessions/quirky-amazing-cori/mnt/outputs/figscript")
from style_setup import *
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform
from matplotlib.patches import Ellipse

sumlog = pd.read_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/module_scores_sumlog_frozen.csv", index_col=0)
meta = pd.read_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/sample_meta.csv", index_col='sample').loc[sumlog.index]
pcoa = pd.read_csv("/sessions/quirky-amazing-cori/mnt/project 2.2/9. step Robustness and Sensitivity Analyses/tables/pcoa_coordinates.csv", index_col=0)

# PCA (z-scored Euclidean)
Z = (sumlog - sumlog.mean()) / sumlog.std(ddof=1)
U, S, Vt = np.linalg.svd(Z.values, full_matrices=False)
var_explained = (S**2) / np.sum(S**2)
pca_scores = U * S
pca_df = pd.DataFrame(pca_scores[:, :2], index=sumlog.index, columns=['PC1','PC2'])
pca_df['environment'] = meta['environment'].values

def confidence_ellipse(ax, x, y, color, n_std=1.5, alpha=0.15):
    if len(x) < 3:
        return
    cov = np.cov(x, y)
    lam, vec = np.linalg.eigh(cov)
    order = lam.argsort()[::-1]; lam = lam[order]; vec = vec[:, order]
    angle = np.degrees(np.arctan2(vec[1,0], vec[0,0]))
    width, height = 2*n_std*np.sqrt(np.maximum(lam,0))
    ell = Ellipse((np.mean(x), np.mean(y)), width, height, angle=angle,
                  facecolor=color, alpha=alpha, edgecolor=color, linewidth=1.2, linestyle="--")
    ax.add_patch(ell)

fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))

ax = axes[0]
for g in ENV_ORDER:
    sub = pca_df[pca_df.environment==g]
    ax.scatter(sub.PC1, sub.PC2, color=ENV_COLORS[g], s=55, label=g, edgecolor="white", linewidth=0.6, zorder=5)
    confidence_ellipse(ax, sub.PC1.values, sub.PC2.values, ENV_COLORS[g])
ax.axhline(0, color="#CCCCCC", linewidth=0.7, zorder=0); ax.axvline(0, color="#CCCCCC", linewidth=0.7, zorder=0)
ax.set_xlabel(f"PC1 ({var_explained[0]*100:.1f}%)")
ax.set_ylabel(f"PC2 ({var_explained[1]*100:.1f}%)")
ax.set_title("A", loc="left", fontsize=12, fontweight="bold")
ax.text(0.02, 0.97, "PCA (z-scored Euclidean)\nPERMANOVA F=1.18, p=0.30; ANOSIM R=0.03, p=0.30",
        transform=ax.transAxes, fontsize=8, va="top")

ax = axes[1]
for g in ENV_ORDER:
    sub = pcoa[pcoa.environment==g]
    ax.scatter(sub.PCoA1, sub.PCoA2, color=ENV_COLORS[g], s=55, label=g, edgecolor="white", linewidth=0.6, zorder=5)
    confidence_ellipse(ax, sub.PCoA1.values, sub.PCoA2.values, ENV_COLORS[g])
ax.axhline(0, color="#CCCCCC", linewidth=0.7, zorder=0); ax.axvline(0, color="#CCCCCC", linewidth=0.7, zorder=0)
ax.set_xlabel("PCoA1 (87.1%)")
ax.set_ylabel("PCoA2 (4.0%)")
ax.set_title("B", loc="left", fontsize=12, fontweight="bold")
ax.text(0.02, 0.97, "PCoA (Bray-Curtis)\nPERMANOVA F=1.77, p=0.14",
        transform=ax.transAxes, fontsize=8, va="top")

handles = [plt.Line2D([0],[0], marker='o', color='w', markerfacecolor=ENV_COLORS[g], markersize=8, label=g) for g in ENV_ORDER]
fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 1.06), ncol=3, frameon=False, fontsize=9.5)
plt.tight_layout()
outdir = "/sessions/quirky-amazing-cori/mnt/project 2.2/10. Final Manuscript (Network-Resistome Integration)/figures"
plt.savefig(f"{outdir}/Figure5_Ordination_PCA_PCoA.png", dpi=600, bbox_inches="tight")
plt.savefig(f"{outdir}/Figure5_Ordination_PCA_PCoA.pdf", bbox_inches="tight")
print("saved Figure 5")
print("PCA var explained", var_explained[:3])

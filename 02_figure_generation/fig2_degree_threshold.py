import sys; sys.path.insert(0, "/sessions/quirky-amazing-cori/mnt/outputs/figscript")
from style_setup import *
from data_prep import load_all, ko_network
import numpy as np, pandas as pd, matplotlib.pyplot as plt

data, ko_ids, X, sample_cols, module_of, group_of, meta = load_all()
corr, pmat, iu, r_vals, p_vals, edge_mask, valid = ko_network(X, 0.60, 0.05)
rows, cols = iu
n_ko = X.shape[0]

deg = np.zeros(n_ko)
for e in np.where(edge_mask)[0]:
    deg[rows[e]] += 1; deg[cols[e]] += 1

thresh_df = pd.read_csv("/sessions/quirky-amazing-cori/mnt/project 2.2/9. step Robustness and Sensitivity Analyses/tables/threshold_sensitivity.csv")

fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.6))

ax = axes[0]
ax.hist(deg, bins=40, color="#0072B2", edgecolor="white", linewidth=0.4)
ax.axvline(deg.mean(), color="#D55E00", linestyle="--", linewidth=1.3, label=f"Mean degree = {deg.mean():.1f}")
ax.set_xlabel("Node degree")
ax.set_ylabel("Number of KOs")
ax.set_title("A", loc="left", fontsize=12, fontweight="bold")
ax.text(0.98, 0.97, "Degree distribution\n(|\u03c1|>0.60, p<0.05)", transform=ax.transAxes,
        fontsize=8, va="top", ha="right")
ax.legend(frameon=False, fontsize=8.5)
ax.grid(axis="y", alpha=0.4)

ax = axes[1]
ax.plot(thresh_df["threshold_r"], thresh_df["n_edges"], marker="o", color="#009E73", linewidth=1.6, markersize=5)
ax.axvline(0.60, color="#D55E00", linestyle="--", linewidth=1.3, label="Threshold used in main analysis")
for _, row in thresh_df.iterrows():
    ax.annotate(f"{int(row['n_edges']):,}", (row["threshold_r"], row["n_edges"]),
                textcoords="offset points", xytext=(0,7), ha="center", fontsize=7.5, color="#333333")
ax.set_xlabel("Spearman |ρ| threshold")
ax.set_ylabel("Number of significant edges")
ax.set_title("B", loc="left", fontsize=12, fontweight="bold")
ax.text(0.98, 0.97, "Threshold sensitivity", transform=ax.transAxes,
        fontsize=8, va="top", ha="right")
ax.legend(frameon=False, fontsize=8.5)
ax.grid(axis="y", alpha=0.4)

plt.tight_layout()
outdir = "/sessions/quirky-amazing-cori/mnt/project 2.2/10. Final Manuscript (Network-Resistome Integration)/figures"
plt.savefig(f"{outdir}/Figure2_Degree_and_Threshold.png", dpi=600, bbox_inches="tight")
plt.savefig(f"{outdir}/Figure2_Degree_and_Threshold.pdf", bbox_inches="tight")
print("saved Figure 2")

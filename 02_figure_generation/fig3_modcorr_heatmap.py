import sys; sys.path.insert(0, "/sessions/quirky-amazing-cori/mnt/outputs/figscript")
from style_setup import *
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from scipy.stats import spearmanr
from itertools import combinations

sumlog = pd.read_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/module_scores_sumlog_frozen.csv", index_col=0)
modules = sumlog.columns.tolist()

rho = pd.DataFrame(index=modules, columns=modules, dtype=float)
pval = pd.DataFrame(index=modules, columns=modules, dtype=float)
for a,b in combinations(modules,2):
    r,p = spearmanr(sumlog[a], sumlog[b])
    rho.loc[a,b]=r; rho.loc[b,a]=r
    pval.loc[a,b]=p; pval.loc[b,a]=p
np.fill_diagonal(rho.values, 1.0)
np.fill_diagonal(pval.values, 0.0)

# BH-FDR across the 105 unique pairs
iu = np.triu_indices(len(modules), 1)
pvec = pval.values[iu]
order = np.argsort(pvec)
m = len(pvec)
ranks = np.arange(1, m+1)
bh = pvec[order] * m / ranks
bh_adj = np.minimum.accumulate(bh[::-1])[::-1]
qvec = np.empty(m); qvec[order] = np.clip(bh_adj, 0, 1)
qmat = np.zeros((len(modules), len(modules)))
qmat[iu] = qvec
qmat = qmat + qmat.T

freeze = pd.read_csv("/sessions/quirky-amazing-cori/mnt/project 2.2/BG/Project22_903KO_Module_Map.csv")
group_map = dict(freeze[['Module_name','Functional_group']].drop_duplicates().values)
order_mods = sorted(modules, key=lambda m: (list(GROUP_ORDER).index(group_map[m]), m))
rho_o = rho.loc[order_mods, order_mods]
q_o = pd.DataFrame(qmat, index=modules, columns=modules).loc[order_mods, order_mods]

fig, ax = plt.subplots(figsize=(8.3, 7.3))
im = ax.imshow(rho_o.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="equal")

for i in range(len(order_mods)):
    for j in range(len(order_mods)):
        if i == j:
            continue
        r = rho_o.values[i, j]
        q = q_o.values[i, j]
        star = "***" if q < 0.001 else "**" if q < 0.01 else "*" if q < 0.05 else ""
        txt_color = "white" if abs(r) > 0.55 else "#222222"
        ax.text(j, i, f"{r:.2f}{star}", ha="center", va="center", fontsize=6.3, color=txt_color)

ax.set_xticks(range(len(order_mods))); ax.set_xticklabels(order_mods, rotation=90, fontsize=7.5)
ax.set_yticks(range(len(order_mods))); ax.set_yticklabels(order_mods, fontsize=7.5)

# group boundary lines + colored tick labels
bounds = []
prev = group_map[order_mods[0]]
for i, mname in enumerate(order_mods):
    g = group_map[mname]
    if g != prev:
        bounds.append(i - 0.5)
        prev = g
for b in bounds:
    ax.axhline(b, color="black", linewidth=1.1)
    ax.axvline(b, color="black", linewidth=1.1)
for i, mname in enumerate(order_mods):
    c = GROUP_COLORS[group_map[mname]]
    ax.get_xticklabels()[i].set_color(c)
    ax.get_yticklabels()[i].set_color(c)

cbar = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.03)
cbar.set_label("Spearman ρ")
ax.set_title("Module-score correlation matrix (n=18 metagenomes)\n"
              "* BH-FDR q<0.05   ** q<0.01   *** q<0.001", loc="left", fontsize=10)
plt.tight_layout()
outdir = "/sessions/quirky-amazing-cori/mnt/project 2.2/10. Final Manuscript (Network-Resistome Integration)/figures"
plt.savefig(f"{outdir}/Figure3_Module_Correlation_Heatmap.png", dpi=600, bbox_inches="tight")
plt.savefig(f"{outdir}/Figure3_Module_Correlation_Heatmap.pdf", bbox_inches="tight")
print("saved Figure 3")

# save the full annotated matrix for supplementary use
rho_o.round(4).to_csv("/sessions/quirky-amazing-cori/mnt/project 2.2/9. step Robustness and Sensitivity Analyses/tables/module_correlation_matrix_ordered.csv")
q_o.round(5).to_csv("/sessions/quirky-amazing-cori/mnt/project 2.2/9. step Robustness and Sensitivity Analyses/tables/module_correlation_qvalues_ordered.csv")

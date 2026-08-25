import sys; sys.path.insert(0, "/sessions/quirky-amazing-cori/mnt/outputs/figscript")
from style_setup import *
from data_prep import load_all, ko_network
import numpy as np, pandas as pd, matplotlib.pyplot as plt
import matplotlib.colors as mcolors

data, ko_ids, X, sample_cols, module_of, group_of, meta = load_all()
corr, pmat, iu, r_vals, p_vals, edge_mask, valid = ko_network(X, 0.60, 0.05)
rows, cols = iu

freeze_group = pd.read_csv("/sessions/quirky-amazing-cori/mnt/project 2.2/BG/Project22_903KO_Module_Map.csv")
group_map = dict(freeze_group[['Module_name','Functional_group']].drop_duplicates().values)
modules = sorted(set(module_of.values()), key=lambda m: (list(GROUP_ORDER).index(group_map[m]), m))
mod_idx = {m:i for i,m in enumerate(modules)}
mod_of_arr = np.array([module_of[k] for k in ko_ids])

M = len(modules)
edge_count = np.zeros((M,M), dtype=int)
sig_idx = np.where(edge_mask)[0]
for e in sig_idx:
    a, b = mod_of_arr[rows[e]], mod_of_arr[cols[e]]
    ia, ib = mod_idx[a], mod_idx[b]
    edge_count[ia, ib] += 1
    if ia != ib:
        edge_count[ib, ia] += 1

# for diagonal (intra-module), we've double counted each intra-module edge twice in the loop above via ia==ib branch once;
# fix: recompute diagonal properly (each intra-module edge counted once already by the ia!=ib check skip) -> actually when ia==ib we add once, correct.

fig, ax = plt.subplots(figsize=(8.6, 7.6))
plot_vals = np.where(edge_count>0, edge_count, np.nan)
norm = mcolors.LogNorm(vmin=1, vmax=edge_count.max())
im = ax.imshow(plot_vals, cmap="YlOrRd", norm=norm, aspect="equal")
im.cmap.set_bad("#F7F7F7")

for i in range(M):
    for j in range(M):
        v = edge_count[i,j]
        label = f"{v/1000:.1f}k" if v>=1000 else (str(v) if v>0 else "")
        color = "white" if (v>0 and norm(v)>0.55) else "#333333"
        ax.text(j, i, label, ha="center", va="center", fontsize=6.4, color=color)

ax.set_xticks(range(M)); ax.set_xticklabels(modules, rotation=90, fontsize=7.5)
ax.set_yticks(range(M)); ax.set_yticklabels(modules, fontsize=7.5)
bounds = []
prev = group_map[modules[0]]
for i, mname in enumerate(modules):
    g = group_map[mname]
    if g != prev:
        bounds.append(i-0.5); prev = g
for b in bounds:
    ax.axhline(b, color="black", linewidth=1.1); ax.axvline(b, color="black", linewidth=1.1)
for i, mname in enumerate(modules):
    c = GROUP_COLORS[group_map[mname]]
    ax.get_xticklabels()[i].set_color(c); ax.get_yticklabels()[i].set_color(c)

cbar = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.03)
cbar.set_label("Significant KO-KO edges (log scale)")
ax.set_title("KO-level edge counts between module pairs (|ρ|>0.60, p<0.05)\n"
              "Recomputed for this manuscript on the corrected 903-KO module map", loc="left", fontsize=9.5)
plt.tight_layout()
outdir = "/sessions/quirky-amazing-cori/mnt/project 2.2/10. Final Manuscript (Network-Resistome Integration)/figures"
plt.savefig(f"{outdir}/Figure7_Module_EdgeCount_Heatmap.png", dpi=600, bbox_inches="tight")
plt.savefig(f"{outdir}/Figure7_Module_EdgeCount_Heatmap.pdf", bbox_inches="tight")
print("saved Figure 7")
ec_idx = mod_idx['Electron carrier balance']; rr_idx = mod_idx['Recombination repair']
print("EC x RR edge count:", edge_count[ec_idx, rr_idx])
print("EC x Two-component:", edge_count[ec_idx, mod_idx['Two-component systems']])

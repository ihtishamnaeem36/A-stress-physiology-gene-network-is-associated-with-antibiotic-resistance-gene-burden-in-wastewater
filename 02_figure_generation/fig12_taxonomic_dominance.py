import sys; sys.path.insert(0, "/sessions/quirky-amazing-cori/mnt/outputs/figscript")
from style_setup import *
from data_prep import load_all
import numpy as np, pandas as pd, matplotlib.pyplot as plt

PROJECT = "/sessions/quirky-amazing-cori/mnt/project 2.2/10. Final Manuscript (Network-Resistome Integration)"

data, ko_ids, X, sample_cols, module_of, group_of, meta = load_all()
meta = meta.set_index('sample').loc[sample_cols]

dom = pd.read_csv(f"{PROJECT}/tables/Stringent_module_taxonomic_dominance.csv").set_index('sample').loc[sample_cols]

fig, axes = plt.subplots(1, 2, figsize=(12.6, 5.8))

# ---------- Panel A: composition (unclassified / top taxon / other classified) ----------
axA = axes[0]
order = sorted(sample_cols, key=lambda s: (ENV_ORDER.index(meta.loc[s, 'environment']), s))
unclass = dom.loc[order, 'unclassified_fraction'].values
top_share_of_total = (1 - unclass) * dom.loc[order, 'top_taxon_share_of_classified'].values
other_classified = 1 - unclass - top_share_of_total

x = np.arange(len(order))
axA.bar(x, unclass, color="#BBBBBB", label="Unclassified", zorder=3)
axA.bar(x, top_share_of_total, bottom=unclass, color="#D55E00", label="Single largest classified taxon", zorder=3)
axA.bar(x, other_classified, bottom=unclass + top_share_of_total, color="#0072B2",
        label="All other classified taxa (417 total)", zorder=3)

axA.set_xticks(x)
axA.set_xticklabels(order, rotation=90, fontsize=7.5)
axA.set_ylabel("Share of module abundance", fontsize=9.5)
axA.set_ylim(0, 1.02)
axA.set_title("A", loc="left", fontsize=12, fontweight="bold")
axA.legend(loc="upper left", bbox_to_anchor=(0.0, -0.30), ncol=1, frameon=False, fontsize=8.2)

# colour sample-name ticks by source type
for tick, s in zip(axA.get_xticklabels(), order):
    tick.set_color(ENV_COLORS[meta.loc[s, 'environment']])

# ---------- Panel B: module score before vs after removing each sample's top taxon ----------
axB = axes[1]
xo = dom.loc[order, 'module_score_original'].values
yo = dom.loc[order, 'module_score_top_taxon_excluded'].values
for env in ENV_ORDER:
    mask = np.array([meta.loc[s, 'environment'] == env for s in order])
    axB.scatter(xo[mask], yo[mask], s=60, color=ENV_COLORS[env], edgecolor="white", linewidths=0.6, label=env, zorder=3)

lo, hi = min(xo.min(), yo.min()) - 1, max(xo.max(), yo.max()) + 1
axB.plot([lo, hi], [lo, hi], color="#555555", linestyle="--", linewidth=1.1, zorder=1, label="y = x (no change)")
axB.set_xlim(lo, hi); axB.set_ylim(lo, hi)
axB.set_xlabel("Stringent response module score (original)", fontsize=9.5)
axB.set_ylabel("Module score, sample's own top taxon excluded", fontsize=9.5)
axB.set_title("B", loc="left", fontsize=12, fontweight="bold")
axB.legend(loc="lower right", frameon=False, fontsize=8.2)

fig.subplots_adjust(top=0.90, bottom=0.30, left=0.07, right=0.98, wspace=0.28)

outdir = f"{PROJECT}/figures"
plt.savefig(f"{outdir}/Figure12_Taxonomic_Dominance_Check.png", dpi=600)
plt.savefig(f"{outdir}/Figure12_Taxonomic_Dominance_Check.pdf")
print("saved Figure 12")

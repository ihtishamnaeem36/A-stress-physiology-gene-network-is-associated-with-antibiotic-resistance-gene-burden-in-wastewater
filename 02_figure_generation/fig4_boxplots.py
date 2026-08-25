import sys; sys.path.insert(0, "/sessions/quirky-amazing-cori/mnt/outputs/figscript")
from style_setup import *
import numpy as np, pandas as pd, matplotlib.pyplot as plt

sumlog = pd.read_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/module_scores_sumlog_frozen.csv", index_col=0)
meta = pd.read_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/sample_meta.csv", index_col='sample').loc[sumlog.index]
kw = pd.read_csv("/sessions/quirky-amazing-cori/mnt/project 2.2/9. step Robustness and Sensitivity Analyses/tables/../../../outputs/../..".replace("../../../outputs/../..","")) if False else None
kw = pd.read_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/kw_environment_sumlog_frozen.csv").sort_values("p_raw")
modules_ordered = kw["module"].tolist()

fig, axes = plt.subplots(3, 5, figsize=(14, 8.4), sharey=False)
for ax, mod in zip(axes.flat, modules_ordered):
    row = kw[kw.module==mod].iloc[0]
    box_data = [sumlog.loc[meta.index[meta.environment==g], mod].values for g in ENV_ORDER]
    bp = ax.boxplot(box_data, patch_artist=True, widths=0.55, showfliers=False,
                     medianprops=dict(color="black", linewidth=1.3))
    for patch, g in zip(bp['boxes'], ENV_ORDER):
        patch.set_facecolor(ENV_COLORS[g]); patch.set_alpha(0.75); patch.set_edgecolor("#333333")
    rng = np.random.default_rng(0)
    for i, g in enumerate(ENV_ORDER):
        vals = sumlog.loc[meta.index[meta.environment==g], mod].values
        jitter = rng.uniform(-0.12, 0.12, size=len(vals))
        ax.scatter(np.full(len(vals), i+1)+jitter, vals, color="black", s=10, zorder=5, alpha=0.7)
    ax.set_xticks([1,2,3]); ax.set_xticklabels(["Hosp","Comm","Slau"], fontsize=8)
    ax.set_title(f"{mod}\nH={row.H:.2f}, p={row.p_raw:.3f}, ε²={row.eps2:.2f}", fontsize=8, fontweight="normal")
    ax.tick_params(axis='y', labelsize=7.5)
    ax.grid(axis="y", alpha=0.3)

for ax in axes.flat[len(modules_ordered):]:
    ax.axis("off")

handles = [plt.Rectangle((0,0),1,1, color=ENV_COLORS[g], alpha=0.75) for g in ENV_ORDER]
fig.legend(handles, ENV_ORDER, loc="upper center", bbox_to_anchor=(0.5, 1.02), ncol=3, frameon=False, fontsize=9.5)
plt.tight_layout()
outdir = "/sessions/quirky-amazing-cori/mnt/project 2.2/10. Final Manuscript (Network-Resistome Integration)/figures"
plt.savefig(f"{outdir}/Figure4_Module_Boxplots_By_Environment.png", dpi=600, bbox_inches="tight")
plt.savefig(f"{outdir}/Figure4_Module_Boxplots_By_Environment.pdf", bbox_inches="tight")
print("saved Figure 4")

import sys; sys.path.insert(0, "/sessions/quirky-amazing-cori/mnt/outputs/figscript")
from style_setup import *
from data_prep import load_all
from sarg_data_prep import load_all_sarg
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from scipy.stats import spearmanr

data, ko_ids, X, sample_cols, module_of, group_of, meta = load_all()
meta = meta.set_index('sample').loc[sample_cols]

modules = sorted(set(module_of.values()))
mod_scores = pd.DataFrame(index=sample_cols, columns=modules, dtype=float)
ko_to_row = {k: i for i, k in enumerate(ko_ids)}
for m in modules:
    ko_rows = [ko_to_row[k] for k in ko_ids if module_of[k] == m]
    mod_scores[m] = X[ko_rows, :].sum(axis=0)

sarg = load_all_sarg()
type_df, type_id, _ = sarg["type"]
type_df = type_df.set_index(type_id)
type_mat = type_df[sample_cols]
total_arg = type_mat.sum(axis=0).loc[sample_cols]
multidrug = type_mat.loc["multidrug", sample_cols]

fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.2))

panels = [
    (axes[0], total_arg, "Total ARG burden (sum of 21 SARG types)", "A"),
    (axes[1], multidrug, "Multidrug-resistance ARG burden", "B"),
]

for ax, yvar, ylabel, letter in panels:
    x = mod_scores["Stringent response (ppGpp)"].loc[sample_cols].values
    y = yvar.values.astype(float)
    rho, p = spearmanr(x, y)
    for env in ENV_ORDER:
        mask = (meta['environment'] == env).values
        ax.scatter(x[mask], y[mask], s=60, color=ENV_COLORS[env], edgecolor="white",
                   linewidths=0.6, label=env, zorder=3)
    # simple linear fit line (visual aid only, statistics are Spearman)
    coef = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, np.polyval(coef, xs), color="#555555", linestyle="--", linewidth=1.2, zorder=1)
    ax.set_xlabel("Stringent response (ppGpp) module score", fontsize=9.5)
    ax.set_ylabel(ylabel, fontsize=9.5)
    ax.set_title(f"{letter}", loc="left", fontsize=12, fontweight="bold")
    ax.text(0.03, 0.96, f"Spearman ρ = {rho:.2f}\np = {p:.4f}", transform=ax.transAxes,
            fontsize=9, va="top", ha="left",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#999999", lw=0.6, alpha=0.9))

axes[0].legend(loc="lower right", frameon=False, fontsize=8.5)

plt.tight_layout()
outdir = "/sessions/quirky-amazing-cori/mnt/project 2.2/10. Final Manuscript (Network-Resistome Integration)/figures"
plt.savefig(f"{outdir}/Figure11_Stringent_Response_vs_ARG.png", dpi=600, bbox_inches="tight")
plt.savefig(f"{outdir}/Figure11_Stringent_Response_vs_ARG.pdf", bbox_inches="tight")
print("saved Figure 11")

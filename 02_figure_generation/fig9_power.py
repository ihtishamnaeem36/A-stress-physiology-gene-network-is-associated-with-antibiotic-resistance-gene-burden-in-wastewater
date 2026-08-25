import sys; sys.path.insert(0, "/sessions/quirky-amazing-cori/mnt/outputs/figscript")
from style_setup import *
import pandas as pd, numpy as np, matplotlib.pyplot as plt

power_df = pd.read_csv("/sessions/quirky-amazing-cori/mnt/project 2.2/9. step Robustness and Sensitivity Analyses/tables/bootstrap_power_analysis.csv")
modules = [c for c in power_df.columns if c != "n_per_group"]
palette = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#999999"]

fig, ax = plt.subplots(figsize=(6.4, 4.6))
for m, c in zip(modules, palette):
    ax.plot(power_df["n_per_group"], power_df[m], marker="o", markersize=4.5, linewidth=1.6, color=c, label=m)
ax.axhline(0.8, color="#333333", linestyle="--", linewidth=1.1, label="80% power")
ax.axvline(6, color="#888888", linestyle=":", linewidth=1.1)
ax.text(6.2, 0.05, "current\nn=6/group", fontsize=8, color="#555555")
ax.set_xlabel("Samples per wastewater source type")
ax.set_ylabel("Empirical statistical power\n(bootstrap Kruskal-Wallis, 1,500 sims)")
ax.set_title("Bootstrap power analysis for the five strongest\n(non-significant) module-level trends", loc="left", fontsize=10)
ax.set_ylim(0, 1.05)
ax.legend(frameon=False, fontsize=7.8, loc="lower right")
ax.grid(alpha=0.3)
plt.tight_layout()
outdir = "/sessions/quirky-amazing-cori/mnt/project 2.2/10. Final Manuscript (Network-Resistome Integration)/figures"
plt.savefig(f"{outdir}/Figure9_Bootstrap_Power_Analysis.png", dpi=600, bbox_inches="tight")
plt.savefig(f"{outdir}/Figure9_Bootstrap_Power_Analysis.pdf", bbox_inches="tight")
print("saved Figure 9")

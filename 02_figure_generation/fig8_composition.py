import sys; sys.path.insert(0, "/sessions/quirky-amazing-cori/mnt/outputs/figscript")
from style_setup import *
import json, numpy as np, matplotlib.pyplot as plt

with open("/sessions/quirky-amazing-cori/mnt/project 2.2/9. step Robustness and Sensitivity Analyses/results/compositional_sensitivity_summary.json") as f:
    s = json.load(f)

fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.0))

ax = axes[0]
cats = ["log10(x+1)\nonly", "Shared\n(both)", "CLR\nonly"]
vals = [s["log_only_edges"], s["shared_edges"], s["clr_only_edges"]]
colors = ["#0072B2", "#009E73", "#D55E00"]
bars = ax.bar(cats, vals, color=colors, width=0.6, edgecolor="#333333", linewidth=0.6)
for b, v in zip(bars, vals):
    ax.text(b.get_x()+b.get_width()/2, v+800, f"{v:,}", ha="center", fontsize=9)
ax.set_ylabel("Number of network edges")
ax.set_title("A", loc="left", fontsize=12, fontweight="bold")
ax.text(0.02, 0.97, f"Edge-set overlap, Jaccard = {s['jaccard_overlap']:.2f}",
        transform=ax.transAxes, fontsize=8, va="top")
ax.set_ylim(0, max(vals)*1.18)
ax.grid(axis="y", alpha=0.3)

ax = axes[1]
cats2 = ["log10(x+1)\ntransform\n(primary)", "CLR transform\n(compositional\nsensitivity)"]
vals2 = [s["bridge_ec_rr_log10"], s["bridge_ec_rr_clr"]]
bars = ax.bar(cats2, vals2, color=["#0072B2", "#D55E00"], width=0.5, edgecolor="#333333", linewidth=0.6)
for b, v in zip(bars, vals2):
    ax.text(b.get_x()+b.get_width()/2, v+30, f"{v:,}", ha="center", fontsize=9)
ax.set_ylabel("Electron carrier balance × Recombination\nrepair edges (KO level)")
ax.set_title("B", loc="left", fontsize=12, fontweight="bold")
ax.text(0.02, 0.97, f"Redox-DNA bridge retained: {100*min(vals2)/max(vals2):.0f}% across transforms",
        transform=ax.transAxes, fontsize=8, va="top")
ax.set_ylim(0, max(vals2)*1.25)
ax.grid(axis="y", alpha=0.3)

fig.suptitle("Compositional sensitivity: log10(x+1) vs. CLR-transformed network (|\u03c1|>0.60, p<0.05)",
             fontsize=10.5, y=1.06)
plt.tight_layout()
outdir = "/sessions/quirky-amazing-cori/mnt/project 2.2/10. Final Manuscript (Network-Resistome Integration)/figures"
plt.savefig(f"{outdir}/Figure8_Compositional_Sensitivity.png", dpi=600, bbox_inches="tight")
plt.savefig(f"{outdir}/Figure8_Compositional_Sensitivity.pdf", bbox_inches="tight")
print("saved Figure 8")

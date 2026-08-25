import sys; sys.path.insert(0, "/sessions/quirky-amazing-cori/mnt/outputs/figscript")
from style_setup import *
import pandas as pd, numpy as np, matplotlib.pyplot as plt
import matplotlib.patches as mpatches

FINAL = "/sessions/quirky-amazing-cori/mnt/project 2.2/10. Final Manuscript (Network-Resistome Integration)"
res = pd.read_csv(f"{FINAL}/tables/ARG_type_x_module_correlation_matrix.csv")

modules_order = ["Electron carrier balance","Glutathione metabolism","Nitric oxide stress",
                  "Thioredoxin/Peroxidase","Catalase/Peroxidase",
                  "Recombination repair","OxyR oxidative DNA repair","Nucleotide excision repair (NER)",
                  "Replication fidelity","SOS response",
                  "Stringent response (ppGpp)","Two-component systems","Sigma factors (RpoS/RpoH)",
                  "LPS remodeling","Peptidoglycan remodeling"]
group_of_mod = {}
for m in modules_order[:5]: group_of_mod[m] = "A-Redox"
for m in modules_order[5:10]: group_of_mod[m] = "B-DNA"
for m in modules_order[10:]: group_of_mod[m] = "C-Stress"

types_order = sorted(res["ARG_Type"].unique())
rho_mat = pd.DataFrame(index=types_order, columns=modules_order, dtype=float)
q_mat = pd.DataFrame(index=types_order, columns=modules_order, dtype=float)
for _, row in res.iterrows():
    rho_mat.loc[row["ARG_Type"], row["Module"]] = row["rho"]
    q_mat.loc[row["ARG_Type"], row["Module"]] = row["q_BH"]

# order ARG types by their strongest |rho| against Stringent response, for visual grouping
types_sorted = rho_mat["Stringent response (ppGpp)"].abs().sort_values(ascending=False).index.tolist()
rho_mat = rho_mat.loc[types_sorted]
q_mat = q_mat.loc[types_sorted]

fig, ax = plt.subplots(figsize=(9.5, 8.5))
im = ax.imshow(rho_mat.values.astype(float), cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")

for i in range(rho_mat.shape[0]):
    for j in range(rho_mat.shape[1]):
        q = q_mat.values[i, j]
        if q < 0.001: mark = "***"
        elif q < 0.01: mark = "**"
        elif q < 0.05: mark = "*"
        else: mark = ""
        if mark:
            ax.text(j, i, mark, ha="center", va="center", fontsize=7.5, color="black", fontweight="bold")

ax.set_xticks(range(len(modules_order)))
ax.set_xticklabels(modules_order, rotation=60, ha="right", fontsize=7.8)
ax.set_yticks(range(len(types_sorted)))
ax.set_yticklabels(types_sorted, fontsize=7.8)

# colour x tick labels by functional group
for tick, m in zip(ax.get_xticklabels(), modules_order):
    tick.set_color(GROUP_COLORS[group_of_mod[m]])

cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
cbar.set_label("Spearman ρ", fontsize=9)

plt.tight_layout()
outdir = "/sessions/quirky-amazing-cori/mnt/project 2.2/10. Final Manuscript (Network-Resistome Integration)/figures"
plt.savefig(f"{outdir}/Figure10_ARG_Type_Module_Heatmap.png", dpi=600, bbox_inches="tight")
plt.savefig(f"{outdir}/Figure10_ARG_Type_Module_Heatmap.pdf", bbox_inches="tight")
print("saved Figure 10")

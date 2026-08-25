import sys; sys.path.insert(0, "/sessions/quirky-amazing-cori/mnt/outputs/figscript")
from style_setup import *
from data_prep import load_all, ko_network
import numpy as np, pandas as pd, networkx as nx, matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

data, ko_ids, X, sample_cols, module_of, group_of, meta = load_all()
corr, pmat, iu, r_vals, p_vals, edge_mask, valid = ko_network(X, 0.60, 0.05)
rows, cols = iu
n_ko = len(ko_ids)

modules = sorted(set(module_of.values()))
mod_group = {}
for k in ko_ids:
    mod_group[module_of[k]] = group_of[k]
mod_size = pd.Series([module_of[k] for k in ko_ids]).value_counts().to_dict()

mod_of_arr = np.array([module_of[k] for k in ko_ids])
n_mod = len(modules)
mod_idx = {m: i for i, m in enumerate(modules)}
sig_count = np.zeros((n_mod, n_mod))
poss_count = np.zeros((n_mod, n_mod))
rho_sum = np.zeros((n_mod, n_mod))

sig_edges = np.where(edge_mask)[0]
for e in sig_edges:
    i, j = rows[e], cols[e]
    mi, mj = mod_idx[mod_of_arr[i]], mod_idx[mod_of_arr[j]]
    a, b = (mi, mj) if mi <= mj else (mj, mi)
    sig_count[a, b] += 1
    rho_sum[a, b] += r_vals[e]

valid_pairs = np.where(valid)[0]
for e in valid_pairs:
    i, j = rows[e], cols[e]
    mi, mj = mod_idx[mod_of_arr[i]], mod_idx[mod_of_arr[j]]
    a, b = (mi, mj) if mi <= mj else (mj, mi)
    poss_count[a, b] += 1

density = np.divide(sig_count, poss_count, out=np.zeros_like(sig_count), where=poss_count > 0)
mean_rho = np.divide(rho_sum, sig_count, out=np.zeros_like(rho_sum), where=sig_count > 0)

Gm = nx.Graph()
for m in modules:
    Gm.add_node(m, size=mod_size[m], group=mod_group[m])
pair_list = []
for a in range(n_mod):
    for b in range(a + 1, n_mod):
        if density[a, b] > 0:
            pair_list.append((a, b, density[a, b]))
pair_list.sort(key=lambda x: -x[2])
n_keep = max(38, int(round(len(pair_list) * 0.42)))
kept = pair_list[:n_keep]

for a, b, w in kept:
    Gm.add_edge(modules[a], modules[b], weight=w, rho=mean_rho[a, b])

fig, ax = plt.subplots(figsize=(9.0, 8.6))

# ---- circular layout, grouped into three arcs with a gap between mechanistic groups ----
order = sorted(modules, key=lambda m: (GROUP_ORDER.index(mod_group[m]), -mod_size[m]))
group_gap_deg = 18
counts = {g: sum(1 for m in order if mod_group[m] == g) for g in GROUP_ORDER}
total_gap = group_gap_deg * len(GROUP_ORDER)
usable_deg = 360 - total_gap
R = 1.0
pos = {}
angle = 90.0
for g in GROUP_ORDER:
    members = [m for m in order if mod_group[m] == g]
    span = usable_deg * (counts[g] / n_mod)
    step = span / max(len(members) - 1, 1) if len(members) > 1 else 0
    a0 = angle
    for i, m in enumerate(members):
        a = a0 - (i * step if len(members) > 1 else 0)
        rad = np.radians(a)
        pos[m] = (R * np.cos(rad), R * np.sin(rad))
    angle = a0 - span - group_gap_deg

# faint outer spine so node order/grouping is legible even where few edges reach a node
theta = np.linspace(0, 2 * np.pi, 400)
ax.plot(R * np.cos(theta), R * np.sin(theta), color="#E8E8E8", linewidth=1.0, zorder=0)

edge_w = [Gm[u][v]['weight'] for u, v in Gm.edges()]
edge_rho = [Gm[u][v]['rho'] for u, v in Gm.edges()]
max_w, min_w = max(edge_w), min(edge_w)
rng = max(max_w - min_w, 1e-9)

# All edges, including the module pair discussed in the text (Electron carrier balance x
# Recombination repair), are drawn with the same rule: colour by sign of mean rho, width and
# opacity by edge density. No edge is styled differently from the others; the figure legend
# and caption, not the rendering, are what the reader uses to find that specific pair.
for (u, v), w, rho in zip(Gm.edges(), edge_w, edge_rho):
    t = (w - min_w) / rng
    lw = 0.5 + 3.3 * t
    alpha = 0.16 + 0.55 * t
    col = "#B2182B" if rho >= 0 else "#2166AC"
    patch = mpatches.FancyArrowPatch(pos[u], pos[v], connectionstyle="arc3,rad=0.15",
                                      arrowstyle="-", color=col, linewidth=lw, alpha=alpha,
                                      capstyle="round", zorder=1)
    ax.add_patch(patch)

node_sizes = [230 + 6.2 * mod_size[m] for m in Gm.nodes()]
node_colors = [GROUP_COLORS[mod_group[m]] for m in Gm.nodes()]
xs = [pos[m][0] for m in Gm.nodes()]; ys = [pos[m][1] for m in Gm.nodes()]
ax.scatter(xs, ys, s=node_sizes, c=node_colors, edgecolors="white", linewidths=1.3, zorder=3)

label_map = {
    "Two-component systems": "Two-component\nsystems",
    "Electron carrier balance": "Electron carrier\nbalance",
    "Recombination repair": "Recombination\nrepair",
    "Stringent response (ppGpp)": "Stringent\nresponse",
    "Peptidoglycan remodeling": "Peptidoglycan\nremodeling",
    "OxyR oxidative DNA repair": "OxyR oxidative\nDNA repair",
    "Glutathione metabolism": "Glutathione\nmetabolism",
    "Nucleotide excision repair (NER)": "NER",
    "Nitric oxide stress": "Nitric oxide\nstress",
    "LPS remodeling": "LPS\nremodeling",
    "Thioredoxin/Peroxidase": "Thioredoxin/\nPeroxidase",
    "Replication fidelity": "Replication\nfidelity",
    "Sigma factors (RpoS/RpoH)": "Sigma factors",
    "SOS response": "SOS\nresponse",
    "Catalase/Peroxidase": "Catalase/\nPeroxidase",
}
for m in Gm.nodes():
    x, y = pos[m]
    ha = "left" if x >= -0.02 else "right"
    dx = 0.13 if x >= -0.02 else -0.13
    dy = 0.13 if y >= 0 else -0.13
    ax.annotate(label_map.get(m, m), (x, y), xytext=(x * 1.34 + dx, y * 1.34 + dy), fontsize=8.4,
                ha=ha, va="center")

ax.set_xlim(-2.05, 2.05); ax.set_ylim(-1.95, 1.85)
ax.axis("off")
ax.set_aspect("equal")

legend_elems = [mpatches.Patch(color=GROUP_COLORS[g], label=GROUP_LABELS[g]) for g in GROUP_ORDER]
legend_elems.append(Line2D([0], [0], color="#B2182B", lw=3, label="Positive mean ρ"))
legend_elems.append(Line2D([0], [0], color="#2166AC", lw=3, label="Negative mean ρ"))
legend_elems.append(Line2D([0], [0], marker='o', color='w', markerfacecolor='#999999', markersize=8, label='Node size ∝ module size (KOs)'))
legend_elems.append(Line2D([0], [0], color='#999999', lw=3, label='Edge width ∝ within/between-module edge density'))
ax.legend(handles=legend_elems, loc="lower center", frameon=False, fontsize=8.4,
          bbox_to_anchor=(0.5, -0.05), ncol=2)

fig.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.06)
outdir = "/sessions/quirky-amazing-cori/mnt/project 2.2/10. Final Manuscript (Network-Resistome Integration)/figures"
plt.savefig(f"{outdir}/Figure1_Network_Backbone.png", dpi=600, bbox_inches="tight")
plt.savefig(f"{outdir}/Figure1_Network_Backbone.pdf", bbox_inches="tight")
print(f"saved Figure 1 (module network, top {len(kept)} of {len(pair_list)} pairs shown, no manual highlighting)")

import pandas as pd, numpy as np
from scipy.stats import rankdata, t as tdist
import networkx as nx
import itertools, json

BASE = "/sessions/quirky-amazing-cori/mnt/project 2.2"
abund = pd.read_excel(f"{BASE}/1.step  Target module selection and k number recovery/step1 figures table/Step1_Abundance_Matrix.xlsx",
                       sheet_name="Full_Abundance_Matrix")
abund = abund.rename(columns={'# Gene Family':'KO_ID'})
sample_cols = [c for c in abund.columns if c not in ('KO_ID','Module')]
ko_ids = abund['KO_ID'].tolist()
X = np.log10(abund[sample_cols].astype(float).values + 1)  # 903 x 18

n_ko, n = X.shape
print("KOs:", n_ko, "samples:", n)

# rank each row (KO) across samples
R = np.apply_along_axis(rankdata, 1, X)  # 903 x 18 ranks

# Pearson correlation on ranks = Spearman rho, computed via corrcoef
corr = np.corrcoef(R)  # 903x903

# p-values via t approx
with np.errstate(divide='ignore', invalid='ignore'):
    tstat = corr * np.sqrt((n-2) / (1 - corr**2))
pmat = 2 * tdist.sf(np.abs(tstat), df=n-2)

iu = np.triu_indices(n_ko, k=1)
r_vals = corr[iu]
p_vals = pmat[iu]
total_pairs = len(r_vals)
print("Total unique pairs:", total_pairs, " expected C(903,2)=", n_ko*(n_ko-1)//2)

edge_mask = (np.abs(r_vals) > 0.60) & (p_vals < 0.05)
n_edges = edge_mask.sum()
density = n_edges / total_pairs
mean_abs_r_edges = np.abs(r_vals[edge_mask]).mean()
pos_frac = (r_vals[edge_mask] > 0).mean()

print(f"Edges (|r|>0.60 & p<0.05): {n_edges}")
print(f"Density: {density:.4f}")
print(f"Mean |r| among edges: {mean_abs_r_edges:.3f}")
print(f"Positive-edge fraction: {pos_frac:.3f}")

# Build graph
G = nx.Graph()
G.add_nodes_from(ko_ids)
rows, cols = iu
edge_rows = rows[edge_mask]; edge_cols = cols[edge_mask]; edge_r = r_vals[edge_mask]
for i,j,rr in zip(edge_rows, edge_cols, edge_r):
    G.add_edge(ko_ids[i], ko_ids[j], weight=rr)

deg = dict(G.degree())
deg_series = pd.Series(deg).sort_values(ascending=False)
print("\nTop 10 hub KOs by degree:")
print(deg_series.head(10))
print("\nMean node degree:", np.mean(list(deg.values())))

comps = sorted(nx.connected_components(G), key=len, reverse=True)
print(f"\nNumber of connected components: {len(comps)}")
print(f"Giant component size: {len(comps[0])} / {n_ko} ({100*len(comps[0])/n_ko:.1f}%)")

# clustering
avg_clust = nx.average_clustering(G)
transitivity = nx.transitivity(G)
print(f"\nMean local clustering coefficient: {avg_clust:.4f}")
print(f"Global transitivity: {transitivity:.4f}")

# ER null model: same n nodes, same n edges, average over a few realizations
np.random.seed(42)
ER_clust = []
ER_trans = []
for rep in range(5):
    GER = nx.gnm_random_graph(n_ko, n_edges, seed=rep)
    ER_clust.append(nx.average_clustering(GER))
    ER_trans.append(nx.transitivity(GER))
print(f"\nER null mean local clustering (5 reps): {np.mean(ER_clust):.4f} -> enrichment {avg_clust/np.mean(ER_clust):.2f}x")
print(f"ER null transitivity (5 reps): {np.mean(ER_trans):.4f} -> enrichment {transitivity/np.mean(ER_trans):.2f}x")

# save summary
summary = {
    "total_pairs": int(total_pairs),
    "n_edges": int(n_edges),
    "density": float(density),
    "mean_abs_r_edges": float(mean_abs_r_edges),
    "positive_fraction": float(pos_frac),
    "mean_degree": float(np.mean(list(deg.values()))),
    "max_degree_KO": deg_series.index[0],
    "max_degree": int(deg_series.iloc[0]),
    "giant_component_size": len(comps[0]),
    "giant_component_pct": 100*len(comps[0])/n_ko,
    "avg_local_clustering": float(avg_clust),
    "transitivity": float(transitivity),
    "ER_avg_local_clustering": float(np.mean(ER_clust)),
    "ER_transitivity": float(np.mean(ER_trans)),
    "clustering_enrichment_local": float(avg_clust/np.mean(ER_clust)),
    "clustering_enrichment_transitivity": float(transitivity/np.mean(ER_trans)),
}
with open("/sessions/quirky-amazing-cori/mnt/outputs/validation/network_summary.json","w") as f:
    json.dump(summary, f, indent=2)

# save edge list and degree table for later use
nx.to_pandas_edgelist(G).to_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/network_edges.csv", index=False)
deg_series.to_csv("/sessions/quirky-amazing-cori/mnt/outputs/validation/network_degree.csv")

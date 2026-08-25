# Project 2.2 — Independently Re-Validated Numbers
(All recomputed directly from BG/Project22_903KO_Module_Map.csv [frozen KO->module map]
merged with the 903x18 KO abundance matrix in Step1_Abundance_Matrix.xlsx.
Module score = sum of log10(x+1) per module per sample, per Methods 2.7.)

## Study design
- 18 metagenomes = 3 cities (Mardan, Peshawar, Swat) x 3 environments (Hospital, Community, Slaughterhouse) x 2 replicates
- n=6 per environment, n=6 per city (confirmed balanced)
- 903 target KOs across 15 modules (confirmed against frozen map, matches Methods doc counts exactly)
- 12 of 903 KOs have zero abundance in all 18 samples (excluded from pairwise correlation tests; minor)

## KO-level co-occurrence network (Spearman, |r|>0.60 & p<0.05, df=16) — VALIDATED, matches original + audit almost exactly
- Total pairs tested: 407,253
- Edges: 53,775
- Density: 0.132
- Mean |r| among edges: 0.722
- Positive-edge fraction: 64.3%
- Giant component: 886/903 KOs (98.1%), 17 components total
- Mean node degree: 119.1
- Top hub KO: K00406, degree 328
- Mean local clustering coefficient: 0.558 (ER null ~0.132, ~4.2x enrichment)
- Transitivity: 0.633 (ER null ~0.132, ~4.8x enrichment)
- BH-FDR (q<0.05, denominator = all 407,253 tests): 47,821 edges retained (88.9%) — matches Step 6's reported 47,695/88.9%

## Module-level correlation matrix (Spearman on sum-of-logs module scores, frozen map) — CORRECTED
- Glutathione metabolism x Nitric oxide stress: rho = 0.932 (p<0.0001) — robust across every score definition tested
- Electron carrier balance x Recombination repair: rho = 0.633 (p=0.0048)
  - ORIGINAL CLAIM: r=0.866 — NOT reproducible under any tested definition, confirmed wrong
  - Prior audit's partial estimate: ~0.75 (used non-frozen/original KO map)
  - TRUE fully-corrected value (frozen map + sum-of-logs): r=0.633 — still significant, still a genuine cross-group correlation, but well below both prior numbers

## Module differential analysis (Kruskal-Wallis, environment, n=6/group, frozen map, sum-of-logs) — WEAKER than reported
- NO module reaches raw p<0.05
- Closest: Stringent response (ppGpp): H=4.11, p=0.128, eps2=0.140
  (originally reported p=0.082, eps2=0.200 using the non-frozen/drifted module map — correcting KO membership weakens this further)
- LPS remodeling: raw p=0.587 (confirms the "p=0.041" claim only held under depth-normalization, not raw abundance — must be exploratory-only language)
- No module survives Bonferroni or BH-FDR across the 15 tests
- City (geography) KW: nothing meaningful (strongest: Replication fidelity p=0.038, uncorrected, 1 of 15 non-hypothesis-driven tests — treat as noise, do not report as a finding)

## Ordination (Step 8) — trend weaker than reported after KO-map correction
- PCA: PC1=46.2%, PC1+PC2=67.8%, PC1-PC3=82.9% (close to originally reported 45.8%/66.5%/82.5%)
- PERMANOVA environment: F=1.77, p=0.14 (Bray-Curtis) / F=1.18, p=0.30 (z-scored Euclidean)
  (original claim was F=2.19, p=0.069 — used non-frozen map; does not reach even "trend" territory once corrected)
- PERMANOVA city: F=0.72, p=0.62 — clearly non-significant
- PERMDISP (formal betadisper, 9999 perm): p=0.69-0.91 — not significant; Slaughterhouse's higher numeric dispersion is not statistically distinguishable
- Removing the Slaughterhouse multivariate outlier (SSLW2) does NOT rescue significance -- signal recedes further, ruling out "confounded by outlier" framing

## Resistome Risk Index (Step 7) — UNSUPPORTED
- No ARG abundance data anywhere in the project folder; no Step 7 folder exists
- Cannot be presented as validated or predictive under any framing; future work / hypothesis only

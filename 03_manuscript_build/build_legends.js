const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType } = require("docx");

function P(text, opts={}) {
  const { bold=false, italic=false, size=22, spacingAfter=240 } = opts;
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: spacingAfter, line: 276 },
    children: [ new TextRun({ text, bold, italics: italic, size }) ]
  });
}
function Title(text) {
  return new Paragraph({ spacing: { before: 200, after: 80 },
    children: [ new TextRun({ text, bold: true, size: 22 }) ] });
}

const legends = [
["Figure 1. Module-level KO co-occurrence network.",
 "Each node is one of the 15 curated modules, sized by its number of target KOs; an edge is drawn between two modules when more than 3% of the KO-KO pairs spanning them are significant network edges (|ρ|>0.60, Benjamini-Hochberg q<0.05). Edge width is proportional to this within/between-module edge density and edge colour indicates the sign of the mean Spearman ρ among the significant pairs (red = positive, blue = negative). Nodes are coloured by functional group (Group A – Redox stress, orange; Group B – DNA damage/fidelity, blue; Group C – Stress physiology, green). A gene-level node-link diagram of the full network (903 nodes, 53,775 edges) was not legible at any print resolution because of edge overplotting, and is not shown; the underlying gene-level edge counts by module pair are given in Figure 7 and Table 5/6, and full network summary statistics are in Table 2."],

["Figure 2. Network degree distribution and threshold sensitivity.",
 "(A) Distribution of node degree across the 903 KOs in the primary network (|ρ|>0.60, p<0.05; mean degree = 119.1, dashed line). (B) Number of significant network edges as a function of the Spearman |ρ| threshold used to define an edge (thresholds tested: 0.50–0.75; p<0.05 throughout). The 0.60 threshold used in the main analysis (dashed line) is conservative relative to the n=18 critical value of ρ≈0.468 for p=0.05."],

["Figure 3. Module-score correlation matrix.",
 "Spearman correlation (ρ) between the 15 module scores (sum of log10(x+1)-transformed KO abundances) across 18 metagenomes. Cell values are Spearman ρ; asterisks denote Benjamini-Hochberg FDR-corrected significance across the 105 unique module pairs (* q<0.05, ** q<0.01, *** q<0.001). Modules are ordered and colour-coded by functional group (orange = Group A Redox stress, blue = Group B DNA damage/fidelity, green = Group C Stress physiology), with black lines demarcating group boundaries. This is the single, corrected module correlation matrix used throughout the manuscript (Section 2.4, Table 4)."],

["Figure 4. Module scores by wastewater source type.",
 "Sum-of-log10(x+1) module scores for all 15 modules, grouped by wastewater source type (Hospital, Community, Slaughterhouse; n=6 each) and ranked by Kruskal-Wallis raw p-value (lowest/strongest first). Boxes show median and interquartile range; whiskers extend to the most extreme non-outlier value; individual sample values are overlaid as black points. Kruskal-Wallis H, raw p-value and epsilon-squared effect size are given above each panel. No module differs significantly by source type after Benjamini-Hochberg correction across the 15 tests (Table 3)."],

["Figure 5. Multivariate ordination of the module-score profile.",
 "(A) Principal component analysis (PCA) of the 18×15 z-scored module-score matrix. (B) Principal coordinates analysis (PCoA) of the same matrix using Bray-Curtis dissimilarity on raw module scores. Points are coloured by wastewater source type; dashed ellipses show a 1.5-standard-deviation data ellipse per group (descriptive only, not a formal confidence region). PERMANOVA (9,999 permutations) and ANOSIM statistics for source type are annotated on each panel; neither ordination shows a statistically significant grouping at n=6 per group."],

["Figure 6. Multivariate dispersion by wastewater source type.",
 "Distance of each sample to its group centroid in principal-coordinates space (z-scored Euclidean distance), grouped by wastewater source type. Horizontal bars show group means. A formal permutation-based PERMDISP test (Anderson's betadisper equivalent; 9,999 permutations) found no significant heterogeneity of dispersion among the three source types (F=0.49, p=0.69), despite Slaughterhouse showing the numerically highest mean dispersion."],

["Figure 7. KO-level edge counts between module pairs.",
 "Number of significant KO-KO co-occurrence edges (|ρ|>0.60, p<0.05) between every pair of the 15 modules, including within-module (diagonal) edges, on a log color scale. Recomputed for this manuscript on the corrected 903-KO module map (Section 2.3); this replaces an earlier version of this figure that used a pre-correction KO-to-module mapping and reported a different edge count (2,147, vs. 2,104 shown here) for the Electron carrier balance × Recombination repair bridge. Two-component systems (406 of 903 target KOs) shows the highest edge counts throughout, consistent with its size (Section 4.3 discusses this as a caveat on interpreting bridge strength)."],

["Figure 8. Compositional sensitivity of the network.",
 "(A) Overlap between the primary log10(x+1) network and a centred-log-ratio (CLR)-transformed sensitivity network, both built at |ρ|>0.60, p<0.05 (Section 9, Step 9 robustness analyses). Jaccard overlap = 0.34; the two networks share 27,630 edges out of 81,428 in their union. (B) The specific redox-DNA bridge motivating this study (Electron carrier balance × Recombination repair, KO level) is stable across the two transforms (2,104 vs. 2,160 edges, 97% retained), even though the broader network topology (hub identity) is more sensitive to the compositional transform (top-15 hub overlap: 4/15)."],

["Figure 9. Bootstrap power analysis.",
 "Empirical statistical power to detect the five modules with the strongest (but non-significant) observed Kruskal-Wallis signal (Table 3), estimated by parametric bootstrap resampling from each source type's six observed module scores (1,500 simulations per module per sample size; Section 9 methods). The dashed horizontal line marks 80% power; the dotted vertical line marks the current study's sample size (n=6 per group). Approximately 15 samples per source type would be needed to resolve the three strongest trends (Stringent response, Two-component systems, Peptidoglycan remodeling) at 80% power; Glutathione metabolism and Catalase/Peroxidase would need approximately 20 and 25 respectively."],
];

const children = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
    children: [ new TextRun({ text: "Figure Legends — Project 2.2", bold: true, size: 28 }) ] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
    children: [ new TextRun({ text: "All figures regenerated directly from the corrected 903-KO abundance matrix and frozen module map for the first-draft manuscript. Source code: 9. step Robustness and Sensitivity Analyses/code/ and the figure-generation scripts referenced there.", italics: true, size: 19, color: "666666" }) ] }),
];
for (const [title, body] of legends) {
  children.push(Title(title));
  children.push(P(body));
}

const doc = new Document({
  styles: { default: { document: { run: { font: "Calibri", size: 22 } } } },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    children,
  }],
});

Packer.toBuffer(doc).then(buffer => {
  const out = "/sessions/quirky-amazing-cori/mnt/project 2.2/figures/Figure_Legends.docx";
  fs.writeFileSync(out, buffer);
  console.log("wrote", out, buffer.length);
});

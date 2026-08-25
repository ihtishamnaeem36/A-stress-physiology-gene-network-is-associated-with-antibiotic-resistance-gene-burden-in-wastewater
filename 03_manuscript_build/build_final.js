const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  ImageRun, PageBreak, Header, Footer, PageNumber, LevelFormat,
  convertInchesToTwip, VerticalAlign, TabStopType, TabStopPosition
} = require("docx");

const BASE = "/sessions/quirky-amazing-cori/mnt/project 2.2/10. Final Manuscript (Network-Resistome Integration)";
const FIG = `${BASE}/figures`;

function P(text, opts={}) {
  const { bold=false, italic=false, size=24, spacingAfter=200, alignment=AlignmentType.JUSTIFIED, indentFirst=false } = opts;
  return new Paragraph({
    alignment,
    spacing: { after: spacingAfter, line: 288 },
    indent: indentFirst ? { firstLine: 360 } : undefined,
    children: [ new TextRun({ text, bold, italics: italic, size }) ]
  });
}
// helper for an italic run inside Mixed(), e.g. for genus/species names
function iRun(text, extra={}) { return { text, italic: true, ...extra }; }
function Mixed(runs, opts={}) {
  const { spacingAfter=200, alignment=AlignmentType.JUSTIFIED } = opts;
  return new Paragraph({
    alignment, spacing: { after: spacingAfter, line: 288 },
    children: runs.map(r => new TextRun({ text: r.text, bold: !!r.bold, italics: !!r.italic, size: r.size || 24, superScript: !!r.sup }))
  });
}
function H1(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 160 }, children: [ new TextRun({ text }) ] });
}
function H2(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 280, after: 140 }, children: [ new TextRun({ text }) ] });
}
function Caption(text) {
  return new Paragraph({
    spacing: { before: 100, after: 300 },
    children: [ new TextRun({ text, italics: true, size: 21 }) ]
  });
}
function cell(text, opts={}) {
  const { bold=false, width=1000, shade=null, align=AlignmentType.LEFT, size=20, italic=false, borders=undefined } = opts;
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: shade ? { fill: shade, type: ShadingType.CLEAR } : undefined,
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    borders,
    children: [ new Paragraph({ alignment: align, children: [ new TextRun({ text: String(text), bold, italics: italic, size }) ] }) ]
  });
}
// Classic three-line (booktabs / Elsevier) table style: a rule above the header,
// a rule below the header, and a rule at the bottom of the table. No vertical
// rules and no rules between body rows.
const NO_BORDER = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const RULE = { style: BorderStyle.SINGLE, size: 8, color: "000000" };
const THIN_RULE = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
function dataTable(headers, rows, widths) {
  const total = widths.reduce((a,b)=>a+b,0);
  const headerCellBorders = { top: RULE, bottom: THIN_RULE, left: NO_BORDER, right: NO_BORDER };
  const bodyCellBorders = { top: NO_BORDER, bottom: NO_BORDER, left: NO_BORDER, right: NO_BORDER };
  const lastBodyCellBorders = { top: NO_BORDER, bottom: RULE, left: NO_BORDER, right: NO_BORDER };
  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map((h,i)=>cell(h, {bold:true, width: widths[i], align: AlignmentType.CENTER, borders: headerCellBorders}))
  });
  const bodyRows = rows.map((r,ri) => new TableRow({
    children: r.map((v,i)=>cell(v, {width: widths[i], align: i===0? AlignmentType.LEFT: AlignmentType.CENTER,
      borders: ri === rows.length-1 ? lastBodyCellBorders : bodyCellBorders}))
  }));
  return new Table({
    width: { size: total, type: WidthType.DXA },
    columnWidths: widths,
    borders: { top: NO_BORDER, bottom: NO_BORDER, left: NO_BORDER, right: NO_BORDER, insideHorizontal: NO_BORDER, insideVertical: NO_BORDER },
    rows: [headerRow, ...bodyRows]
  });
}
const ITALIC_TAXA = new Set(["Pseudomonas","Vibrio","Bacteroides","Flavobacterium","Desulfomicrobium","Escherichia coli"]);
function taxonCell(text, opts={}) {
  return cell(text, { ...opts, italic: ITALIC_TAXA.has(String(text)) });
}
// Same three-line style as dataTable(), but italicises genus/species names in one column
// (columnIndex) using the ITALIC_TAXA whitelist; family/order/class-level "unresolved (...)"
// values are correctly left upright.
function dataTableItalicCol(headers, rows, widths, italicColIndex) {
  const total = widths.reduce((a,b)=>a+b,0);
  const headerCellBorders = { top: RULE, bottom: THIN_RULE, left: NO_BORDER, right: NO_BORDER };
  const bodyCellBorders = { top: NO_BORDER, bottom: NO_BORDER, left: NO_BORDER, right: NO_BORDER };
  const lastBodyCellBorders = { top: NO_BORDER, bottom: RULE, left: NO_BORDER, right: NO_BORDER };
  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map((h,i)=>cell(h, {bold:true, width: widths[i], align: AlignmentType.CENTER, borders: headerCellBorders}))
  });
  const bodyRows = rows.map((r,ri) => new TableRow({
    children: r.map((v,i)=>cell(v, {width: widths[i], align: i===0? AlignmentType.LEFT: AlignmentType.CENTER,
      italic: i===italicColIndex && ITALIC_TAXA.has(String(v)),
      borders: ri === rows.length-1 ? lastBodyCellBorders : bodyCellBorders}))
  }));
  return new Table({
    width: { size: total, type: WidthType.DXA },
    columnWidths: widths,
    borders: { top: NO_BORDER, bottom: NO_BORDER, left: NO_BORDER, right: NO_BORDER, insideHorizontal: NO_BORDER, insideVertical: NO_BORDER },
    rows: [headerRow, ...bodyRows]
  });
}
function img(path, w, h) {
  const data = fs.readFileSync(path);
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 200, after: 80 },
    children: [ new ImageRun({ data, type: "png", transformation: { width: w, height: h } }) ]
  });
}
console.log("helpers ready");

// ============================================================
// TITLE / ABSTRACT
// ============================================================
const titleBlock = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
    children: [ new TextRun({ text: "A stress-physiology gene co-occurrence network is associated with antibiotic-resistance-gene burden in urban wastewater metagenomes", bold: true, size: 30 }) ] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 300 },
    children: [ new TextRun({ text: "Running title: A stress-gene network linked to resistance-gene burden in wastewater", italics: true, size: 20 }) ] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 },
    children: [ new TextRun({ text: "[Author names to be added]", size: 20, color: "808080" }) ] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
    children: [ new TextRun({ text: "[Affiliations to be added]", size: 20, color: "808080" }) ] }),
];

const abstractHeading = H1("Abstract");
const abstractBody = [
  Mixed([{text:"Background. ", bold:true},{text:"Wastewater surveillance for antimicrobial resistance (AMR) typically profiles resistance genes directly, but says less about the physiological background, oxidative stress, DNA damage and repair, and general stress physiology, against which resistance is acquired and retained. We treat these processes as a set of resistance-adjacent functional gene modules, test whether they form a coordinated co-occurrence network, and, critically, test whether that network is actually associated with measured resistance-gene burden in the same samples."}]),
  Mixed([{text:"Methods. ", bold:true},{text:"We profiled 18 wastewater metagenomes spanning three source types (hospital, community, slaughterhouse; n=6 each) and three cities in Khyber Pakhtunkhwa, Pakistan, balanced in a 3×3×2 design. From a 10,333-KO functional abundance table we curated 903 target KOs across 15 modules in three functional groups (redox stress, DNA damage/fidelity, stress physiology). A KO-level Spearman co-occurrence network (|ρ|>0.60, p<0.05, Benjamini-Hochberg FDR correction over 407,253 pairs) and module-level differential, correlation and ordination analyses were run and stress-tested with five robustness analyses (compositional sensitivity, threshold sensitivity, hub/group-pair summary, PCoA/ANOSIM, bootstrap power). Antibiotic resistance gene (ARG) abundance for the same 18 samples was obtained from a SARG (Structured Antibiotic Resistance Genes database) annotation at Type (21 categories), Subtype, Mechanism-group and pathogen-host resolution, and correlated against the module scores."}]),
  Mixed([{text:"Results. ", bold:true},{text:"The 903 KOs formed one predominantly connected, non-random network (53,775 significant edges, 98.1% of KOs in one component, 4-5× the clustering of a random-graph null; 88.9% of edges surviving FDR correction). No individual module differed significantly by wastewater source type after correction (n=6/group), but total ARG burden did (Kruskal-Wallis p=0.0033, hospital effluent roughly 2.3-fold higher than community or slaughterhouse). Of the 15 modules, Stringent response (ppGpp) was significantly correlated with total ARG burden (Spearman ρ=0.73, BH-FDR q=0.0098) and, at finer resolution, with seven of the 21 individual SARG resistance types spanning multiple mechanistically unrelated drug classes (multidrug, aminoglycoside, beta-lactam, sulfonamide, trimethoprim, bacitracin, chloramphenicol; all q<0.05), a pattern independently reproduced at the resistance-mechanism level (efflux pump mechanism x Stringent response, ρ=0.86, q=0.0005). Leave-one-out resampling confirmed these associations were not driven by any single sample, and a source-type/city confound check and a taxonomic dominance check using taxon-stratified functional data (418 distinct contributing taxa, no single taxon exceeding 44% of classified abundance) both left the association materially unchanged."}]),
  Mixed([{text:"Conclusions. ", bold:true},{text:"Redox, DNA-repair and stress-response genes form one integrated, non-random co-occurrence network in these wastewater communities, and this network is not merely a structural curiosity: the stringent response module, part of that network, tracks resistance-gene burden across multiple antibiotic classes in the same samples. This is consistent with the stringent response's established role in antibiotic tolerance and persister-cell formation, and supports treating stress-physiology gene networks as a resistome-relevant surveillance signal rather than only an indirect, resistance-adjacent proxy. The association is correlational, cross-sectional and drawn from n=18 samples, and does not establish causation; a direct taxonomic dominance check found no evidence that a single dominant organism explains it, so independent, out-of-sample replication is identified as the priority follow-up."}]),
  Mixed([{text:"Keywords: ", bold:true},{text:"wastewater metagenomics; functional gene co-occurrence network; antibiotic resistance genes; SARG; stringent response; KEGG Orthology; oxidative stress; DNA repair; antimicrobial resistance surveillance"}], {spacingAfter:400}),
];

console.log("title/abstract ready");

// ============================================================
// 1. INTRODUCTION
// ============================================================
const introHeading = H1("1. Introduction");
const introBody = [
  P("Antimicrobial resistance (AMR) is tracked increasingly through environmental surveillance rather than clinical isolates alone, and wastewater is a useful matrix for this purpose because it pools genetic material from community, clinical and agricultural sources upstream of treatment [CITATION]. Most wastewater AMR studies quantify antibiotic resistance genes (ARGs) directly, reporting their abundance, diversity or co-occurrence with mobile genetic elements [CITATION]. This approach measures resistance genes that are already present, but says less about the physiological conditions under which bacteria acquire or retain them in the first place."),
  P("Resistance acquisition and persistence are not purely a matter of gene presence. Oxidative stress increases the mutation rate through reactive-oxygen-species (ROS)-mediated DNA damage; DNA-repair pathways, particularly the SOS response and recombination repair, both fix this damage and, in the case of error-prone repair, generate the genetic variation on which selection for resistance can act; and general stress physiology, especially the stringent response (ppGpp), is a well-established driver of antibiotic tolerance and persister-cell formation across many antibiotic classes simultaneously, independent of resistance-gene acquisition itself [CITATION]. These three functional layers, redox, DNA and stress physiology, are mechanistically linked and each has documented relevance to resistance, but they are rarely profiled together as a system, and rarer still tested directly against measured resistance-gene burden in the same environmental samples."),
  P("Three gaps follow from this. Genes linked to redox stress, DNA repair and general stress physiology are typically studied as separate, independently interpreted modules, so the possibility that they are co-regulated as a single functional network remains unexamined. Wastewater studies that compare sites also rarely separate the effect of source type (hospital, community, agricultural or slaughterhouse discharge) from the effect of geography (city or catchment), even though most sampling designs conflate the two. Most consequentially, studies that build a resistance-adjacent gene framework rarely test it against measured resistance-gene data from the same samples, leaving the framework's practical relevance an untested assumption rather than a demonstrated result."),
  P("This study addresses all three gaps using 18 wastewater metagenomes from three source types and three cities in Khyber Pakhtunkhwa, Pakistan, sampled in a fully crossed design. We curated 903 KEGG Orthology (KO) genes into 15 functional modules spanning redox stress, DNA damage and fidelity, and stress physiology, and set out to (i) build and characterise a KO-level co-occurrence network across these modules and test its robustness to compositional-data and threshold artefacts, (ii) test whether module abundance differs by wastewater source type or by city, (iii) evaluate whether the network structure supports treating these genes as a coordinated system, and (iv) test this framework directly against antibiotic-resistance-gene (ARG) abundance measured in the same 18 samples via a SARG database annotation, rather than deferring that test to future work."),
];

console.log("intro ready");

// ============================================================
// 2. METHODS
// ============================================================
const methodsHeading = H1("2. Methods");

const m21head = H2("2.1 Study area and sampling design");
const m21body = [
  P("Wastewater samples were collected across three districts of Khyber Pakhtunkhwa, Pakistan (Mardan, Peshawar and Swat) to capture functional gene variation across a gradient of urban anthropogenic pressure. Within each district, samples were obtained from three wastewater source types representing distinct discharge profiles: hospital (H), community/municipal (C) and slaughterhouse (SL) wastewater. Two biological replicates were collected per source type per district, giving a balanced 3 (city) × 3 (source type) × 2 (replicate) design and 18 metagenomes in total (n=6 per source type, n=6 per city). Because city and source type were fully crossed, the two factors were tested independently in all downstream multivariate analyses. [TO CONFIRM: sampling dates, volumes, collection and storage protocol for all 18 sites, and whether hospital and slaughterhouse sites followed the same protocol, season and handling as the community sites; site coordinates for each of the 18 sites.]"),
];
const m22head = H2("2.2 Sequencing, quality control and functional annotation");
const m22body = [
  P("[TO CONFIRM: DNA extraction method, library preparation kit, sequencing platform, read depth per sample, quality-control and host-DNA-depletion pipeline, assembly/gene-catalogue construction, and the KEGG annotation tool and database version used to assign KO identifiers.] Per-sample KO abundances were aggregated into a functional abundance table of 10,333 KO families across 18 samples. Sequencing depth was approximately uniform across samples (coefficient of variation reported at 0.067 in earlier project notes; not independently re-verified for this draft) and Kruskal-Wallis testing of total depth across source types was reported as non-significant, i.e. depth is not expected to confound the environment comparisons below, but this should be re-confirmed against the raw depth values before submission."),
  P("The functional table used throughout this manuscript reflects the balanced 18-sample design described above, with two biological replicates confirmed for every source type and city combination."),
];
const m23head = H2("2.3 Target-module curation and KO-to-module mapping");
const m23body = [
  P("Fifteen functional modules were curated a priori to represent three mechanistically distinct groups: Group A, redox stress (glutathione metabolism, thioredoxin/peroxidase, nitric oxide stress, electron carrier balance, catalase/peroxidase); Group B, DNA damage and fidelity (SOS response, replication fidelity, nucleotide excision repair, recombination repair, OxyR oxidative DNA repair); and Group C, stress physiology and membrane adaptation (stringent response/ppGpp, two-component systems, sigma factors RpoS/RpoH, LPS remodelling, peptidoglycan remodelling). Modules were selected on three criteria: non-universal occurrence across environmental metagenomes; a mechanistically reasoned, bidirectional link to resistance-enabling physiology, such that both elevated and depleted states are biologically interpretable; and no direct overlap with resistance genes, mobile genetic elements or metal-resistance pathways, to keep the module set analytically independent of resistome content, so that any later association with measured ARG data (Section 2.8) could not be attributed to definitional overlap."),
  P("KOs were assigned to modules using KEGG pathway map identifiers where a module maps onto a defined pathway (for example map00480 for glutathione metabolism, map03420 for nucleotide excision repair, map02020 for two-component systems) and case-insensitive regular-expression matching against KEGG description fields for modules defined by protein-family membership. This produced 903 target KOs (8.7% of the 10,333-KO table)."),
  P("Two versions of this mapping exist in the underlying project files: an initial mapping produced during target selection, and a corrected mapping that resolves 18 KOs that had been placed in the wrong module by the initial search-term rules (for example, six 2-oxoglutarate/isocitrate dehydrogenase KOs that the initial rules had assigned to Recombination repair by keyword collision were reassigned to Electron carrier balance). All results in this manuscript were recomputed on the corrected mapping; the module sizes it yields are given in Table 1. This correction changes counts for 8 of the 15 modules but leaves the total at 903 KOs, and is disclosed here because two headline numbers in earlier project notes (a module correlation coefficient and a Kruskal-Wallis result) differ materially from the values reported here as a direct consequence of it."),
];
const table1_data = [
  ["Group","Module","No. KOs"],
  ["A: Redox stress","Electron carrier balance","115"],
  ["A: Redox stress","Glutathione metabolism","26"],
  ["A: Redox stress","Nitric oxide stress","21"],
  ["A: Redox stress","Thioredoxin/Peroxidase","11"],
  ["A: Redox stress","Catalase/Peroxidase","3"],
  ["B: DNA damage/fidelity","Recombination repair","100"],
  ["B: DNA damage/fidelity","OxyR oxidative DNA repair","28"],
  ["B: DNA damage/fidelity","Nucleotide excision repair (NER)","25"],
  ["B: DNA damage/fidelity","Replication fidelity","11"],
  ["B: DNA damage/fidelity","SOS response","4"],
  ["C: Stress physiology","Two-component systems","406"],
  ["C: Stress physiology","Stringent response (ppGpp)","83"],
  ["C: Stress physiology","Peptidoglycan remodeling","52"],
  ["C: Stress physiology","LPS remodeling","13"],
  ["C: Stress physiology","Sigma factors (RpoS/RpoH)","5"],
];
const table1 = dataTable(table1_data[0], table1_data.slice(1), [3200,4200,1600]);
const table1cap = Caption("Table 1. The 15 curated functional modules, grouped into three mechanistic categories, with the number of KEGG Orthology (KO) genes assigned to each module in the corrected 903-KO map (Section 2.3). Two-component systems accounts for 45% of all target KOs; this size imbalance is revisited as a caveat in Sections 3.3 and 4.");

const m24head = H2("2.4 Data preprocessing and module scoring");
const m24body = [
  P("Missing KO abundances were treated as zero, consistent with interpreting an absent KO as undetected functional capacity. All KO abundances were log10(x+1)-transformed to stabilise variance and compress the dynamic range of highly abundant KOs. A single module score was then defined, for each module and sample, as the sum of the log10(x+1)-transformed abundances of the KOs assigned to that module, giving an 18×15 module-score matrix. Summing rather than averaging preserves the contribution of module size to total functional capacity and is the definition used throughout this manuscript for every module-level analysis, including the module correlation matrix (Section 2.6), the differential analysis (Section 2.7) and the resistome-linkage analysis (Section 2.8); using a single, consistent module-score definition across all analyses was a deliberate correction relative to earlier project notes, which had mixed a mean-abundance definition with a sum-of-logs definition."),
  P("Twelve of the 903 target KOs had zero abundance in all 18 samples and were therefore excluded from pairwise correlation testing (Section 2.5), since a constant value cannot be assigned a Spearman rank correlation; they still contribute to their module's sum-of-logs score, where zero-abundance KOs correctly add nothing to the total."),
];
const m25head = H2("2.5 KO-level co-occurrence network");
const m25body = [
  P("A KO-level co-occurrence network was constructed from the log10(x+1)-transformed abundances of the 903 target KOs across the 18 samples. Spearman rank correlations were computed for all 407,253 unique KO pairs (903 choose 2), implemented as Pearson correlations on ranked abundances, which is algebraically equivalent to the Spearman coefficient. Statistical significance was assessed from the t-distribution approximation, t = ρ√[(n−2)/(1−ρ²)], with n−2=16 degrees of freedom and two-tailed p-values. KO pairs with |ρ|>0.60 and p<0.05 were retained as network edges. This threshold is conservative: at n=18 the critical ρ for p=0.05 is approximately 0.468, so the |ρ|>0.60 cutoff corresponds to p≈0.008 even before correction for multiple testing."),
  P("Network topology (edge count, density, degree distribution, connected components and module-level connectivity) was characterised in Python (NetworkX) and compared against an Erdős-Rényi random graph of identical node and edge count, used as a null model for clustering. Because 407,253 correlations were tested simultaneously, edge p-values were also corrected by the Benjamini-Hochberg (BH) false-discovery-rate procedure, with the denominator set to the full 407,253-pair space rather than only the edges surviving the initial |ρ|>0.60 filter."),
];
const m26head = H2("2.6 Module-level differential and correlation analysis");
const m26body = [
  P("Differences in module scores among the three wastewater source types (n=6 each) were tested with the Kruskal-Wallis H test, with effect size reported as epsilon-squared (ε²). Family-wise control across the 15 modules was assessed with both Bonferroni correction (α=0.0033) and BH-FDR. City (district) effects were tested in parallel using the same procedure, to distinguish source-type effects from geographic variation. Pairwise Spearman correlations among the 15 module scores were computed to summarise co-variation at the module level, using the single sum-of-logs score definition described in Section 2.4 for both this analysis and the differential test above."),
];
const m27head = H2("2.7 Multivariate ordination and dispersion analysis");
const m27body = [
  P("Community-level structure in the 18×15 module-score matrix was examined by principal component analysis (PCA) on per-module z-scored scores and by principal coordinates analysis (PCoA) on Bray-Curtis dissimilarities of raw module scores. Differences in multivariate location among source types and among cities were tested by permutational multivariate analysis of variance (PERMANOVA; 9,999 permutations) on both distance matrices, and by analysis of similarities (ANOSIM; 9,999 permutations) on the Bray-Curtis matrix as a rank-based complement that does not assume equal within-group dispersion. Homogeneity of multivariate dispersion among source types was tested with the permutation-based PERMDISP procedure (Anderson's betadisper equivalent; 9,999 permutations), evaluated before interpreting the PERMANOVA result. Because a single Slaughterhouse sample (SSLW2) was identified as a multivariate outlier by distance-to-centroid in ordination space, PERMANOVA was re-run after excluding this sample, after excluding the two most extreme Slaughterhouse samples, and on a Hospital-versus-Community comparison with the Slaughterhouse group dropped entirely, to test whether environmental separation is being suppressed or inflated by within-group heterogeneity."),
];

const m28head = H2("2.8 Resistome linkage (SARG)");
const m28body = [
  P("Antibiotic resistance gene (ARG) abundance for the same 18 wastewater metagenomes was obtained from a SARG (Structured Antibiotic Resistance Genes database) annotation, summarised at four levels of resolution: Type (21 broad drug/resistance categories), Subtype (748 specific gene families), Mechanism group and Mechanism subgroup (resistance mechanism, e.g. efflux pump, enzymatic inactivation, target alteration), plus a per-gene detail table cross-referencing predicted pathogen host. Values are SARG's standard per-sample relative-abundance units. SARG was used in preference to CARD (the Comprehensive Antibiotic Resistance Database) for two reasons. First, SARG's reference set and its associated read-mapping workflow are built specifically for short, unassembled metagenomic reads, and return abundance directly at the Type, Subtype and Mechanism levels used throughout this analysis; CARD's companion tool, the Resistance Gene Identifier, is designed around aligning longer, ideally assembled sequences against curated reference genes, and is comparatively less suited to profiling short-read data of the kind analysed here without an added assembly step. Second, these same 18 samples already had a CARD-based resistome characterisation from separate work by the authors; using SARG here tests the stress-physiology network against an independent resistance-gene database rather than reproducing the CARD analysis, and gives the resistome-linkage result reported below some measure of database independence."),
  P("The SARG sample set matches the 18-sample KO matrix used throughout the rest of this manuscript."),
  P("Four analyses tested whether the KO-level functional network (Sections 2.5-2.10) is associated with resistance-gene burden. (1) Total ARG burden (summed across all 21 SARG types) was correlated (Spearman) against each of the 15 module scores, with Benjamini-Hochberg FDR correction across the 15 tests, and tested for source-type differences with Kruskal-Wallis. (2) A full Type x Module correlation matrix (21 ARG types x 15 modules; one constant-abundance type, antibacterial_fatty_acid, was excluded, giving 300 valid tests) was computed with the same Spearman/BH-FDR procedure used for the KO-KO and module-module networks elsewhere in this manuscript, with a coarser Mechanism-group x Module matrix (8 categories x 15 modules = 120 tests) run in parallel as a cross-check at a resolution less vulnerable to the Type-level matrix's multiple-testing burden. Leave-one-out sensitivity (recomputing ρ after excluding each of the 18 samples in turn) was used to confirm FDR-significant pairs were not driven by any single sample. (3) Total ARG burden was fitted as an environmental vector onto the z-scored module-score PCA ordination (Section 2.7), using multiple linear regression of ARG burden on the first two principal component scores (equivalent in spirit to vegan::envfit); significance was assessed by permutation (9,999 permutations of sample labels). (4) Because hospital effluent has both the highest total ARG burden and, nominally, the highest mean Stringent response score, a confound check tested whether the Stringent response-ARG burden correlation reflects source-type grouping rather than a continuous relationship: the correlation was recomputed within each source type separately, in the pooled non-hospital subset (Community + Slaughterhouse, n=12, hospital excluded entirely), and as a partial (rank-residual) correlation after regressing out source type, and separately city, as three-level categorical covariates (code: 03_source_type_confound_check.py)."),
];

const m29taxhead = H2("2.9 Taxonomic attribution of Stringent response module abundance");
const m29taxbody = [
  P("To directly test whether the resistome linkage could reflect a single dominant, resistant, stress-tolerant taxon rather than a community-wide association, a taxon-stratified KEGG functional abundance table for the same 18 samples was obtained and cross-checked against the primary abundance matrix: unstratified per-KO totals for all 83 Stringent response module KOs matched the primary matrix exactly (Pearson r=1.0000), confirming a common underlying quantification rather than a separate annotation run."),
  P("Rows in this table are labelled by KO and, where stratified, a taxonomic lineage string (kingdom through species); taxonomic resolution is frequently incomplete below genus, so results are described as taxon-level rather than species-level. For each sample, the Stringent response module's 83 KOs were aggregated by contributing taxon (excluding the classifier's literal \"unclassified\" category, which is not a specific organism) to give, per sample: the number of distinct contributing taxa, the single largest contributor and its share of classified abundance, and the Shannon diversity of classified per-taxon contributions. As the decisive test, the module score (Section 2.4 definition) was recomputed with each sample's own single largest contributing taxon's abundance subtracted from each KO before the log10(x+1) transform, and the Spearman correlation of this taxon-excluded module score against total ARG burden was compared to the original Section 3.7 result (code: 04_taxonomic_dominance_check.py)."),
];

const m29head = H2("2.10 Robustness and sensitivity analyses");
const m29body = [
  P("Three additional analyses were run to test the sensitivity of the network results above to methodological choices. (i) Compositional sensitivity: because metagenomic KO abundances are compositional, a centred-log-ratio (CLR) transform was applied per sample across the 903 KOs (zero values replaced by half the smallest non-zero value in that sample) and the network-construction procedure in Section 2.5 was re-run on the CLR-transformed matrix; edge sets were compared to the primary log10(x+1) network by Jaccard overlap, hub-node overlap (top 15 by degree), and retention of the Electron carrier balance × Recombination repair bridge specifically. (ii) Threshold sensitivity: the network was rebuilt at |ρ| thresholds of 0.50, 0.55, 0.65, 0.70 and 0.75 (p<0.05 throughout) in addition to the primary 0.60 threshold. (iii) Bootstrap power analysis: for the five modules with the strongest (though non-significant) Kruskal-Wallis signal, empirical power at n=6, 8, 10, 12, 15, 20, 25 and 30 samples per group was estimated by parametric bootstrap (1,500 simulations per module per sample size), resampling with replacement from each source type's six observed module scores with Gaussian jitter (SD = 15% of the group's empirical standard deviation) to avoid exact-tie degeneracy. Full methods, code and output tables for all three analyses are in 9. step Robustness and Sensitivity Analyses/ in the project files."),
];

const m210head = H2("2.11 Software and reproducibility");
const m210body = [
  P("All statistical analyses were performed in Python (pandas, NumPy, SciPy, NetworkX, Matplotlib) [TO CONFIRM: exact versions and any R packages used for PERMANOVA/betadisper if vegan was used instead of a Python implementation for the original Step 8 analysis]. All KO-to-module mappings, module-score matrices, network edge lists, SARG-linkage tables and statistical outputs underlying this manuscript, including every figure, were regenerated directly from the corrected 903-KO abundance matrix and the corrected SARG tables for this draft, rather than carried forward from earlier intermediate files. Code and intermediate tables are available as Supplementary Materials (Section 6)."),
];

console.log("methods ready");

// ============================================================
// 3. RESULTS
// ============================================================
const resultsHeading = H1("3. Results");

const r31head = H2("3.1 The 903 target KOs form a single, non-random co-occurrence network");
const r31body = [
  P("Of 407,253 possible KO pairs, 53,775 (13.2%) met the |ρ|>0.60, p<0.05 edge criterion (Table 2). The resulting network was not a loose collection of small clusters: 886 of 903 KOs (98.1%) fell into a single connected component, with the remaining 17 KOs distributed across 16 small fragments of one to three nodes. Edges were predominantly positive (64.3%) and, among edges retained, strongly correlated on average (mean |ρ|=0.72). The network was substantially more clustered than expected by chance: mean local clustering coefficient 0.56 and transitivity 0.63, against 0.13 for both metrics in a degree-matched Erdős-Rényi null (4.2- and 4.8-fold enrichment respectively). After Benjamini-Hochberg correction over the full 407,253-pair test space, 47,821 of the 53,775 edges (88.9%) remained significant at q<0.05, indicating that the network is not primarily an artefact of uncorrected multiple testing."),
  P("Connectivity was uneven across modules and genes. The single most connected KO was K00406 (degree 328), and the module with the highest mean degree per gene was Nitric oxide stress (mean degree 208.9 across 21 KOs, versus a network-wide mean of 119.1 across all 903 KOs), despite this module ranking only seventh by Kruskal-Wallis effect size in the differential analysis below (Section 3.2). This combination, high network centrality with a comparatively modest univariate signal, suggests that nitric oxide stress genes function as an integrative hub rather than as source-type-specific markers in this dataset. A conventional gene-level node-link diagram of the full network (903 nodes, 53,775 edges) was not legible at any print resolution because of edge overplotting, even after restricting to the giant component or raising the visualization threshold; Figure 1 therefore summarises the network at the module level instead, with gene-level edge counts by module pair given in Figure 7 and Tables 5-6. Figure 2 shows the full degree distribution and the sensitivity of edge count to the |ρ| threshold, which scales smoothly from 88,398 edges at |ρ|>0.50 to 18,510 at |ρ|>0.75 with no discontinuity around the 0.60 threshold used throughout this manuscript."),
  img(`${FIG}/Figure1_Network_Backbone.png`, 400, 391),
  Caption("Figure 1."),
  img(`${FIG}/Figure2_Degree_and_Threshold.png`, 560, 216),
  Caption("Figure 2."),
];

const r31bhead = H2("3.1.1 Hub genes and functional-group connectivity");
const r31bbody = [
  P("The 15 highest-degree KOs (Table 5) span three modules, most from Two-component systems (6 of 15, reflecting that module's size), alongside Electron carrier balance, Nitric oxide stress, Glutathione metabolism and Peptidoglycan remodeling. No individual DNA-repair-group KO appears among the top 15 hubs, even though Recombination repair participates heavily in cross-group edges in aggregate (Section 3.3); single-gene connectivity and module-level connectivity are not the same claim, and both are reported here for that reason. At the functional-group level (Table 6), within-group edge density was highest for Group A-Redox (24.0% of within-group pairs significant) and lowest, proportionally, for Group C-Stress (11.7%, despite the largest raw edge count due to Two-component systems' size); cross-group density was intermediate throughout (11.6-16.8%), and all six group-pair categories were positive-edge-dominant (60-67%)."),
];

const table2_data = [
  ["Metric","Value"],
  ["KOs analysed","903 (12 with zero variance excluded from pairwise testing)"],
  ["Total KO pairs tested","407,253"],
  ["Significant edges (|ρ|>0.60, p<0.05)","53,775"],
  ["Network density","0.132"],
  ["Mean |ρ| among edges","0.722"],
  ["Positive-edge fraction","64.3%"],
  ["Giant component size","886 / 903 KOs (98.1%)"],
  ["Mean node degree","119.1"],
  ["Maximum node degree","328 (K00406)"],
  ["Mean local clustering coefficient (network / ER null)","0.558 / 0.132 (4.2×)"],
  ["Transitivity (network / ER null)","0.633 / 0.132 (4.8×)"],
  ["Edges surviving BH-FDR (q<0.05, full 407,253-pair denominator)","47,821 (88.9%)"],
];
const table2 = dataTable(table2_data[0], table2_data.slice(1), [5800,3200]);
const table2cap = Caption("Table 2. Summary topology statistics for the KO-level co-occurrence network, independently computed for this manuscript from the corrected 903-KO abundance matrix (Section 2.5). ER = Erdős-Rényi random-graph null model with identical node and edge count.");

const table5_data = [
  ["Rank","KO ID","Module","Group","Degree"],
  ["1","K00406","Two-component systems","C-Stress","328"],
  ["2","K12531","Two-component systems","C-Stress","319"],
  ["3","K18351","Two-component systems","C-Stress","319"],
  ["4","K15862","Two-component systems","C-Stress","318"],
  ["5","K00626","Two-component systems","C-Stress","317"],
  ["6","K11526","Two-component systems","C-Stress","317"],
  ["7","K03941","Electron carrier balance","A-Redox","315"],
  ["8","K04561","Nitric oxide stress","A-Redox","314"],
  ["9","K00356","Electron carrier balance","A-Redox","312"],
  ["10","K08305","Peptidoglycan remodeling","C-Stress","312"],
  ["11","K00799","Glutathione metabolism","A-Redox","312"],
  ["12","K15864","Nitric oxide stress","A-Redox","310"],
  ["13","K08082","Two-component systems","C-Stress","310"],
  ["14","K02305","Nitric oxide stress","A-Redox","310"],
  ["15","K00681","Glutathione metabolism","A-Redox","309"],
];
const table5 = dataTable(table5_data[0], table5_data.slice(1), [900,1500,3300,1900,1400]);
const table5cap = Caption("Table 5. The 15 highest-degree KOs in the primary co-occurrence network (|ρ|>0.60, p<0.05; network mean degree = 119.1). Six of 15 belong to Two-component systems, the largest module (406 of 903 KOs).");

const table6_data = [
  ["Group pair","KO pairs tested","Sig. edges","% sig.","Mean ρ (sig.)","% positive"],
  ["A-Redox × A-Redox","15,051","3,613","24.0%","0.150","59.6%"],
  ["A-Redox × B-DNA","29,058","4,880","16.8%","0.185","61.7%"],
  ["A-Redox × C-Stress","95,700","15,133","15.8%","0.195","62.7%"],
  ["B-DNA × B-DNA","13,861","1,810","13.1%","0.234","64.5%"],
  ["B-DNA × C-Stress","91,850","10,692","11.6%","0.218","64.3%"],
  ["C-Stress × C-Stress","150,975","17,647","11.7%","0.262","67.3%"],
];
const table6 = dataTable(table6_data[0], table6_data.slice(1), [2600,1900,1500,1100,1700,1400]);
const table6cap = Caption("Table 6. KO-level edge summary by functional-group pairing (three within-group, three cross-group combinations). % sig. = percentage of testable KO pairs meeting the |ρ|>0.60, p<0.05 edge criterion.");

console.log("results 3.1 ready");

const r32head = H2("3.2 Module abundance differs only modestly, and non-significantly, by wastewater source type");
const r32body = [
  P("Using the single sum-of-logs module-score definition (Section 2.4) applied to the corrected 903-KO module map, no module reached p<0.05 for a Kruskal-Wallis test of source-type differences (Table 3, Figure 4). The module with the strongest, though still non-significant, signal was Stringent response (ppGpp) (H=4.11, p=0.128, ε²=0.14), followed by Glutathione metabolism (p=0.160, ε²=0.11) and Two-component systems (p=0.164, ε²=0.11). LPS remodelling, which had been reported elsewhere as significant (p=0.041) under a depth-normalised score, was not significant on raw module scores (p=0.587); we treat the depth-normalised result as exploratory rather than as a confirmed finding, since it does not reproduce under the primary (raw, sum-of-logs) scoring definition used throughout this manuscript. None of the 15 modules survived Bonferroni or BH-FDR correction across the 15 tests. A parallel Kruskal-Wallis test across the three cities found no coherent pattern (strongest: Replication fidelity, p=0.038, uncorrected, 1 of 15 tests); given the absence of any prior hypothesis for a city-level effect and the lack of correction, we do not interpret this as a finding. Notably, Stringent response, the module later shown to be significantly associated with ARG burden (Section 3.7), does not itself differ significantly by source type here, indicating that its resistome association (Section 3.7) is not a simple restatement of a source-type effect."),
  P("Directionally, Slaughterhouse scored numerically lowest in 11 of 15 modules and Community scored numerically highest in 9 of 15 modules, consistent with a modest source-type gradient; we report this pattern descriptively rather than as a statistically supported result, and avoid characterising Slaughterhouse as functionally depleted given that none of the underlying comparisons reach significance at n=6 per group. Section 3.6 quantifies, by bootstrap simulation, how much larger a study would need to be to resolve the strongest of these trends."),
  img(`${FIG}/Figure4_Module_Boxplots_By_Environment.png`, 560, 353),
  Caption("Figure 4."),
];

const table3_data = [
  ["Module","H","p (raw)","ε²","p (BH-FDR)"],
  ["Stringent response (ppGpp)","4.11","0.128","0.140","0.522"],
  ["Glutathione metabolism","3.66","0.160","0.111","0.522"],
  ["Two-component systems","3.61","0.164","0.108","0.522"],
  ["Peptidoglycan remodeling","3.59","0.166","0.106","0.522"],
  ["Catalase/Peroxidase","3.13","0.209","0.076","0.522"],
  ["Recombination repair","3.13","0.209","0.076","0.522"],
  ["Nitric oxide stress","2.54","0.281","0.036","0.602"],
  ["Sigma factors (RpoS/RpoH)","1.63","0.444","−0.025","0.727"],
  ["OxyR oxidative DNA repair","1.31","0.519","−0.046","0.727"],
  ["Nucleotide excision repair (NER)","1.30","0.523","−0.047","0.727"],
  ["Replication fidelity","1.20","0.548","−0.053","0.727"],
  ["LPS remodeling","1.06","0.587","−0.062","0.727"],
  ["Electron carrier balance","0.92","0.630","−0.072","0.727"],
  ["Thioredoxin/Peroxidase","0.43","0.805","−0.104","0.863"],
  ["SOS response","0.22","0.895","−0.119","0.895"],
];
const table3 = dataTable(table3_data[0], table3_data.slice(1), [3200,1300,1500,1300,1700]);
const table3cap = Caption("Table 3. Kruskal-Wallis test of module-score differences among the three wastewater source types (Hospital, Community, Slaughterhouse; n=6 each), ranked by raw p-value. H = Kruskal-Wallis test statistic; ε² = epsilon-squared effect size; p (BH-FDR) = Benjamini-Hochberg-corrected p-value across the 15 tests. No module reaches p<0.05 before or after correction.");

const r33head = H2("3.3 A modest, corrected redox-DNA association within a broader module correlation structure");
const r33body = [
  P("The strongest module-level correlation in the dataset, by a wide margin, was between Glutathione metabolism and Nitric oxide stress (Spearman ρ=0.93, BH-FDR q<0.001), two modules within the same redox-stress group (Figure 3). The Electron carrier balance and Recombination repair pair, the redox-DNA axis motivating this study, was also significantly correlated (ρ=0.63, q<0.05), but ranked outside the ten strongest of 105 module pairs (Table 4); several stronger correlations involved Two-component systems, which, at 406 of 903 target KOs (45%), is disproportionately large and is therefore likely to correlate with most other modules on size alone, independent of any specific biological coupling. This is visible directly in the KO-level edge-count matrix (Figure 7): Two-component systems has the highest edge count against every other module, consistent with size rather than necessarily reflecting stronger biological coupling. We flag this as a compositional/size caveat (Section 4) rather than treating Two-component systems' correlations as equally interpretable to the smaller, more evenly sized modules."),
  P("This ρ=0.63 (module level) / 2,104-edge (KO level) result differs substantially from a figure of r=0.87 module-level correlation reported in earlier project notes for the same module pair. We were unable to reproduce r=0.87 under any of the module-score and KO-mapping definitions available in the project files (Section 2.3-2.4); depending on which combination of (uncorrected or corrected) module mapping and (mean-abundance or sum-of-logs) scoring is used, the pair's module-level correlation ranges from 0.53 to 0.76. The value reported here, ρ=0.63, uses the single mapping and scoring definition applied consistently throughout this manuscript and is the value we consider defensible. The pair remains significantly and positively correlated under every definition tested, so the qualitative claim, that electron-carrier and recombination-repair gene abundance co-vary across these samples, is retained; the magnitude originally reported is not. Section 3.5 additionally shows that this specific association is stable under a compositional-data sensitivity transform."),
  img(`${FIG}/Figure3_Module_Correlation_Heatmap.png`, 470, 426),
  Caption("Figure 3."),
  img(`${FIG}/Figure7_Module_EdgeCount_Heatmap.png`, 480, 444),
  Caption("Figure 7."),
];

const table4_data = [
  ["Module A","Module B","Spearman ρ","q (BH-FDR)"],
  ["Glutathione metabolism","Nitric oxide stress","0.93","<0.001"],
  ["Electron carrier balance","Two-component systems","0.80","0.008"],
  ["Recombination repair","Two-component systems","0.79","0.008"],
  ["Glutathione metabolism","Replication fidelity","0.78","0.005"],
  ["Recombination repair","Thioredoxin/Peroxidase","0.78","0.006"],
  ["Nitric oxide stress","Sigma factors (RpoS/RpoH)","−0.74","0.010"],
  ["Nitric oxide stress","Two-component systems","0.72","0.017"],
  ["Sigma factors (RpoS/RpoH)","Thioredoxin/Peroxidase","−0.72","0.017"],
  ["Glutathione metabolism","Two-component systems","0.70","0.021"],
  ["Electron carrier balance","Recombination repair","0.63","0.049"],
];
const table4 = dataTable(table4_data[0], table4_data.slice(1), [3100,3100,1400,1400]);
const table4cap = Caption("Table 4. The ten strongest module-score correlations (Spearman) of the 105 unique module pairs, ranked by |ρ|. The redox-DNA pair motivating this study (Electron carrier balance × Recombination repair, bottom row) is significant but is not among the top-ranked correlations in the matrix. Full 15×15 matrix in Figure 3 / Supplementary Table S3.");

console.log("results 3.2-3.3 ready");

const r34head = H2("3.4 A directional but statistically unresolved separation by source type, none by city");
const r34body = [
  P("Principal component analysis of the 18×15 z-scored module-score matrix placed 46.2% of variance on PC1 and 67.8% on PC1+PC2; a complementary Bray-Curtis PCoA placed 87.1% of variance on its first axis (Figure 5). The very different variance concentration between the two ordinations reflects the different geometry of Euclidean distance on z-scored data versus Bray-Curtis distance on raw-magnitude module scores, and the two should be read as complementary views of the same 18×15 matrix rather than as conflicting results. PERMANOVA found no significant effect of source type (F=1.77, p=0.14 on Bray-Curtis distance; F=1.18, p=0.30 on z-scored Euclidean distance) or city (F=0.72, p=0.62) on the module-score profile. ANOSIM, a rank-based method that does not assume equal within-group dispersion, reached the same conclusion (source type: R=0.028, p=0.30; city: R=−0.033, p=0.59), reinforcing that the PERMANOVA result is not an artefact of dispersion heterogeneity."),
  P("A formal PERMDISP test found no significant heterogeneity of multivariate dispersion among source types (p=0.69-0.91 across both distance metrics, Figure 6), despite Slaughterhouse showing the numerically highest mean dispersion; one Slaughterhouse sample (SSLW2) was identified as a clear multivariate outlier and accounted for most of this numerical elevation. Removing SSLW2, removing the two most extreme Slaughterhouse samples, or dropping the Slaughterhouse group entirely and comparing Hospital against Community directly all reduced rather than increased the PERMANOVA signal, indicating that the modest source-type separation is not being suppressed by an outlier or by unequal dispersion; it is better described as a genuine but underpowered trend at n=6 per group than as a result confounded by a single sample."),
  img(`${FIG}/Figure5_Ordination_PCA_PCoA.png`, 560, 250),
  Caption("Figure 5."),
  img(`${FIG}/Figure6_Beta_Dispersion.png`, 420, 328),
  Caption("Figure 6."),
];

const r35head = H2("3.5 Robustness of the network to a compositional-data sensitivity check");
const r35body = [
  P("Because metagenomic KO abundances are compositional, the primary log10(x+1) Spearman network can in principle inflate apparent co-occurrence independent of true biological association. Rebuilding the network on centred-log-ratio (CLR)-transformed abundances at the same |ρ|>0.60, p<0.05 criterion produced a similarly sized network (55,283 edges versus 53,775 in the primary network) but only partial edge-level overlap: Jaccard overlap = 0.34 (27,630 edges shared out of 81,428 in the union), and only 4 of the 15 top hub KOs were shared between the two networks (Figure 8). This indicates that the fine-grained topology of the network, specifically, which individual KOs are hubs, is moderately sensitive to the compositional transform and should be read with that caveat."),
  P("The specific result motivating this study was more robust than the network's topology as a whole: the Electron carrier balance × Recombination repair bridge retained 2,160 of its edges under the CLR transform against 2,104 under log10(x+1), a difference of under 3% (Figure 8B). We read this as evidence that the headline, hypothesis-relevant association is not an artefact of the compositional transform, even though claims about which specific genes act as network hubs should be interpreted more cautiously given the topology-level sensitivity observed here."),
  img(`${FIG}/Figure8_Compositional_Sensitivity.png`, 550, 246),
  Caption("Figure 8."),
];

const r36head = H2("3.6 A larger study is needed to resolve the observed source-type trends");
const r36body = [
  P("Bootstrap power simulation for the five modules with the strongest observed (non-significant) Kruskal-Wallis signal (Section 2.10) indicated that approximately 15 samples per source type would be needed to detect the Stringent response, Two-component systems and Peptidoglycan remodeling trends at 80% power; Glutathione metabolism would need approximately 20 per group, and Catalase/Peroxidase approximately 25 (Figure 9). All estimates are 2.5-4 times the current n=6 per source type, confirming that the non-significant results in Section 3.2 reflect a power limitation rather than an informative null result, and giving a concrete, defensible sampling target for a follow-up study designed to resolve these trends rather than simply repeating the current design at a larger but still arbitrary sample size."),
  img(`${FIG}/Figure9_Bootstrap_Power_Analysis.png`, 460, 329),
  Caption("Figure 9."),
];

console.log("results 3.4-3.6 ready");

const r37head = H2("3.7 The stringent response module is associated with resistance-gene burden");
const r37body = [
  P("Total ARG burden (SARG, all 21 types summed) differed significantly by wastewater source type (Kruskal-Wallis H=11.42, p=0.0033; mean burden Hospital 6.99, Community 3.10, Slaughterhouse 3.04), roughly 2.3-fold higher in hospital effluent than in the other two source types. This is the only quantity tested in this manuscript, module score or ARG burden, that reaches significance for source type at n=6 per group, and stands in contrast to the null result for every individual functional module in Section 3.2."),
  P("Of the 15 functional modules, Stringent response (ppGpp) was the only one significantly correlated with total ARG burden after Benjamini-Hochberg correction (Spearman ρ=0.73, raw p=0.0007, q=0.0098, n=18; Figure 11A); no other module approached significance (next-strongest: Nucleotide excision repair, q=0.174)."),
  P("At finer resolution, the 21 SARG resistance types were each correlated against all 15 module scores (300 valid tests after excluding one constant-abundance type). Fifteen type-module pairs survived Benjamini-Hochberg correction at q<0.05 (Table 7, Figure 10), and the pattern was concentrated rather than scattered: Stringent response (ppGpp) was implicated in 7 of the 15 significant pairs (multidrug, sulfonamide, aminoglycoside, bacitracin, chloramphenicol, beta-lactam and trimethoprim resistance, ρ 0.67-0.83, including multidrug resistance specifically, ρ=0.83, Figure 11B), and Two-component systems in 3 more (bacitracin, multidrug, mupirocin, ρ 0.70-0.77). A coarser Mechanism-group x Module cross-check (120 tests, 8 mechanism categories) gave a consistent result: 9 of 120 pairs survived correction, again dominated by Stringent response (4 of 9 pairs, including the single strongest association in either matrix, Efflux pump mechanism x Stringent response, ρ=0.86, q=0.0005). Leave-one-out resampling (recomputing ρ after excluding each sample in turn) showed all four spot-checked top pairs remained significant and stable in direction regardless of which single sample was excluded (e.g. multidrug x Stringent response: full-data ρ=0.83, leave-one-out range 0.80-0.92), indicating the association is not an artefact of any one sample."),
  P("Because hospital effluent is elevated in both total ARG burden and, nominally, Stringent response score (Table 3), a confound check tested whether the module-ARG correlation above is a source-type artefact rather than a continuous relationship (Supplementary Table S8). The correlation held with hospital samples excluded entirely (Community + Slaughterhouse pooled, n=12: ρ=0.70, p=0.011), and within Slaughterhouse alone it was the single strongest sub-group result observed anywhere in this analysis (n=6, ρ=0.94, p=0.0048); Hospital-only and Community-only subsets showed the same positive direction but did not reach significance at n=6 (ρ=0.77, p=0.072 and ρ=0.43, p=0.40 respectively), consistent with the power limitation already noted for all n=6 comparisons in this manuscript (Section 4.1). A partial (rank-residual) correlation controlling for source type left the association materially unchanged (ρ=0.68, p=0.0017), as did controlling for city instead (ρ=0.73, p=0.0005). Taken together, these results indicate the Stringent response-ARG burden correlation is not attributable to hospital samples alone being high on both variables."),
  P("Fitting total ARG burden as a vector onto the z-scored module-score PCA ordination (Section 3.4) explained a moderate share of variance (R²=0.29) but did not reach significance under permutation testing (9,999 permutations, p=0.074). This is weaker than, and not in conflict with, the direct module-level correlations above: ARG burden's association with the module-score profile is concentrated in one or two modules (principally Stringent response) rather than distributed across the broader multivariate structure that PC1/PC2 summarise, so a whole-ordination vector fit is expected to be a less sensitive test of this specific, module-concentrated signal than a direct pairwise correlation."),
  img(`${FIG}/Figure11_Stringent_Response_vs_ARG.png`, 560, 253),
  Caption("Figure 11."),
  img(`${FIG}/Figure10_ARG_Type_Module_Heatmap.png`, 480, 430),
  Caption("Figure 10."),
];

const table7_data = [
  ["ARG type","Module","Spearman ρ","q (BH-FDR)"],
  ["multidrug","Stringent response (ppGpp)","0.83","0.006"],
  ["bacitracin","Two-component systems","0.77","0.029"],
  ["sulfonamide","Stringent response (ppGpp)","0.74","0.031"],
  ["multidrug","Two-component systems","0.74","0.031"],
  ["other_peptide_antibiotics","Peptidoglycan remodeling","0.73","0.031"],
  ["aminoglycoside","Stringent response (ppGpp)","0.71","0.038"],
  ["bacitracin","Stringent response (ppGpp)","0.71","0.038"],
  ["quinolone","Replication fidelity","0.70","0.038"],
  ["mupirocin","Two-component systems","0.70","0.038"],
  ["bacitracin","Recombination repair","0.70","0.038"],
  ["chloramphenicol","Stringent response (ppGpp)","0.69","0.038"],
  ["bacitracin","Thioredoxin/Peroxidase","0.68","0.046"],
  ["beta_lactam","Stringent response (ppGpp)","0.68","0.046"],
  ["multidrug","Recombination repair","0.67","0.049"],
  ["trimethoprim","Stringent response (ppGpp)","0.67","0.049"],
];
const table7 = dataTable(table7_data[0], table7_data.slice(1), [2600,3200,1500,1500]);
const table7cap = Caption("Table 7. All 15 ARG type x module pairs surviving Benjamini-Hochberg correction (q<0.05) of the 300-test Type x Module matrix (Section 3.7, Figure 10). Stringent response (ppGpp) accounts for 7 of 15 pairs, spanning mechanistically unrelated drug classes.");

console.log("results 3.7 ready");

const r38head = H2("3.8 The stringent response-resistome association is not attributable to a single dominant taxon");
const r38body = [
  P("Section 4.1 of an earlier version of this manuscript identified a shared taxonomic driver, a single resistant, stress-tolerant organism carrying elevated levels of both stringent-response genes and ARGs simply because it is more abundant in some samples, as the single highest-priority unresolved question for the Section 3.7 result. This was tested directly using a taxon-stratified KEGG functional abundance table for the same 18 samples (the same underlying quantification as the primary abundance matrix: unstratified per-KO totals for all 83 Stringent response module KOs match Section 2.2's corrected matrix exactly, Pearson r=1.0000), which decomposes each KO's abundance by contributing taxon."),
  P("Taxonomic resolution in this table is variable and frequently incomplete below genus (the species field is empty in the large majority of rows), consistent with the known limits of short-read taxonomic classification; results below are accordingly described as taxon-level, not species-level. Between 47% and 76% of each sample's module abundance falls in the classifier's literal \"unclassified\" category, which is not a specific organism and is excluded from the dominance test itself; this is a normal feature of metagenomic classification, not evidence for or against a taxonomic driver."),
  Mixed([
    {text: "Among classified reads, 418 distinct taxa contribute to the Stringent response module across the 18 samples (Table 8). No single taxon accounts for more than 44% of classified module abundance in any sample, and the majority of samples are below 20%. The single largest contributor also differs from sample to sample: 10 distinct genera serve as the top contributor across the 18 samples (most frequently an unresolved Comamonadaceae lineage within Betaproteobacteria/Burkholderiales, and "},
    {text: "Bacteroides", italic: true},
    {text: ", each top in 3-4 samples; also "},
    {text: "Pseudomonas", italic: true}, {text: ", "},
    {text: "Vibrio", italic: true}, {text: ", "},
    {text: "Flavobacterium", italic: true}, {text: ", "},
    {text: "Desulfomicrobium", italic: true},
    {text: " and three further unresolved lineages), rather than one recurring organism (Table 8, Figure 12A). Shannon diversity of classified per-taxon contributions averaged 3.60 (range 2.83-3.98) against a theoretical maximum of ln(418)=6.04 for this taxon set, indicating a broadly, if unevenly, distributed signal rather than concentration in a small number of taxa."},
  ]),
  P("The decisive test recomputed the Stringent response module score (same sum-of-log10(x+1) definition used throughout this manuscript, Section 2.4) with each sample's own single largest classified contributor subtracted out KO-by-KO before the log transform, then re-tested the Spearman correlation against total ARG burden. The correlation was essentially unchanged: ρ=0.725 (p=0.0007) originally versus ρ=0.769 (p=0.0002) with the top taxon excluded (Figure 12B), a directionally stronger, not weaker, association. This is not consistent with the module-ARG burden link being carried by a single dominant organism: removing each sample's largest individual contributor left the signal intact."),
  img(`${FIG}/Figure12_Taxonomic_Dominance_Check.png`, 560, 258),
  Caption("Figure 12."),
];

const table8_data = [
  ["Sample","Source type","Unclassified","Top classified taxon","Top taxon share","Shannon diversity"],
  ["MHW1","Hospital","70%","Pseudomonas","21%","3.60"],
  ["MHW2","Hospital","76%","unresolved (Bacteroidota)","16%","3.74"],
  ["PHW1","Hospital","56%","unresolved (Comamonadaceae)","19%","3.63"],
  ["PHW2","Hospital","64%","unresolved (Rhodocyclales)","10%","3.84"],
  ["SHW1","Hospital","62%","unresolved (Comamonadaceae)","11%","3.84"],
  ["SHW2","Hospital","51%","unresolved (Comamonadaceae)","14%","3.58"],
  ["MCW1","Community","66%","Desulfomicrobium","8%","3.75"],
  ["MCW2","Community","53%","unresolved (Betaproteobacteria)","16%","3.58"],
  ["PCW1","Community","56%","unresolved (Comamonadaceae)","12%","3.82"],
  ["PCW2","Community","51%","Vibrio","44%","2.90"],
  ["SCW1","Community","67%","Pseudomonas","12%","3.98"],
  ["SCW2","Community","58%","Bacteroides","24%","3.41"],
  ["MSLW1","Slaughterhouse","67%","unresolved (Bacteroidales)","8%","3.82"],
  ["MSLW2","Slaughterhouse","63%","unresolved (Rhodocyclales)","8%","3.79"],
  ["PSLW1","Slaughterhouse","58%","Bacteroides","10%","3.83"],
  ["PSLW2","Slaughterhouse","47%","Flavobacterium","38%","2.83"],
  ["SSLW1","Slaughterhouse","67%","unresolved (Bacteroidales)","8%","3.79"],
  ["SSLW2","Slaughterhouse","74%","Bacteroides","17%","3.02"],
];
const table8 = dataTableItalicCol(table8_data[0], table8_data.slice(1), [1400,1800,1500,2900,1500,1600], 3);
const table8cap = Caption("Table 8. Taxonomic composition of the Stringent response module, per sample (Section 3.8). Unclassified = share of module abundance not assigned to any taxon by the classifier. Top taxon share = that taxon's share of classified (non-unclassified) abundance only. Shannon diversity computed on classified per-taxon proportions (max possible for 418 taxa = 6.04). Full detail: Supplementary Table S9.");

console.log("results 3.8 ready");

// ============================================================
// 4. DISCUSSION
// ============================================================
const discHeading = H1("4. Discussion");

const d0 = P("The central result of this study is that a stress-physiology gene network built entirely from KEGG functional-abundance data, without any resistance-gene information informing its construction, is measurably associated with actual antibiotic-resistance-gene burden in the same samples. The Stringent response (ppGpp) module correlates with total ARG burden and with seven individual, mechanistically unrelated resistance-drug classes, and an independent mechanism-level cross-check reproduces the same pattern. This moves the central claim of this manuscript from a structural one, that these genes co-occur, to a substantive one, that their co-occurrence network carries information relevant to resistance surveillance. The result is consistent with an extensive existing literature establishing the stringent response as a driver of antibiotic tolerance and persister-cell formation across many antibiotic classes simultaneously, largely independent of specific resistance-gene acquisition [CITATION], which is the most parsimonious explanation for why one module tracks resistance to structurally and mechanistically distinct drug classes at once rather than a single class. A direct test using taxon-stratified functional data also weighs against the most obvious alternative explanation, that a single dominant resistant organism carries both signals: classified module abundance is spread across 418 distinct taxa, no single taxon exceeds 44% of classified abundance in any sample, and the association survives removal of each sample's own largest contributor. This is a genuine strengthening of the resistome-relevance claim, since it directly addresses the confound most likely to be raised against this result.");

const d1 = P("This result rests on a structural precondition established earlier in the manuscript: redox, DNA-repair and stress-physiology genes do not behave as independent modules in these wastewater communities. Ninety-eight percent of the 903 target KOs sit in one connected co-occurrence network, and that network is substantially more clustered than a random graph of the same size, a pattern that survives false-discovery-rate correction over the full pair space and, for the specific redox-DNA bridge motivating this study, a compositional-data sensitivity check. Had the modules turned out to be unconnected, there would have been no basis for treating them as a coordinated system, and no reason to expect a single module within that system to track a resistome-wide outcome as broadly as Stringent response does.");

const d2 = P("Nitric oxide stress genes were the most connected module per gene in the network (mean degree 209, against a network mean of 119) despite ranking only seventh among 15 modules in the differential analysis (ε²=0.036, Table 3), and despite not appearing in the resistome linkage. Nitric oxide is mechanistically well placed to act as a network hub: it is directly mutagenic to DNA through deamination and nitrosative damage, it disrupts iron-sulfur clusters in the electron transport chain, and NO-responsive regulators intersect with general stress signalling. That it is highly central in the network but not the module linked to ARG burden indicates that network centrality and resistome relevance are separate properties in this dataset; Stringent response was neither the highest-degree nor the most differentially abundant module, but was the one substantively linked to the outcome that matters for surveillance.");

const d3 = P("Two-component systems contributed 406 of the 903 target KOs (45%), and this size difference needs to be kept in view when reading the network, the module correlation matrix, and the resistome linkage, where Two-component systems is the second-most-implicated module (3 of 15 significant type-module pairs, versus Stringent response's 7). A module with several hundred genes will tend to have high edge counts and to correlate with more variables simply because it has more opportunities to do so; Figure 7 makes this concrete for the KO-KO network, showing Two-component systems as the highest-edge-count partner for every other module in the matrix. This does not fully explain the resistome result, since Stringent response, a mid-sized module at 83 KOs, not the largest, carries more than twice as many significant ARG associations as Two-component systems; it is nonetheless a real limitation of interpreting Two-component systems' contribution at face value, and a reason to treat Stringent response, not module size generally, as the primary resistome-relevant finding.");

const d3b = P("A related and more general compositional caveat applies to the KO-level network as a whole. This was tested directly by rebuilding the network on centred-log-ratio-transformed abundances: the two networks overlapped only partially (Jaccard = 0.34), and only 4 of the top 15 hub KOs were shared between them, indicating that specific hub identities should be treated as provisional rather than definitive. The Electron carrier balance and Recombination repair bridge itself, in contrast, was essentially unaffected (97% edge retention), which is the more important result for this study's structural claim, but the broader hub-level sensitivity is a genuine limitation of the network as characterised here and should be weighed accordingly when this network is used to prioritise individual genes (for example, glutathione S-transferase, K00799, Table 5) for follow-up work. The compositional sensitivity analysis was not re-run on the resistome linkage; this is identified as a specific, unresolved gap in the Limitations below.");

const d4 = P("The redox-DNA pair motivating this study, Electron carrier balance and Recombination repair, was significantly co-occurring both at the KO level (2,104 network edges before FDR correction) and at the module level (ρ=0.63, Table 4), and this association survived the compositional sensitivity check. Neither module, however, was among the modules linked to ARG burden; Recombination repair appears only as a secondary contributor (2 of 15 significant type-module pairs) and Electron carrier balance not at all. This is consistent with, and does not on its own confirm, the proposed pathway in which disrupted electron transport increases ROS production, ROS damages DNA, and recombination repair responds to that damage. It means the redox-DNA bridge and the resistome association are two separate results from this dataset, not the same finding under two names: the redox-DNA bridge supports the structural claim that these gene categories are coupled, while Stringent response is the specific module doing the resistome-relevant work.");

const d5 = P("Module abundance differed only directionally, not significantly, by wastewater source type, and not at all by city, a conclusion reached independently by two complementary multivariate tests (PERMANOVA and ANOSIM). Total ARG burden, by contrast, did differ significantly by source type, roughly 2.3-fold higher in hospital effluent. Because Stringent response itself did not differ significantly by source type (Table 3), its correlation with ARG burden across all 18 samples is not simply a restatement of a shared source-type effect between two independently-varying group means; the association held under leave-one-out resampling and, visually, samples of all three source types span a broad and overlapping range of both variables (Figure 11) rather than separating into three discrete clusters. This was tested directly rather than left as a hypothetical concern (Supplementary Table S8): the correlation remained significant with hospital samples excluded entirely (Community and Slaughterhouse only, n=12, ρ=0.70, p=0.011), and a partial correlation controlling for source type (ρ=0.68, p=0.0017) or for city (ρ=0.73, p=0.0005) left the association materially unchanged, indicating it is not attributable to the source-type grouping.");

const d6head = H2("4.1 Limitations");
const d6 = [
  P("First, and most consequentially, statistical power is limited. Bootstrap simulation indicates that 15-25 samples per source type, roughly 2.5-4 times the current n=6, would be needed to resolve the strongest observed module-level trends at 80% power. Non-significance at n=6 is therefore a power limitation, not evidence that the underlying differences do not exist, but it should not be read as a confirmed finding either; hedged language is used consistently throughout the Results for this reason. The resistome-linkage tests use the full n=18, which strengthens them relative to the source-type comparisons, but 18 samples remains a modest basis for a 300-test correlation matrix, and the 15 pairs surviving correction (Table 7) should be treated as a defensible but not final estimate of which ARG types associate with which modules."),
  P("Second, the KO-level network relies on Spearman correlation applied to compositional abundance data. This was tested directly for the core network rather than treated as a hypothetical concern: the network's specific hypothesis-relevant result (the redox-DNA bridge) held up, but the broader hub structure did not (Jaccard overlap 0.34, hub overlap 4/15). This compositional sensitivity check was not re-run on the resistome linkage specifically; whether the Stringent response-ARG association holds equally well under a CLR transform of the module scores is accordingly identified as unresolved and a priority for a future revision, not assumed to hold by extension from the core-network result."),
  P("Third, and specific to the resistome linkage, bulk metagenomic co-abundance could in principle reflect a shared taxonomic driver (a single resistant, stress-tolerant organism, or a small number of organisms, becoming more abundant in some samples and carrying elevated levels of both stringent-response genes and ARGs simply because they carry more of everything) rather than a genuine cross-taxon physiological association. This was tested directly using a taxon-stratified KEGG functional table for the same 18 samples: classified Stringent response module abundance is spread across 418 distinct taxa, no single taxon exceeds 44% of classified abundance in any sample, the identity of the largest contributor differs from sample to sample (10 distinct genera across 18 samples), and recomputing the module score with each sample's own largest contributor removed leaves the ARG-burden correlation essentially unchanged (ρ=0.73 to ρ=0.77). This does not support a single-taxon explanation. It is not, however, a complete resolution: taxonomic resolution in this table is frequently incomplete below genus, 47-76% of module abundance remains in the classifier's unclassified category, and metagenome-assembled-genome-level confirmation, directly linking stringent-response genes and ARGs on the same assembled genome, would still strengthen the causal case further. That step remains a valuable follow-up, but, given the taxonomic dominance check's result, is no longer the single highest-priority unresolved question for this manuscript."),
  P("Fourth, this is a single time-point, cross-sectional design; it cannot distinguish stable functional differences between wastewater types, or a stable resistome-gene-network association, from transient conditions on the sampling date."),
  P("Fifth, an earlier module correlation coefficient and a source-type Kruskal-Wallis result had been computed under an initial KO-to-module mapping and an inconsistent module-score definition. Every statistic and figure reported in this manuscript, including the resistome-linkage analysis, was regenerated from a single corrected mapping and a single scoring definition to avoid propagating that inconsistency."),
];

const d7head = H2("4.2 The resistome linkage is a surveillance signal, not a validated predictive tool");
const d7 = P("The stringent response module result supports treating this module, and by extension the broader stress-physiology network it belongs to, as a resistome-relevant surveillance signal: a module built with no reference to resistance genes at all is nonetheless associated with resistance-gene burden across multiple drug classes in the same samples, a considerably stronger claim than this manuscript could support before the SARG linkage was added. It is not, on its own, a validated predictive tool. The association is correlational and cross-sectional, drawn from 18 samples. A direct test for the most obvious alternative explanation, a shared taxonomic driver, found no support for one: the signal is distributed across hundreds of taxa rather than concentrated in one, and survives removal of each sample's single largest contributor. The claim in this manuscript is accordingly limited to the association itself, reported with its effect sizes, corrected p-values, leave-one-out stability and taxonomic dominance check, without a composite predictive index or risk score built from these data: doing so before independent, out-of-sample replication would overstate what a single-timepoint, n=18 correlational study, from one region, can support, in the same way overstated causal language has been avoided for the redox-DNA bridge elsewhere in this manuscript. Beyond replication in an independent cohort, establishing a mechanistic basis for the association is the necessary next step: confirming that stringent-response genes and resistance genes co-occur on the same assembled genome would rule out the remaining taxonomic ambiguity left by incomplete classification in the present data, and directly testing whether induction of the stringent response increases resistance-gene expression or persister-cell survival would establish causation rather than association. Until that work is done, this signal should be treated as hypothesis-generating for surveillance, not as a validated mechanism.");

// ============================================================
// 5. CONCLUSIONS
// ============================================================
const conclHeading = H1("5. Conclusions");
const concl = [
  P("Redox, DNA-repair and stress-response genes form one integrated, non-random co-occurrence network across 18 wastewater metagenomes, rather than operating as independent functional programmes, and this network is measurably associated with resistance-gene burden in the same samples: the Stringent response (ppGpp) module correlates with total ARG burden and with seven mechanistically distinct resistance-drug classes, a pattern reproduced at the resistance-mechanism level and stable under leave-one-out resampling. This is consistent with the stringent response's established role in antibiotic tolerance and persister-cell formation, and elevates this study's central claim from a structural observation to a resistome-relevant one. A direct test using taxon-stratified functional data found this association is not attributable to a single dominant taxon: classified module abundance is spread across 418 distinct taxa, no single taxon exceeds 44% of classified abundance in any sample, and the correlation survives removal of each sample's own largest contributor (ρ=0.73 to ρ=0.77). Nitric oxide stress genes are the most network-central module per gene but are not the module linked to resistance burden, indicating that network centrality and resistome relevance are distinct properties of this network. The redox-DNA pathway motivating the original study design, Electron carrier balance and Recombination repair, remains significantly co-occurring and robust to a compositional-data sensitivity check, but is a separate result from the resistome linkage, not the same finding under two names. Module abundance differs directionally, but not statistically, by wastewater source type at the current sample size of six per group, while total ARG burden does differ significantly by source type; a bootstrap power analysis indicates that 15-25 samples per group would be needed to resolve the module-level trends. The resistome association reported here remains correlational and cross-sectional; independent, out-of-sample replication, rather than building a predictive index on the present result, is identified as the necessary next step."),
];

console.log("discussion/conclusion ready");

// ============================================================
// 6. DATA AND CODE AVAILABILITY / SUPPLEMENTARY MATERIALS
// ============================================================
const suppHeading = H1("6. Data and code availability");
const suppBody = [
  P("[TO CONFIRM: repository / accession details for raw sequencing reads and the deposition plan for processed tables.] The corrected 903-KO abundance matrix, the frozen KO-to-module map, module-score matrices, the full KO-level and module-level correlation matrices, the network edge lists (primary and CLR-sensitivity), the corrected SARG resistome tables (Type, Subtype, Mechanism group/subgroup, Pathogen, per-gene detail), the taxon-stratified KEGG functional table used for the taxonomic dominance check, the ARG-linkage correlation matrices, and the analysis code used to regenerate every statistic and figure in this manuscript are available as Supplementary Materials and in the project folders 9. step Robustness and Sensitivity Analyses/ (methods, results, tables and code for the robustness analyses in Sections 2.10, 3.5 and 3.6) and 10. Final Manuscript (Network-Resistome Integration)/ (this manuscript's own code, methods, results, tables and all 12 figures, PNG and vector PDF, for Sections 2.8-2.9 and 3.7-3.8 plus the complete figure set)."),
  P("Supplementary Table S1. Full 903-KO module map (KO ID, module, functional group, KEGG pathway).", {spacingAfter:80}),
  P("Supplementary Table S2. Full network edge list, primary (log10(x+1)) and CLR-sensitivity networks (Cytoscape-compatible).", {spacingAfter:80}),
  P("Supplementary Table S3. Full 15×15 module correlation matrix (ρ and BH-FDR q-values).", {spacingAfter:80}),
  P("Supplementary Table S4. Raw and depth-normalised module scores, side by side.", {spacingAfter:80}),
  P("Supplementary Table S5. Threshold-sensitivity edge counts (|ρ| 0.50-0.75) and bootstrap power analysis, full n-per-group grid.", {spacingAfter:80}),
  P("Supplementary Table S6. Full SARG Type x Module and Mechanism-group x Module correlation matrices (300 and 120 tests respectively, all ρ, p and q values, not only the 15/9 pairs surviving correction).", {spacingAfter:80}),
  P("Supplementary Materials S7. Analysis code and intermediate tables (this project's step-by-step working files, including 9. step Robustness and Sensitivity Analyses/code/ and 10. Final Manuscript (Network-Resistome Integration)/code/).", {spacingAfter:80}),
  P("Supplementary Table S8. Stringent response-ARG burden source-type confound check: correlation recomputed within each source type, with hospital samples excluded, and as a partial correlation controlling for source type and for city (Section 3.7; code: 03_source_type_confound_check.py; table: Stringent_ARG_confound_check.csv).", {spacingAfter:80}),
  P("Supplementary Table S9. Full taxonomic dominance check detail underlying Table 8 (Section 3.8): per-sample distinct classified taxon counts, full (non-truncated) top-taxon lineage strings, and the original-vs-taxon-excluded module score comparison (code: 04_taxonomic_dominance_check.py; table: Stringent_module_taxonomic_dominance.csv; source data: data/stringent_stratified_extract.tsv).", {spacingAfter:300}),
];

const disclosureHead = H2("Methods disclosure");
const disclosureBody = P("Preliminary exploration of this dataset used an uncorrected KO-to-module mapping. All results and figures reported in this manuscript use the corrected 903-KO module mapping. Three headline numbers changed materially as a result: the Electron carrier balance and Recombination repair module correlation (originally reported as r=0.87, corrected to ρ=0.63, KO-level edge count corrected from 2,147 to 2,104), the strongest source-type Kruskal-Wallis result (originally reported for Two-component systems at p=0.008 under the uncorrected mapping, not significant under the corrected mapping), and the module edge-count figure (Figure 7), which was regenerated from the corrected map for this draft. This manuscript supersedes an earlier draft that presented the KO co-occurrence network without a resistome linkage; that version is retained in the project files for reference, but this document is the final manuscript.");

// ============================================================
// REFERENCES
// ============================================================
const refHeading = H1("References");
const refNote = P("[Background-literature citations marked CITATION in the Introduction and Discussion, including the stringent-response/antibiotic-tolerance literature underpinning Sections 1 and 4, are placeholders for the author to fill in from the primary literature; none have been fabricated for this draft.] The following software/tool citations are carried over from the project's existing methods notes and should be verified and formatted to the target journal's style before submission:", {spacingAfter:200});
const refList = [
  "Bolger, A.M., Lohse, M., Usadel, B. (2014). Trimmomatic: a flexible trimmer for Illumina sequence data. Bioinformatics.",
  "Langmead, B., Salzberg, S.L. (2012). Fast gapped-read alignment with Bowtie 2. Nature Methods.",
  "Li, D., Liu, C.-M., Luo, R., Sadakane, K., Lam, T.-W. (2015). MEGAHIT: an ultra-fast single-node solution for large and complex metagenomics assembly. Bioinformatics.",
  "Hyatt, D., Chen, G.-L., LoCascio, P.F., Land, M.L., Larimer, F.W., Hauser, L.J. (2010). Prodigal: prokaryotic gene recognition and translation initiation site identification. BMC Bioinformatics.",
  "Fu, L., Niu, B., Zhu, Z., Wu, S., Li, W. (2012). CD-HIT: accelerated for clustering the next-generation sequencing data. Bioinformatics.",
  "Gurevich, A., Saveliev, V., Vyahhi, N., Tesler, G. (2013). QUAST: quality assessment tool for genome assemblies. Bioinformatics.",
  "Patro, R., Duggal, G., Love, M.I., Irizarry, R.A., Kingsford, C. (2017). Salmon provides fast and bias-aware quantification of transcript expression. Nature Methods.",
  "Hagberg, A.A., Schult, D.A., Swart, P.J. (2008). Exploring network structure, dynamics, and function using NetworkX. Proceedings of the 7th Python in Science Conference.",
  "Yin, X., Jiang, X.-T., Chai, B., Li, L., Yang, Y., Cole, J.R., Tiedje, J.M., Zhang, T. (2018). ARGs-OAP v2.0 with an expanded SARG database and Hidden Markov Models for enhancement characterization and quantification of antibiotic resistance genes in environmental metagenomes. Bioinformatics.",
].map(t => new Paragraph({ spacing: { after: 160, line: 276 }, indent: { left: 360, hanging: 360 }, children: [ new TextRun({ text: t, size: 20 }) ] }));

const figLegendsHeading = H1("Figure legends");
const figLegends = [
  P("Figure 1. Module-level KO co-occurrence network: 15 module nodes sized by KO count, edges weighted by within/between-module edge density (colour = sign of mean ρ). Underlying gene-level network: 903 KOs, 53,775 significant edges (|ρ|>0.60, q<0.05, Table 2).", {spacingAfter:200}),
  P("Figure 2. (A) Degree distribution of the 903-KO co-occurrence network (|ρ|>0.60, p<0.05). (B) Edge count as a function of the Spearman |ρ| threshold used to define the network (0.50-0.75 tested); the primary 0.60 threshold is marked.", {spacingAfter:200}),
  P("Figure 3. Module-score correlation matrix (Spearman ρ, n=18 metagenomes), ordered and colour-coded by functional group. * BH-FDR q<0.05, ** q<0.01, *** q<0.001 (105 unique pairs).", {spacingAfter:200}),
  P("Figure 4. Module scores (sum of log10(x+1)-transformed KO abundances) by wastewater source type for all 15 modules, ranked by Kruskal-Wallis p-value, n=6 samples per source type. No module differs significantly after correction for multiple testing (Table 3).", {spacingAfter:200}),
  P("Figure 5. (A) PCA (z-scored Euclidean) and (B) PCoA (Bray-Curtis) ordination of the 18×15 module-score matrix, coloured by wastewater source type, with descriptive 1.5-SD data ellipses. PERMANOVA and ANOSIM statistics annotated; neither ordination shows significant grouping.", {spacingAfter:200}),
  P("Figure 6. Distance to group centroid (z-scored Euclidean, PCoA space) by wastewater source type. Horizontal bars show group means. The formal PERMDISP permutation test found this difference non-significant (F=0.49, p=0.69, 9,999 permutations).", {spacingAfter:200}),
  P("Figure 7. KO-level edge counts between module pairs (|ρ|>0.60, p<0.05, log color scale), recomputed on the corrected module map. Two-component systems dominates by edge count across almost every module pair, consistent with its size (406 of 903 KOs).", {spacingAfter:200}),
  P("Figure 8. (A) Overlap between the primary log10(x+1) network and a CLR-transformed compositional-sensitivity network (both |ρ|>0.60, p<0.05). (B) The Electron carrier balance × Recombination repair bridge is stable across both transforms (97% of edges retained), unlike the network's broader hub structure (4/15 top hubs shared).", {spacingAfter:200}),
  P("Figure 9. Bootstrap-estimated statistical power (1,500 simulations per point) to detect the five strongest observed module-level trends, as a function of samples per wastewater source type. Dashed line: 80% power. Dotted line: current study n=6/group.", {spacingAfter:200}),
  P("Figure 10. Correlation matrix (Spearman ρ) between 21 SARG resistance types and 15 functional modules (300 valid tests). * BH-FDR q<0.05, ** q<0.01, *** q<0.001. ARG types ordered by |ρ| against Stringent response; module x-axis labels coloured by functional group.", {spacingAfter:200}),
  P("Figure 11. Stringent response (ppGpp) module score versus (A) total ARG burden and (B) multidrug-resistance ARG burden specifically, coloured by wastewater source type, n=18. Dashed line is a linear trend for visual reference; statistics are Spearman.", {spacingAfter:200}),
  P("Figure 12. (A) Stringent response module abundance composition per sample: unclassified, single largest classified taxon, and all other classified taxa (417 total), ordered by source type. (B) Module score recomputed with each sample's own top contributing taxon excluded, versus the original score; proximity to the y=x line indicates minimal change. n=18.", {spacingAfter:200}),
];

console.log("supp/ref ready");

// ============================================================
// ASSEMBLE DOCUMENT
// ============================================================
const allChildren = [
  ...titleBlock,
  abstractHeading, ...abstractBody,
  introHeading, ...introBody,
  methodsHeading,
  m21head, ...m21body,
  m22head, ...m22body,
  m23head, ...m23body,
  table1, table1cap,
  m24head, ...m24body,
  m25head, ...m25body,
  m26head, ...m26body,
  m27head, ...m27body,
  m28head, ...m28body,
  m29taxhead, ...m29taxbody,
  m29head, ...m29body,
  m210head, ...m210body,
  resultsHeading,
  r31head, ...r31body,
  table2, table2cap,
  r31bhead, ...r31bbody,
  table5, table5cap,
  table6, table6cap,
  r32head, ...r32body,
  table3, table3cap,
  r33head, ...r33body,
  table4, table4cap,
  r34head, ...r34body,
  r35head, ...r35body,
  r36head, ...r36body,
  r37head, ...r37body,
  table7, table7cap,
  r38head, ...r38body,
  table8, table8cap,
  discHeading,
  d0, d1, d2, d3, d3b, d4, d5,
  d6head, ...d6,
  d7head, d7,
  conclHeading, ...concl,
  suppHeading, ...suppBody,
  disclosureHead, disclosureBody,
  refHeading, refNote, ...refList,
  figLegendsHeading, ...figLegends,
];

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Times New Roman", size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Times New Roman" }, paragraph: { spacing: { before: 360, after: 160 } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, italics: false, font: "Times New Roman" }, paragraph: { spacing: { before: 280, after: 140 } } },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 },
      },
    },
    headers: {
      default: new Header({ children: [ new Paragraph({ children: [] }) ] }),
    },
    footers: {
      default: new Footer({
        children: [ new Paragraph({ children: [] }) ],
      }),
    },
    children: allChildren,
  }],
});

Packer.toBuffer(doc).then(buffer => {
  const out = "/sessions/quirky-amazing-cori/mnt/outputs/manuscript/Project22_FINAL_Manuscript.docx";
  fs.writeFileSync(out, buffer);
  console.log("WROTE", out, buffer.length, "bytes");
}).catch(e => { console.error("PACK ERROR", e); process.exit(1); });

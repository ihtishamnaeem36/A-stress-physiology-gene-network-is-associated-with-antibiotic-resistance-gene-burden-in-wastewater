# Wastewater stress-physiology / resistome network — analysis code

Analysis code for **"A stress-physiology gene co-occurrence network is associated with
antibiotic-resistance-gene burden in urban wastewater metagenomes."**

Eighteen wastewater metagenomes (3 source types x 3 cities x 2 replicates, Khyber Pakhtunkhwa,
Pakistan) were profiled for 903 curated KEGG Orthology (KO) genes across 15 functional modules
in three mechanistic groups (redox stress, DNA damage/fidelity, stress physiology). A KO-level
Spearman co-occurrence network was built and shown to be one connected, non-random structure.
The headline result: the Stringent response (ppGpp) module correlates with antibiotic-
resistance-gene (ARG) burden (SARG database) across multiple drug classes, robust to
resampling, a source-type/city confound check, and a taxonomic-dominance check, though the
association weakens under a compositional-data (CLR) transform.

This repository contains every script used to produce the manuscript's statistics, tables,
figures, and supplementary materials — not just the final numbers.

## Repository layout

```
code/
├── 00_core_network_pipeline/       Module scores, KO-KO Spearman network, FDR correction,
│                                    PCA/PERMANOVA ordination. Run first; everything else
│                                    depends on its outputs.
├── 01_resistome_and_robustness_checks/
│                                    SARG resistome linkage plus every sensitivity/confound/
│                                    taxonomic-dominance check reported in the manuscript.
├── 02_figure_generation/           One script per manuscript figure (fig1.py .. fig12.py),
│                                    matplotlib, sharing a common style module.
├── 03_manuscript_build/            Node.js scripts (using the `docx` package) that assemble
│                                    the manuscript .docx from text and table data directly.
├── _reference_frozen_outputs/      Frozen intermediate CSV/JSON outputs from the core
│                                    pipeline, committed so every reported number can be
│                                    checked without re-running anything.
├── REPRODUCIBILITY_AND_PARAMETERS.txt
│                                    Script-by-script description of every analysis: exact
│                                    statistical parameters, thresholds, FDR procedure,
│                                    permutation counts, random seeds, and known caveats.
│                                    Read this before re-running or extending any analysis.
├── requirements.txt                Python dependencies.
├── LICENSE                         MIT (code only — see note inside the file).
└── CITATION.cff                    Machine-readable citation metadata.
```

Each numbered subfolder's scripts are meant to be run in filename order (`00_...`, `01_...`,
`step2_...`, `step3_...`, etc.) — later scripts consume the outputs of earlier ones. Start with
`REPRODUCIBILITY_AND_PARAMETERS.txt` for the exact run order, inputs, and outputs of every
single script; this README only gives the map.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Figure-generation and manuscript-build steps additionally need:
- Node.js (>=16) and npm, for `03_manuscript_build/` (`cd 03_manuscript_build && npm install`)
- LibreOffice (`soffice`) and Poppler (`pdftoppm`), only if you want to render the built
  `.docx` to PDF/JPEG for visual verification after a rebuild — not required to run the
  analysis itself.

## Data availability

The raw KO abundance matrix (`Step1_Abundance_Matrix.xlsx`) and the SARG resistome annotation
tables that these scripts read are **not included in this repository** — they are the
project's primary research data and are referenced by the manuscript's own Data and code
availability statement (see the main text; a Sequence Read Archive BioProject accession is
given there). Several scripts in `00_core_network_pipeline/` and
`01_resistome_and_robustness_checks/` therefore contain a hardcoded `BASE` path pointing at
this data on the original analysis machine — update that constant to point at your own copy of
the raw data before re-running a script from scratch. The frozen intermediate outputs in
`_reference_frozen_outputs/` let you verify or extend the downstream statistics without needing
the raw data at all.

## Reproducing a specific number, table, or figure

1. Open `REPRODUCIBILITY_AND_PARAMETERS.txt` and find the script listed under the relevant
   pipeline stage (core network stats are in `00_...`, resistome/ARG stats in `01_...`, a given
   figure in `02_figure_generation/figN_*.py`).
2. Check that script's stated inputs — most read directly from `_reference_frozen_outputs/` or
   from another script's output, a few read the raw abundance/SARG data directly (see Data
   availability above).
3. Run it: `python path/to/script.py`. Random seeds are fixed throughout (see
   REPRODUCIBILITY_AND_PARAMETERS.txt, "Global conventions" section) so permutation-based
   results (PERMANOVA, bootstrap power) reproduce exactly.

## Key methodological conventions (see REPRODUCIBILITY_AND_PARAMETERS.txt for full detail)

- Correlation method: Spearman rank correlation throughout, never Pearson on raw values.
- KO-KO network edge threshold: |rho| > 0.60 and p < 0.05, with Benjamini-Hochberg FDR
  correction applied afterward (manual step-up implementation, not a library call — replicate
  it exactly if adding new analyses for consistency).
- Module score definition: sum, across a module's member KOs, of log10(abundance + 1) per KO
  per sample.
- n = 18 samples throughout (3 source types x 3 cities x 2 replicates), except where explicitly
  reduced for a specific sensitivity check (e.g. n = 12 in the non-hospital-only subset).

## Citing this code

See `CITATION.cff`. If you use or adapt this pipeline, please cite the associated manuscript
(full citation to be finalised on acceptance).

## License

MIT for the code in this repository (see `LICENSE`). This does not extend to the manuscript
text, figures, or underlying sequencing data.

# 03 — Manuscript build

Node.js scripts, using the [`docx`](https://www.npmjs.com/package/docx) npm package, that
assemble the manuscript `.docx` files programmatically from text and table data embedded
directly in the script (rather than editing a `.docx` by hand). `docx`-style libraries can only
*create* new files, not open and edit an existing one — so any content change to the manuscript
means editing the relevant string/array literal in `build_final.js` and rebuilding, or editing
the exported `.docx`'s XML directly (unzip -> edit `word/document.xml` -> rezip) if you are
working from the `.docx` alone without this source.

| Script | Produces |
|---|---|
| `build_final.js` | `Project22_FINAL_Manuscript.docx` — the authoritative, submission-track manuscript. Contains Title/Abstract, Introduction, Methods, Results (including every table's raw data), Discussion, Limitations, Conclusions, References, and the consolidated figure-legends section, plus all Word-formatting helpers (three-line table borders, heading styles, italic-taxon-name handling, image embedding, page setup). |
| `build_legends.js` | Standalone script used once to build/verify the consolidated figure-legends section before it was folded into `build_final.js`. Kept for reference. |
| `build_plain_language_summary.js` | `Plain_Language_Summary.docx` — the separate lay-audience summary document. |

## Setup and build

```bash
npm install
node build_final.js
```

Check the output path hardcoded near the bottom of `build_final.js` and update it to point at
your local manuscript folder before running.

## Verifying a rebuild

Don't trust that the script ran without errors — render and look at it:

```bash
soffice --headless --convert-to pdf Project22_FINAL_Manuscript.docx
pdftoppm -jpeg -r 100 Project22_FINAL_Manuscript.pdf page
```

Then inspect the resulting `page-NN.jpg` files, particularly any page you just changed.

## Formatting conventions this script enforces

No em/en dashes, no AI-vocabulary filler words, three-line (booktabs) tables only, Times New
Roman throughout, no page numbers/running header, genus/species names italicised, figure
legends consolidated after the references (not embedded per-figure). Full list: see
`../REPRODUCIBILITY_AND_PARAMETERS.txt`, section "03_manuscript_build", and the project's
`PROJECT_STATUS_AND_HANDOFF.txt` (one level up) for the complete style-convention rationale.

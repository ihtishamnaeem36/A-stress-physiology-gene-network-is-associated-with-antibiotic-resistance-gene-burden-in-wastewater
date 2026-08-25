# Turning this folder into a live GitHub repository

The analysis code in this folder is fully organised and ready to push (README, per-folder
READMEs, LICENSE, CITATION.cff, requirements.txt, .gitignore, and REPRODUCIBILITY_AND_
PARAMETERS.txt are all in place). One initial commit was already made and packaged into
`project22_code.bundle` in this same folder, but it could not be written directly onto this
network-mounted drive as a live `.git` repository — this drive doesn't support the file
operations git needs (you may see a broken, unusable `.git` folder left behind here; see
step 1 below). Do the following on your own machine instead, where this is a non-issue.

## Step 1 — clean start

1. Copy this whole `code` folder to a normal local folder on your computer (not the mounted/
   synced drive) — e.g. `Documents\project22_code`.
2. In that local copy, delete the `.git` folder if one was copied over (right-click -> Delete,
   or `rmdir /s .git` on Windows / `rm -rf .git` on Mac/Linux). It's broken and safe to remove.
   Do **not** delete `project22_code.bundle`, `.gitignore`, `LICENSE`, `CITATION.cff`,
   `README.md`, `requirements.txt`, or `REPRODUCIBILITY_AND_PARAMETERS.txt` — those are the
   real deliverables.

## Step 2 — recreate the repository with its commit history intact

From inside your local copy of the folder:

```bash
git clone project22_code.bundle .temp_clone
```

This unpacks the one commit that's already made (with a proper message describing the full
pipeline) into `.temp_clone/.git`. Then:

```bash
mv .temp_clone/.git .
rm -rf .temp_clone
git status
```

`git status` should now show a clean working tree (no changes), because the bundle already
contains exactly the files sitting in this folder. `git log` will show the one initial commit.

If you'd rather skip preserving that commit and just start fresh, that's fine too — delete
`project22_code.bundle`, run `git init`, `git add -A`, `git commit -m "Initial commit"` instead
and skip the bundle entirely.

## Step 3 — create the GitHub repository and push

1. On github.com, create a new **empty** repository (no README/license/gitignore — you already
   have those). Suggested name: `wastewater-stress-resistome-network` or similar.
2. Back in your local folder:

```bash
git remote add origin https://github.com/<your-username>/<repo-name>.git
git branch -M main
git push -u origin main
```

## Step 4 — a few finishing touches worth doing before/after the first push

- Open `CITATION.cff` and replace `REPLACE_WITH_GITHUB_URL_ONCE_PUSHED` with the real repo URL.
- Update `01_resistome_and_robustness_checks/*.py` and `00_core_network_pipeline/*.py`'s
  hardcoded `BASE` path constants if you want the scripts to run as-is for someone who clones
  the repo — right now they point at your original analysis machine's folder layout. The
  README already documents this (see "Data availability").
- Consider adding a short repo description and topics on GitHub (e.g. `metagenomics`,
  `wastewater`, `antimicrobial-resistance`, `bioinformatics`, `network-analysis`) so it's
  discoverable.
- If you want a DOI for the code (common for a methods-heavy manuscript), connect the
  repository to Zenodo (GitHub Settings -> Integrations, or zenodo.org -> GitHub) and cut a
  release (e.g. `v1.0.0`) once the repository is pushed — the manuscript's Data and code
  availability section can then cite that DOI directly instead of just the GitHub URL.
- The raw abundance matrix and SARG tables are intentionally not in this repository (see
  README, "Data availability") — decide where those will be deposited (the manuscript
  currently points to an SRA BioProject for the raw reads) and make sure the README's
  Data availability section stays consistent with whatever you finalise there.

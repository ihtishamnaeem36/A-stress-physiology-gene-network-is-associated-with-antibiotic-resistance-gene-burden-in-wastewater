"""
SARG (Structured Antibiotic Resistance Genes) data loader for Project 2.2.

Sample-naming fix (applied automatically, every load):
  - The SARG pipeline mislabelled the sample "SCW2" as "SSLW3". Any column
    named SSLW3 in raw SARG output is therefore renamed to SCW2.
  - "MHW3" in the raw SARG output is an extra sample with no counterpart in
    the KO abundance matrix and is dropped.
  - After these two fixes, the SARG sample set is identical (same 18 codes)
    to the KO/module abundance matrix used throughout the rest of the project.
Confirmed with the project owner (2026-07-19); do not re-ask, just apply.
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))  # .../project 2.2
BASE = os.path.join(PROJECT_ROOT, "DATA used",
                     "data SARG (resistance gene) (best for wasterwter metagenomic",
                     "MAM_asem_anno22fHiA9hpGDXDXTLWiNAPm_result")

SAMPLE_RENAME = {"SSLW3": "SCW2"}
SAMPLE_DROP = ["MHW3"]

EXPECTED_18 = ['MCW1','MCW2','MHW1','MHW2','MSLW1','MSLW2','PCW1','PCW2',
               'PHW1','PHW2','PSLW1','PSLW2','SCW1','SCW2','SHW1','SHW2',
               'SSLW1','SSLW2']

def _fix_samples(df, sample_cols):
    df = df.rename(columns=SAMPLE_RENAME)
    drop_present = [c for c in SAMPLE_DROP if c in df.columns]
    if drop_present:
        df = df.drop(columns=drop_present)
    new_cols = [SAMPLE_RENAME.get(c, c) for c in sample_cols if c not in SAMPLE_DROP]
    assert sorted(new_cols) == sorted(EXPECTED_18), f"sample mismatch after fix: {sorted(new_cols)}"
    return df, new_cols

def load_sarg_table(filename, sample_row_offset_cols=1, extra_trailing_cols=None):
    """Generic loader for the tab-separated SARG summary tables (Type, Subtype,
    Mechanism.group, Mechanism.subgroup, Mechanism.subgroup2, Pathogen).
    First column is the category name, remaining columns (until any trailing
    metadata columns) are per-sample relative abundance."""
    df = pd.read_csv(f"{BASE}/{filename}", sep="\t")
    id_col = df.columns[0]
    trailing = extra_trailing_cols or []
    sample_cols = [c for c in df.columns[1:] if c not in trailing]
    df, sample_cols = _fix_samples(df, sample_cols)
    return df, id_col, sample_cols

def load_all_sarg():
    type_df, type_id, type_samples = load_sarg_table("All.SARG.Type.txt")
    subtype_df, subtype_id, subtype_samples = load_sarg_table("All.SARG.Subtype.txt")
    mech_group_df, mg_id, mg_samples = load_sarg_table("All.SARG.Mechanism.group.txt")
    mech_subgroup_df, msg_id, msg_samples = load_sarg_table("All.SARG.Mechanism.subgroup.txt")
    pathogen_df, path_id, path_samples = load_sarg_table("All.SARG.Pathogen.txt")
    detail_df, detail_id, detail_samples = load_sarg_table(
        "All.SARG.detail.txt",
        extra_trailing_cols=["Type","Subtype","HMM category","Mechanism group",
                              "Mechanism subgroup","Mechanism subgroup2","Pathogen"]
    )
    return {
        "type": (type_df, type_id, type_samples),
        "subtype": (subtype_df, subtype_id, subtype_samples),
        "mechanism_group": (mech_group_df, mg_id, mg_samples),
        "mechanism_subgroup": (mech_subgroup_df, msg_id, msg_samples),
        "pathogen": (pathogen_df, path_id, path_samples),
        "detail": (detail_df, detail_id, detail_samples),
    }

if __name__ == "__main__":
    tabs = load_all_sarg()
    for name, (df, idcol, samples) in tabs.items():
        print(f"{name}: {df.shape[0]} rows, {len(samples)} samples, id_col={idcol}")
        print("  samples:", sorted(samples))

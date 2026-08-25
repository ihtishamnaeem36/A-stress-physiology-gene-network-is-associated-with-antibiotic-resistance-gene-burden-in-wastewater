"""
data_prep.py -- shared KO abundance / module-score loader for Project 2.2.

Reconstructed (2026-08-22) to make the resistome-linkage analysis scripts in
this folder runnable again: they originally imported this module from a
temporary session path (/sessions/.../outputs/figscript/data_prep.py) that
was never saved into the project and no longer exists. This version lives
in the same code/ folder as the scripts that import it and uses only
paths relative to the project root, so the whole pipeline can be re-run
from a fresh checkout.

load_all() returns exactly what arg_network_link.py, 02_arg_source_type_and_envfit.py
and 03_source_type_confound_check.py expect:
    data        - merged 903-KO abundance + module-map DataFrame
    ko_ids      - list of 903 KO_ID strings, row order matching X
    X           - 903 x 18 ndarray, log10(x+1)-transformed abundance
                  (the primary module-score definition, Section 2.4)
    sample_cols - list of 18 sample codes, column order matching X
    module_of   - dict KO_ID -> Module_name (15 modules, frozen map)
    group_of    - dict KO_ID -> Functional_group (A/B/C)
    meta        - DataFrame with columns sample, environment, city
"""
import os
import pandas as pd
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))  # .../project 2.2


def env_of(s):
    if 'HW' in s:
        return 'Hospital'
    if 'CW' in s:
        return 'Community'
    return 'Slaughterhouse'


def city_of(s):
    return {'M': 'Mardan', 'P': 'Peshawar', 'S': 'Swat'}[s[0]]


def load_all():
    abund = pd.read_excel(
        os.path.join(PROJECT_ROOT, "1.step  Target module selection and k number recovery",
                     "step1 figures table", "Step1_Abundance_Matrix.xlsx"),
        sheet_name="Full_Abundance_Matrix")
    abund = abund.rename(columns={'# Gene Family': 'KO_ID'}).drop(columns=['Module'])
    sample_cols = [c for c in abund.columns if c != 'KO_ID']

    freeze = pd.read_csv(os.path.join(PROJECT_ROOT, "BG", "Project22_903KO_Module_Map.csv"))[
        ['KO_ID', 'Module_name', 'Functional_group']]
    data = abund.merge(freeze, on='KO_ID', how='inner')
    assert data.shape[0] == 903, f"expected 903 target KOs, got {data.shape[0]}"

    ko_ids = data['KO_ID'].tolist()
    X_raw = data[sample_cols].astype(float).values
    X = np.log10(X_raw + 1)   # primary sum-of-log10(x+1) module-score definition (Section 2.4)

    module_of = dict(zip(data['KO_ID'], data['Module_name']))
    group_of = dict(zip(data['KO_ID'], data['Functional_group']))

    meta = pd.DataFrame({'sample': sample_cols})
    meta['environment'] = meta['sample'].map(env_of)
    meta['city'] = meta['sample'].map(city_of)

    return data, ko_ids, X, sample_cols, module_of, group_of, meta


if __name__ == "__main__":
    data, ko_ids, X, sample_cols, module_of, group_of, meta = load_all()
    print(f"{len(ko_ids)} KOs x {len(sample_cols)} samples, {len(set(module_of.values()))} modules")
    print(meta)

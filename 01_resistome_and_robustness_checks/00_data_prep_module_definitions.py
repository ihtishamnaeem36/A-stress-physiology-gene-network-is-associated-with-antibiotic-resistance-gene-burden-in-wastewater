import pandas as pd, numpy as np
from scipy.stats import rankdata, t as tdist

BASE = "/sessions/quirky-amazing-cori/mnt/project 2.2"

def load_all():
    abund = pd.read_excel(f"{BASE}/1.step  Target module selection and k number recovery/step1 figures table/Step1_Abundance_Matrix.xlsx",
                           sheet_name="Full_Abundance_Matrix")
    abund = abund.rename(columns={'# Gene Family':'KO_ID'}).drop(columns=['Module'])
    sample_cols = [c for c in abund.columns if c != 'KO_ID']
    freeze = pd.read_csv(f"{BASE}/BG/Project22_903KO_Module_Map.csv")[['KO_ID','Module_name','Functional_group']]
    data = abund.merge(freeze, on='KO_ID', how='inner')
    ko_ids = data['KO_ID'].tolist()
    X = np.log10(data[sample_cols].astype(float).values + 1)
    module_of = dict(zip(data['KO_ID'], data['Module_name']))
    group_of  = dict(zip(data['KO_ID'], data['Functional_group']))

    def env_of(s):
        if 'HW' in s: return 'Hospital'
        if 'CW' in s: return 'Community'
        return 'Slaughterhouse'
    def city_of(s):
        return {'M':'Mardan','P':'Peshawar','S':'Swat'}[s[0]]
    meta = pd.DataFrame({'sample': sample_cols})
    meta['environment'] = meta['sample'].map(env_of)
    meta['city'] = meta['sample'].map(city_of)

    return data, ko_ids, X, sample_cols, module_of, group_of, meta

def ko_network(X, thresh_r=0.60, alpha=0.05):
    n_ko, n = X.shape
    R = np.apply_along_axis(rankdata, 1, X)
    corr = np.corrcoef(R)
    with np.errstate(divide='ignore', invalid='ignore'):
        tstat = corr * np.sqrt((n-2) / (1 - corr**2))
    pmat = 2 * tdist.sf(np.abs(tstat), df=n-2)
    iu = np.triu_indices(n_ko, k=1)
    r_vals = corr[iu]; p_vals = pmat[iu]
    valid = ~np.isnan(p_vals)
    edge_mask = valid & (np.abs(r_vals) > thresh_r) & (p_vals < alpha)
    return corr, pmat, iu, r_vals, p_vals, edge_mask, valid

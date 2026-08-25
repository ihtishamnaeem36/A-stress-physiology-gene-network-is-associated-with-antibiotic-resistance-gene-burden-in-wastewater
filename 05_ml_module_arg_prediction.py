"""
05_ml_module_arg_prediction.py

Purpose
-------
Tests whether the 15 module scores jointly predict total ARG burden, as a
multivariate complement to the univariate module-by-module correlations
already reported (ARG_total_burden_vs_modules.csv, Section 3.8 originally
"3.7" of the manuscript). Reported in Section 3.7 ("A multivariate model
links module abundance to ARG burden").

Feature matrix
--------------
module_scores_sumlog_frozen.csv (18 samples x 15 modules), the same
per-sample module-score matrix underlying the manuscript's primary
sum-of-log10(x+1) analysis throughout. Verified before use by reproducing
the already-reported Stringent response (ppGpp) rho = 0.7255 against total
ARG burden exactly (see sanity check printed at runtime).

Note: an earlier table in this project, module_scores_CLR_vs_ARG_burden.csv,
could not be reproduced from any script or frozen matrix available in this
repository (neither the sumlog nor a module-level CLR transform of the
meanraw matrix reproduces its reported rho values). It was therefore not
used as the feature source here; the CLR-transform robustness check that IS
reproducible and used elsewhere in this manuscript (Section 3.10 / 09_...
CLR sensitivity script) is a separate, correctly-traced analysis.

Why leave-one-out cross-validation, not a train/test split
------------------------------------------------------------
n=18. A held-out test split would leave single-digit samples per side.
All performance estimates below use leave-one-out cross-validation (LOOCV),
with feature scaling and hyperparameter selection refit inside each
training fold only (nested CV) to avoid leakage.

Methods run
-----------
1. Elastic Net regression, nested LOOCV (outer: 18 leave-one-out folds;
   inner: 5-fold CV to select alpha and l1_ratio on the training fold only).
   Reports R2, RMSE and Spearman(predicted, observed) on the pooled
   out-of-fold predictions, plus the full-data model's standardized
   coefficients for interpretation.
2. Bootstrap stability selection (B=500 resamples of the 18 samples,
   Elastic Net refit on each resample): reports the fraction of resamples
   in which each module's coefficient was non-zero. Standard practice for
   defensible feature selection at small n.
3. Random Forest regression, same nested-LOOCV evaluation, reported
   transparently including its negative result (does not generalise at
   this sample size), plus permutation importance from a full-data fit for
   reference only (not a second confirmatory model).

Deep parameters (grids, seeds, iteration counts) are documented in
Supplementary Methods; this script is the single source of truth for the
exact values used.

Requirements: pandas, numpy, scikit-learn>=1.3, scipy
"""

import warnings
warnings.filterwarnings('ignore')

import json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import ElasticNetCV
from sklearn.model_selection import KFold, LeaveOneOut
from sklearn.preprocessing import StandardScaler

# ----------------------------------------------------------------------
# Fixed parameters (see Supplementary Methods for rationale)
# ----------------------------------------------------------------------
RANDOM_SEED = 2026
L1_RATIOS = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
N_ALPHAS = 40
INNER_CV_FOLDS = 5
N_BOOTSTRAPS = 500
RF_N_ESTIMATORS_LOOCV = 1000
RF_N_ESTIMATORS_FULL = 2000
RF_MIN_SAMPLES_LEAF = 2
RF_PERMUTATION_REPEATS = 200

FEATURES_PATH = '_reference_frozen_outputs/module_scores_sumlog_frozen.csv'
TARGET_PATH = '../tables/ARG_total_burden_per_sample.csv'
OUT_DIR = '../results'
TABLE_OUT = '../tables/ML_module_summary_table.csv'


def main():
    np.random.seed(RANDOM_SEED)

    X_full = pd.read_csv(FEATURES_PATH, index_col=0)
    y_full = pd.read_csv(TARGET_PATH, index_col=0).iloc[:, 0]
    common = X_full.index.intersection(y_full.index)
    assert len(common) == 18, f'expected 18 samples, got {len(common)}'
    X = X_full.loc[common].copy()
    y = y_full.loc[common].copy()
    modules = X.columns.tolist()
    n, p = X.shape
    print(f'n={n} samples, p={p} module features')

    r_check, _ = spearmanr(X['Stringent response (ppGpp)'], y)
    print('sanity check, Stringent response rho vs ARG burden (expect ~0.7255):', round(r_check, 4))
    assert abs(r_check - 0.7255) < 0.001, 'feature matrix does not match the reported manuscript value'

    # -------------------- 1. Elastic Net, nested LOOCV --------------------
    loo = LeaveOneOut()
    en_preds = np.zeros(n)
    for tr_idx, te_idx in loo.split(X):
        Xtr, Xte = X.iloc[tr_idx].values, X.iloc[te_idx].values
        ytr = y.iloc[tr_idx].values
        scaler = StandardScaler().fit(Xtr)
        Xtr_s, Xte_s = scaler.transform(Xtr), scaler.transform(Xte)
        inner_cv = KFold(n_splits=INNER_CV_FOLDS, shuffle=True, random_state=0)
        model = ElasticNetCV(l1_ratio=L1_RATIOS, cv=inner_cv, max_iter=20000, random_state=0)
        model.fit(Xtr_s, ytr)
        en_preds[te_idx] = model.predict(Xte_s)

    en_r2 = 1 - np.sum((y.values - en_preds) ** 2) / np.sum((y.values - y.values.mean()) ** 2)
    en_rmse = np.sqrt(np.mean((y.values - en_preds) ** 2))
    en_rho, en_rho_p = spearmanr(y.values, en_preds)
    print(f'\nElasticNet (nested LOOCV): R2={en_r2:.3f}  RMSE={en_rmse:.3f}  '
          f'Spearman(pred,obs) rho={en_rho:.3f} p={en_rho_p:.4f}')

    scaler_full = StandardScaler().fit(X.values)
    X_full_s = scaler_full.transform(X.values)
    inner_cv_full = KFold(n_splits=INNER_CV_FOLDS, shuffle=True, random_state=0)
    en_full = ElasticNetCV(l1_ratio=L1_RATIOS, cv=inner_cv_full, max_iter=20000, random_state=0)
    en_full.fit(X_full_s, y.values)
    coefs = pd.Series(en_full.coef_, index=modules).sort_values(key=np.abs, ascending=False)
    print(f'\nElasticNet full-data coefficients (standardized units), '
          f'alpha={en_full.alpha_:.4f} l1_ratio={en_full.l1_ratio_:.2f}:')
    print(coefs.to_string())

    # -------------------- 2. Bootstrap stability selection --------------------
    selected = pd.DataFrame(0, index=range(N_BOOTSTRAPS), columns=modules)
    coef_signs = pd.DataFrame(0.0, index=range(N_BOOTSTRAPS), columns=modules)
    rng = np.random.default_rng(RANDOM_SEED)

    for b in range(N_BOOTSTRAPS):
        idx = rng.integers(0, n, size=n)
        Xb, yb = X.values[idx], y.values[idx]
        scaler_b = StandardScaler().fit(Xb)
        Xb_s = scaler_b.transform(Xb)
        try:
            m = ElasticNetCV(l1_ratio=L1_RATIOS, cv=INNER_CV_FOLDS, n_alphas=N_ALPHAS,
                              max_iter=3000, random_state=b)
            m.fit(Xb_s, yb)
            selected.iloc[b] = (np.abs(m.coef_) > 1e-8).astype(int)
            coef_signs.iloc[b] = m.coef_
        except Exception:
            continue

    stability = selected.mean(axis=0).sort_values(ascending=False)
    mean_coef_when_selected = (coef_signs.where(selected == 1)).mean(axis=0)
    print(f'\nBootstrap stability selection (fraction of {N_BOOTSTRAPS} resamples with nonzero coefficient):')
    print(stability.to_string())

    # -------------------- 3. Random Forest: LOOCV + permutation importance --------------------
    rf_preds = np.zeros(n)
    for tr_idx, te_idx in loo.split(X):
        Xtr, Xte = X.iloc[tr_idx].values, X.iloc[te_idx].values
        ytr = y.iloc[tr_idx].values
        rf = RandomForestRegressor(n_estimators=RF_N_ESTIMATORS_LOOCV, random_state=0,
                                    min_samples_leaf=RF_MIN_SAMPLES_LEAF)
        rf.fit(Xtr, ytr)
        rf_preds[te_idx] = rf.predict(Xte)

    rf_r2 = 1 - np.sum((y.values - rf_preds) ** 2) / np.sum((y.values - y.values.mean()) ** 2)
    rf_rmse = np.sqrt(np.mean((y.values - rf_preds) ** 2))
    rf_rho, rf_rho_p = spearmanr(y.values, rf_preds)
    print(f'\nRandom Forest (LOOCV): R2={rf_r2:.3f}  RMSE={rf_rmse:.3f}  '
          f'Spearman(pred,obs) rho={rf_rho:.3f} p={rf_rho_p:.4f}  '
          f'(reported for transparency; does not generalise at this n)')

    rf_full = RandomForestRegressor(n_estimators=RF_N_ESTIMATORS_FULL, random_state=0,
                                     min_samples_leaf=RF_MIN_SAMPLES_LEAF)
    rf_full.fit(X.values, y.values)
    perm = permutation_importance(rf_full, X.values, y.values,
                                   n_repeats=RF_PERMUTATION_REPEATS, random_state=0)
    rf_importance = pd.Series(perm.importances_mean, index=modules).sort_values(ascending=False)
    print('\nRandom Forest permutation importance (training-set, full model, reference only):')
    print(rf_importance.to_string())

    # -------------------- save --------------------
    results = {
        'n_samples': int(n), 'n_features': int(p),
        'feature_matrix': 'module_scores_sumlog_frozen.csv (validated against reported '
                           'Stringent response rho=0.7255)',
        'elasticnet_nested_loocv': {'R2': float(en_r2), 'RMSE': float(en_rmse),
                                     'spearman_rho_pred_vs_obs': float(en_rho), 'p': float(en_rho_p)},
        'elasticnet_full_fit': {'alpha': float(en_full.alpha_), 'l1_ratio': float(en_full.l1_ratio_),
                                 'coefficients_standardized': coefs.to_dict()},
        'bootstrap_stability_selection': {'n_bootstraps': N_BOOTSTRAPS,
                                           'selection_frequency': stability.to_dict(),
                                           'mean_coef_when_selected': mean_coef_when_selected.dropna().to_dict()},
        'random_forest_loocv': {'R2': float(rf_r2), 'RMSE': float(rf_rmse),
                                 'spearman_rho_pred_vs_obs': float(rf_rho), 'p': float(rf_rho_p)},
        'random_forest_permutation_importance': rf_importance.to_dict(),
        'parameters': {
            'random_seed': RANDOM_SEED, 'l1_ratios': L1_RATIOS, 'n_alphas_bootstrap': N_ALPHAS,
            'inner_cv_folds': INNER_CV_FOLDS, 'n_bootstraps': N_BOOTSTRAPS,
            'rf_n_estimators_loocv': RF_N_ESTIMATORS_LOOCV, 'rf_n_estimators_full': RF_N_ESTIMATORS_FULL,
            'rf_min_samples_leaf': RF_MIN_SAMPLES_LEAF, 'rf_permutation_repeats': RF_PERMUTATION_REPEATS,
        },
    }
    with open(f'{OUT_DIR}/ml_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    summary_table = pd.DataFrame({
        'univariate_spearman_rho': [spearmanr(X[m], y)[0] for m in modules],
        'elasticnet_coef_std': coefs.reindex(modules),
        'bootstrap_selection_freq': stability.reindex(modules),
        'rf_permutation_importance': rf_importance.reindex(modules),
    }, index=modules).sort_values('bootstrap_selection_freq', ascending=False)
    summary_table.to_csv(TABLE_OUT)
    print('\nsaved ml_results.json and ML_module_summary_table.csv')
    print(summary_table.round(4).to_string())


if __name__ == '__main__':
    main()

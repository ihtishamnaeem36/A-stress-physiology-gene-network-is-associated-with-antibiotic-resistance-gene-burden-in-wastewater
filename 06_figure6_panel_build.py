"""
06_figure6_panel_build.py

Purpose
-------
Builds Figure 6 (two panels, true vector output, no embedded raster images):
  Panel A: bootstrap statistical power for the five strongest (non-significant)
           module-level source-type trends (Section 3.6), redrawn from
           bootstrap_power_analysis.csv for a clean vector figure consistent
           with Panel B rather than embedding the earlier standalone PNG/PDF.
  Panel B: Elastic Net bootstrap stability selection for predicting total ARG
           burden (Section 3.7), from 05_ml_module_arg_prediction.py's output
           (ML_module_summary_table.csv).

Run 05_ml_module_arg_prediction.py first to produce ML_module_summary_table.csv.

Requirements: pandas, matplotlib
"""

import json
import pandas as pd
import matplotlib.pyplot as plt

MODULE_COLORS_PATH = '../figures/module_colors.json'
POWER_TABLE_PATH = '../../9. step Robustness and Sensitivity Analyses/tables/bootstrap_power_analysis.csv'
ML_TABLE_PATH = '../tables/ML_module_summary_table.csv'
OUT_PDF = '../figures/Figure9_Bootstrap_Power_Analysis.pdf'
OUT_PNG = '../figures/Figure9_Bootstrap_Power_Analysis.png'

# fixed 5-module colour key used in the original bootstrap-power figure
POWER_LINE_COLORS = {
    'Stringent response (ppGpp)': '#1f77b4',
    'Glutathione metabolism': '#d95f02',
    'Two-component systems': '#1b9e77',
    'Peptidoglycan remodeling': '#e377c2',
    'Catalase/Peroxidase': '#888888',
}


def main():
    with open(MODULE_COLORS_PATH) as f:
        module_colors = json.load(f)['colors']

    power = pd.read_csv(POWER_TABLE_PATH, index_col=0)
    ml_tab = pd.read_csv(ML_TABLE_PATH, index_col=0)
    ml_tab = ml_tab.sort_values('bootstrap_selection_freq', ascending=True)

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(13, 5.2))

    # Panel A
    for col in power.columns:
        axA.plot(power.index, power[col], marker='o', linewidth=2, markersize=5,
                 color=POWER_LINE_COLORS.get(col, '#333333'), label=col)
    axA.axhline(0.8, color='black', linestyle='--', linewidth=1.3, label='80% power')
    axA.axvline(6, color='#888888', linestyle=':', linewidth=1.3)
    axA.text(6.3, 0.05, 'current\nn=6/group', fontsize=8.5, color='#666666')
    axA.set_xlabel('Samples per wastewater source type')
    axA.set_ylabel('Empirical statistical power\n(bootstrap Kruskal-Wallis, 1,500 sims)')
    axA.set_ylim(0, 1.05)
    axA.spines['top'].set_visible(False)
    axA.spines['right'].set_visible(False)
    axA.legend(fontsize=8, loc='lower right', frameon=False)
    axA.text(-0.14, 1.04, 'A', transform=axA.transAxes, fontsize=18, fontweight='bold')
    axA.set_title('Bootstrap power for the five strongest\n(non-significant) module-level trends',
                   fontsize=10.5, loc='left')

    # Panel B
    colors = [module_colors.get(m, '#999999') for m in ml_tab.index]
    axB.barh(ml_tab.index, ml_tab['bootstrap_selection_freq'] * 100, color=colors,
             edgecolor='white', height=0.72)
    axB.axvline(50, color='#888888', linestyle='--', linewidth=1)
    axB.text(50.5, -0.7, '50% (reference line only, not a permutation-derived null)',
             fontsize=6.8, color='#666666', va='top')
    for y, (name, row) in enumerate(ml_tab.iterrows()):
        axB.text(row['bootstrap_selection_freq'] * 100 + 1.5, y,
                  f"{row['bootstrap_selection_freq']*100:.0f}%", va='center', fontsize=7.8, color='#333333')
    axB.set_xlabel('Bootstrap selection frequency (%)\n'
                    'Elastic Net, 500 resamples, predicting total ARG burden')
    axB.set_xlim(0, 112)
    axB.spines['top'].set_visible(False)
    axB.spines['right'].set_visible(False)
    axB.tick_params(axis='y', labelsize=9)
    axB.text(-0.30, 1.04, 'B', transform=axB.transAxes, fontsize=18, fontweight='bold')
    axB.set_title('Module stability selection for\npredicting total ARG burden', fontsize=10.5, loc='left')

    plt.tight_layout(w_pad=3)
    plt.savefig(OUT_PDF, bbox_inches='tight', facecolor='white')
    plt.savefig(OUT_PNG, dpi=300, bbox_inches='tight', facecolor='white')
    print('saved', OUT_PDF, 'and', OUT_PNG)


if __name__ == '__main__':
    main()

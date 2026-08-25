import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#333333",
    "axes.linewidth": 0.8,
    "grid.color": "#DDDDDD",
    "grid.linewidth": 0.5,
    "savefig.dpi": 600,
    "figure.dpi": 150,
})

# Okabe-Ito colorblind-safe palette
GROUP_COLORS = {"A-Redox": "#D55E00", "B-DNA": "#0072B2", "C-Stress": "#009E73"}
GROUP_LABELS = {"A-Redox": "Group A: Redox stress", "B-DNA": "Group B: DNA damage/fidelity", "C-Stress": "Group C: Stress physiology"}
ENV_COLORS = {"Hospital": "#CC79A7", "Community": "#0072B2", "Slaughterhouse": "#E69F00"}
ENV_ORDER = ["Hospital", "Community", "Slaughterhouse"]
GROUP_ORDER = ["A-Redox", "B-DNA", "C-Stress"]

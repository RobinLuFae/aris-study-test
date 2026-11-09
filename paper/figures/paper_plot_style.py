"""Shared print style and JSON sources; no model inference."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
matplotlib.rcParams.update({
    'font.family': 'serif', 'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 9, 'axes.labelsize': 9, 'legend.fontsize': 8,
    'xtick.labelsize': 8, 'ytick.labelsize': 8,
    'axes.spines.top': False, 'axes.spines.right': False,
    'pdf.fonttype': 42, 'ps.fonttype': 42,
    'savefig.bbox': 'tight', 'savefig.pad_inches': .035,
})

def read(name):
    return json.loads((ROOT/'results'/name).read_text(encoding='utf-8-sig'))

def save(fig, name):
    fig.savefig(OUT/f'{name}.pdf')
    fig.savefig(OUT/f'{name}.png', dpi=220)
    plt.close(fig)


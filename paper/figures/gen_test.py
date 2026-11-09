"""Frozen P004 paired losses in millidecibels; descriptive intervals."""
from paper_plot_style import *
import numpy as np

data = read('P004_R003_analysis.json')
cells = data['cells']
fig, ax = plt.subplots(figsize=(3.3, 2.2), layout='constrained')
for off, label, color, marker in [(False,'Table knot','#555555','s'),
                                  (True,'Interpolation','#0072B2','o')]:
    rows = [c for c in cells if (not float(c['snr_db']).is_integer())==off]
    x = np.array([c['snr_db'] for c in rows])
    y = np.array([c['loss_db'] for c in rows])*1000
    ci = np.array([c['pointwise_descriptive_95_percentile_interval_db'] for c in rows])*1000
    ax.errorbar(x,y,yerr=np.array([y-ci[:,0],ci[:,1]-y]),fmt=marker,
                color=color,capsize=2,markersize=4,linewidth=1,label=label)
ax.axhline(0,color='0.4',linewidth=.6)
ax.set(xlabel='Channel SNR (dB)',ylabel='PSNR loss (millidecibels)',xticks=[1,4,7,10,13])
ax.legend(frameon=False,loc='upper right')
save(fig,'frozen_test')


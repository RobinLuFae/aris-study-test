"""P002 dense validation, both variants on identical conditions."""
from paper_plot_style import *

data = read('P002_R003_summary.json')
fig, ax = plt.subplots(figsize=(3.3, 2.2), layout='constrained')
for name, label, color, marker in [('linear5','5 knots','#D55E00','s'),
                                  ('linear13','13 knots','#0072B2','o')]:
    v = next(v for v in data['variants'] if v['variant']==name)
    cells = v['cells']
    ax.plot([c['snr_db'] for c in cells], [c['loss_vs_original_db'] for c in cells],
            label=label, color=color, linewidth=1.0)
    # Marker semantics refer to each method's own knots, not its training SNRs.
    off = [c for c in cells if not c['is_table_knot']]
    ax.scatter([c['snr_db'] for c in off], [c['loss_vs_original_db'] for c in off],
               s=13, marker=marker, color=color, facecolors='none', linewidths=.7)
ax.axhline(0, color='0.4', linewidth=.6)
ax.set(xlabel='Channel SNR (dB)', ylabel='PSNR loss (dB)', xticks=[1,4,7,10,13])
ax.legend(frameon=False, loc='upper right')
save(fig, 'dense_validation')


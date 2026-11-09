"""Write exact-source LaTeX tables and an evidence manifest."""
from paper_plot_style import *

pre = read('P002_gate_tables_R003_preparation.json')
pilot = read('P001_pilot_summary_v2.json')
test = read('P004_R003_analysis.json')
lookup = {v['variant']:v for v in pre['variants']}
lines = [r'\begin{tabular}{lrr}',r'\toprule',r'Deployment & Parameters & File bytes \\',r'\midrule']
for key,label in [('original','Original'),('linear5','Linear, 5 knots'),('linear13','Linear, 13 knots')]:
    v=lookup[key]
    lines.append(f'{label} & {v["parameter_count"]:,} & {v["serialized_bytes"]:,} '+r'\\')
lines += [r'\bottomrule',r'\end{tabular}']
(OUT/'table_storage.tex').write_text('\n'.join(lines)+'\n',encoding='utf-8')
lines=[r'\begin{tabular}{lrr}',r'\toprule',r'Method & File bytes & Max. loss (dB) \\',r'\midrule']
labels={'original':'Original','shared_snr':'Shared-SNR MLP','linear3':'Linear, 3 knots','linear5':'Linear, 5 knots','linear9':'Linear, 9 knots','linear13':'Linear, 13 knots','nearest5':'Nearest, 5 knots'}
for v in pilot['variants']:
    lines.append(f'{labels[v["variant"]]} & {v["serialized_bytes"]:,} & {v["worst_grid_loss_db"]:.6f} '+r'\\')
lines += [r'\bottomrule',r'\end{tabular}']
(OUT/'table_pilot.tex').write_text('\n'.join(lines)+'\n',encoding='utf-8')
lines=[r'\setlength{\tabcolsep}{3pt}',r'\begin{tabular}{rrrrr}',r'\toprule',r'SNR & Original & 13 knots & Loss & 95\% interval \\',r'(dB) & (dB) & (dB) & (mdB) & (mdB) \\',r'\midrule']
for c in test['cells']:
    loss=1000*c['loss_db']
    shown='0.000' if abs(loss)<0.0005 else f'{loss:+.3f}'
    ci=[1000*v for v in c['pointwise_descriptive_95_percentile_interval_db']]
    interval='[0.000, 0.000]' if max(abs(v) for v in ci)<.0005 else f'[{ci[0]:.3f}, {ci[1]:.3f}]'
    lines.append(f'{c["snr_db"]:g} & {c["original_psnr_db"]:.5f} & {c["table_psnr_db"]:.5f} & {shown} & {interval} '+r'\\')
lines += [r'\bottomrule',r'\end{tabular}']
(OUT/'table_test.tex').write_text('\n'.join(lines)+'\n',encoding='utf-8')
manifest={'sources':['results/P002_R003_summary.json','results/P004_R003_analysis.json',
                     'results/P002_gate_tables_R003_preparation.json','results/P001_pilot_summary_v2.json'],
          'test_max_signed_loss_db':max(c['loss_db'] for c in test['cells']),
          'test_max_absolute_change_db':max(abs(c['loss_db']) for c in test['cells']),
          'raw_inputs_unchanged':True,'model_inference':False}
(OUT/'data_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')


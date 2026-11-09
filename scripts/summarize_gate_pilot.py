"""Pool noise MSEs and distinguish each variant's real table knots from common probes."""
import argparse
import json
import math
from pathlib import Path
from witt_support import write_json


def summarize(pilot, preparation):
    if pilot['status'] != 'completed':raise ValueError('Pilot is incomplete')
    variants = {v['variant']: v for v in preparation['variants']}
    baseline = pilot['variants'][0]
    if baseline['variant'] != 'original':raise ValueError('Original reference missing')
    def metric(row, snr):
        ms = [m for repeat in row['repeats'] for m in repeat['metrics'] if m['snr_db'] == snr]
        if len(ms) != pilot['noise_repeats']:raise ValueError('Missing or duplicate cell')
        if any(not math.isfinite(m['mse_0_1']) or m['mse_0_1'] <= 0 for m in ms):
            raise ValueError('Invalid MSE')
        mean_mse = sum(m['mse_0_1'] for m in ms)/len(ms)
        return {'mean_mse_0_1': mean_mse, 'psnr_db': -10*math.log10(mean_mse),
                'mean_image_psnr_db': sum(m['mean_image_psnr_db'] for m in ms)/len(ms)}
    output = []
    for row in pilot['variants']:
        transform = variants[row['variant']]['transformation']
        k = transform['anchors'] if transform else None
        knots = [1+i*12/(k-1) for i in range(k)] if k else []
        cells = []
        for snr in pilot['snrs']:
            reference = metric(baseline, snr); current = metric(row, snr)
            cells.append({'snr_db': snr, **current,
                          'loss_vs_original_db': reference['psnr_db']-current['psnr_db'],
                          'is_table_knot': any(abs(snr-a)<1e-6 for a in knots),
                          'is_original_training_snr': snr in (1,4,7,10,13)})
        off = [c for c in cells if not c['is_table_knot']]
        worst = max(cells, key=lambda c:c['loss_vs_original_db'])
        output.append({'variant': row['variant'], 'knots': knots,
                       'serialized_bytes': row['serialized_bytes'],
                       'serialized_reduction_fraction': row['serialized_reduction_fraction'],
                       'worst_grid_loss_db': worst['loss_vs_original_db'], 'worst_grid_snr_db': worst['snr_db'],
                       'worst_true_off_knot_loss_db': max(c['loss_vs_original_db'] for c in off) if k else None,
                       'fresh_vs_reloaded_max_abs_difference': row['fresh_vs_reloaded_max_abs_difference'],
                       'cells': cells})
    return {'pilot_id': pilot['pilot_id'], 'source_global_step': pilot['source_global_step'],
            'aggregation': 'Average noise-repeat MSE per SNR, then PSNR; losses original minus variant.',
            'scope': 'Only this measured validation grid and checkpoint; no population/global bound.',
            'variants': output}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--pilot', required=True); ap.add_argument('--preparation', required=True)
    ap.add_argument('--output', required=True); args = ap.parse_args()
    output = Path(args.output)
    if output.exists():raise ValueError('Refusing to overwrite summary')
    read = lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
    result = summarize(read(args.pilot), read(args.preparation)); write_json(output, result)
    print(json.dumps([{k:v for k,v in r.items() if k!='cells'} for r in result['variants']], indent=2))

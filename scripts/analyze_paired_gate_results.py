"""Pointwise paired batch-cluster bootstrap, conditional on recorded images/noises/model."""
import argparse
import json
import math
from pathlib import Path
import numpy as np
from witt_support import write_json


def analyze(report, target='linear13'):
    if report['status'] != 'completed':raise ValueError('Incomplete evaluation')
    rows = {r['variant']: r for r in report['variants']}
    cells = []
    for snr in report['snrs']:
        def get(name):
            selected = [next(m for m in r['metrics'] if m['snr_db']==snr) for r in rows[name]['repeats']]
            return selected, np.array([[b['mse_sum'] for b in m['batches']] for m in selected]), np.array([[b['images'] for b in m['batches']] for m in selected])
        ref, a, ca = get('original'); cur, b, cb = get(target)
        if not np.array_equal(ca, cb) or not np.array_equal(ca, np.tile(ca[0], (len(ca),1))):
            raise ValueError('Batch pairing or counts differ')
        if any(x['noise_seed'] != y['noise_seed'] for x,y in zip(ref,cur)):
            raise ValueError('Noise repeats are not paired')
        if not np.isfinite(a).all() or not np.isfinite(b).all() or np.any(a<=0) or np.any(b<=0):
            raise ValueError('Invalid batch errors')
        original_mse = float(a.sum()/ca.sum()); table_mse = float(b.sum()/cb.sum())
        ids = np.random.default_rng(20261108+int(round(snr*1000))).integers(0, a.shape[1], (2000,a.shape[1]))
        # One original batch ID jointly selects all noise repeats and both methods.
        count = ca.sum(axis=0)[ids].sum(axis=1)
        original_boot = a.sum(axis=0)[ids].sum(axis=1)/count
        table_boot = b.sum(axis=0)[ids].sum(axis=1)/count
        interval = np.percentile(10*np.log10(table_boot/original_boot), [2.5,97.5]).tolist()
        cells.append({'snr_db': snr, 'unique_images': ref[0]['images'], 'batch_clusters': a.shape[1],
                      'last_batch_images': int(ca[0,-1]), 'noise_repeats': len(ref),
                      'original_mse': original_mse, 'table_mse': table_mse,
                      'original_psnr_db': -10*math.log10(original_mse),
                      'table_psnr_db': -10*math.log10(table_mse),
                      'loss_db': 10*math.log10(table_mse/original_mse),
                      'pointwise_descriptive_95_percentile_interval_db': interval})
    maximum = max(cells, key=lambda x:x['loss_db'])
    reduction = rows[target]['serialized_reduction_fraction']
    roundtrip = rows[target]['fresh_vs_reloaded_max_abs_difference']
    return {'evaluation_id': report['pilot_id'], 'source_checkpoint': report['source_checkpoint'],
            'source_global_step': report['source_global_step'], 'split': report['split'], 'variant': target,
            'serialized_reduction_fraction': reduction, 'roundtrip_difference': roundtrip,
            'maximum_signed_grid_loss_db': maximum['loss_db'], 'maximum_loss_snr_db': maximum['snr_db'],
            'engineering_gate': {'tolerance_db': .1, 'minimum_storage_reduction': .25,
                                 'passed': maximum['loss_db'] <= .1 and reduction >= .25 and roundtrip == 0},
            'bootstrap': {'draws': 2000, 'seed_base': 20261108, 'unit': 'original batch ID, jointly across methods/noise repeats',
                          'scope': 'Pointwise descriptive percentile intervals conditional on this checkpoint, fixed batch members and recorded noise draws; not simultaneous or continuous-SNR bounds.'},
            'cells': cells}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True); ap.add_argument('--variant', default='linear13')
    args = ap.parse_args(); output = Path(args.output)
    if output.exists():raise ValueError('Refusing to overwrite analysis')
    result = analyze(json.loads(Path(args.input).read_text(encoding='utf-8')), args.variant)
    write_json(output, result)
    print(json.dumps({k:v for k,v in result.items() if k!='cells'}, indent=2))

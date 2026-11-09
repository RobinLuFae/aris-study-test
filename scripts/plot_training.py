"""Render recorded validation curves without touching model or data."""
from pathlib import Path
import argparse
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    run = Path(args.run)
    rows = [json.loads(line) for line in (run/'metrics.jsonl').read_text().splitlines()]
    vals = [r for r in rows if r['type'] == 'validation']
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for snr in sorted({m['snr_db'] for r in vals for m in r['metrics']}):
        selected = [(r['global_step'], m['psnr_from_mean_mse_db'])
                    for r in vals for m in r['metrics'] if m['snr_db'] == snr]
        axes[0].plot(*zip(*selected), marker='o', markersize=3, label=f'{snr} dB')
    axes[0].set(xlabel='Optimizer update', ylabel='PSNR from mean MSE (dB)')
    axes[0].legend(title='Physical SNR')
    axes[1].plot([r['global_step'] for r in vals],
                 [r['selection_mean_mse_0_1'] for r in vals], marker='o', markersize=3)
    axes[1].set(xlabel='Optimizer update', ylabel='Selection mean MSE', yscale='log')
    for axis in axes:
        axis.grid(alpha=.25)
    cfg = json.loads((run/'metadata.json').read_text())['config']
    boundary = 0
    for stage in cfg['stages'][:-1]:
        boundary += stage['steps']
        for axis in axes:
            axis.axvline(boundary, color='gray', linestyle='--', linewidth=1)
    fig.suptitle(f"{cfg['run_id']} — validation; CBR=1/3")
    fig.tight_layout()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)
    print(json.dumps({'output': str(output), 'validation_records': len(vals)}))


if __name__ == '__main__':
    main()

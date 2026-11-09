"""Paired image-quality and idle-device latency pilot for saved deployment variants."""
from pathlib import Path
import argparse
import json
import math
import statistics
import sys
import time
import torch
from witt_support import ROOT, build_model, upstream_version, write_json
from snr_gate_table import install_empty_tables, share_snr_computation, tabulate_snr_gates
from training_budget import TrainingWindow
from validation_data import frozen_validation
from witt_conditioning import conditioned_forward

SNRS = [1, 2, 2.25, 4, 5, 5.25, 7, 8, 8.25, 10, 11, 11.25, 13]


def load_deployment(path, device):
    artifact = torch.load(path, map_location='cpu', weights_only=True)
    cfg = dict(artifact['config'], device=device)
    model = build_model(cfg, 'WITT')
    if artifact['anchors']:
        install_empty_tables(model, artifact['anchors'], artifact['interpolation'])
    elif artifact['variant'] == 'shared_snr':
        share_snr_computation(model)
    model.load_state_dict(artifact['state_dict'], strict=True)
    model.eval()
    return model, cfg, {k: v for k, v in artifact.items() if k != 'state_dict'}


def freshly_compile(metadata, cfg):
    source = torch.load(metadata['source_checkpoint'], map_location='cpu', weights_only=True)
    model = build_model(dict(cfg, device='cpu'), 'WITT')
    model.load_state_dict(source['state_dict'], strict=True); model.eval()
    if metadata['anchors']:
        tabulate_snr_gates(model, metadata['anchors'], metadata['interpolation'])
    elif metadata['variant'] == 'shared_snr':
        share_snr_computation(model)
    model.to(cfg['device'])
    model.config.device = torch.device(cfg['device'])
    model.channel.device = torch.device(cfg['device'])
    return model


@torch.no_grad()
def evaluate(model, images, indices, cfg, repeat, budget):
    metrics = []
    for snr in SNRS:
        if budget.should_checkpoint():raise TimeoutError('Approved evaluation window exhausted')
        seed = 51001+repeat*100000+int(round(snr*1000))
        torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
        squared_sum = psnr_sum = 0.; count = 0
        for idx in indices.split(cfg['batch_size']):
            x = images[idx].to(cfg['device'], dtype=torch.float32)/255.
            y, cbr, *_ = model(x, given_SNR=snr)
            if not torch.isfinite(y).all():raise RuntimeError('Nonfinite reconstruction')
            error = (y.clamp(0, 1)-x).square().flatten(1).mean(1)
            squared_sum += error.sum().item()
            psnr_sum += (-10*torch.log10(error.clamp_min(1e-12))).sum().item()
            count += len(idx)
        metrics.append({'snr_db': snr, 'noise_seed': seed, 'images': count, 'cbr': cbr,
                        'mse_0_1': squared_sum/count,
                        'psnr_from_mean_mse_db': -10*math.log10(max(squared_sum/count, 1e-12)),
                        'mean_image_psnr_db': psnr_sum/count})
    return metrics


@torch.no_grad()
def latency(model, images, indices, cfg, budget):
    rows = []
    for batch in (1, 128):
        if budget.should_checkpoint():raise TimeoutError('Approved evaluation window exhausted')
        x = images[indices[:batch]].to(cfg['device'], dtype=torch.float32)/255.
        for _ in range(10):conditioned_forward(model, x, 7, 7)
        timings = []
        for _ in range(30):
            torch.cuda.synchronize(); started = time.perf_counter()
            conditioned_forward(model, x, 7, 7); torch.cuda.synchronize()
            timings.append((time.perf_counter()-started)*1000)
        rows.append({'batch_size': batch, 'snr_db': 7, 'warmup': 10, 'repeats': 30,
                     'median_ms': statistics.median(timings),
                     'p90_ms': sorted(timings)[math.ceil(.9*len(timings))-1],
                     'samples_ms': timings,
                     'scope': 'Synchronized encoder+authorAWGN+decoder forward, excluding image metrics; inputs already on GPU; idle research GPU.'})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preparation', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--budget-file', default=str(ROOT/'configs/training_window_2026-11-07.json'))
    args = ap.parse_args()
    assert Path(sys.prefix).resolve() == (ROOT/'.conda').resolve()
    output = Path(args.output)
    if output.suffix != '.json' or output.exists():raise ValueError('Use a new .json output')
    budget = TrainingWindow(args.budget_file, 1200)
    prep = json.loads(Path(args.preparation).read_text(encoding='utf-8'))
    first = torch.load(ROOT/prep['variants'][0]['artifact'], map_location='cpu', weights_only=True)
    cfg = dict(first['config'], device='cuda:0')
    source = upstream_version()
    if source != first['source']:raise ValueError('Author source mismatch')
    torch.set_num_threads(cfg['cpu_threads'])
    torch.backends.cudnn.benchmark = False; torch.backends.cudnn.deterministic = True
    images, indices = frozen_validation(cfg, 1000)
    report = {'pilot_id': prep['pilot_id'], 'source_checkpoint': prep['source_checkpoint'],
              'source_global_step': first['source_global_step'], 'source': source,
              'split': 'validation', 'validation_indices': indices.tolist(), 'test_partition_used': False,
              'snrs': SNRS, 'noise_repeats': 3, 'gpu': torch.cuda.get_device_name(),
              'torch': torch.__version__, 'status': 'running', 'variants': []}
    del first
    original_witness = None
    try:
        for variant in prep['variants']:
            model, _, metadata = load_deployment(ROOT/variant['artifact'], cfg['device'])
            if metadata['source'] != source or metadata['source_checkpoint'] != prep['source_checkpoint']:
                raise ValueError('Variant has a different source')
            witness = {}
            with torch.no_grad():
                x = images[indices[:8]].to(cfg['device'], dtype=torch.float32)/255.
                for snr in [1., 2.25, 7., 13.]:
                    torch.manual_seed(71001); torch.cuda.manual_seed_all(71001)
                    witness[str(snr)] = model(x, given_SNR=snr)[0].cpu()
            fresh_model = freshly_compile(metadata, cfg)
            roundtrip_error = 0.
            with torch.no_grad():
                for snr in [1., 2.25, 7., 13.]:
                    torch.manual_seed(71001); torch.cuda.manual_seed_all(71001)
                    prediction = fresh_model(x, given_SNR=snr)[0].cpu()
                    if not torch.isfinite(prediction).all() or not torch.isfinite(witness[str(snr)]).all():
                        raise RuntimeError('Nonfinite serialization witness')
                    roundtrip_error = max(roundtrip_error, (prediction-witness[str(snr)]).abs().max().item())
            del fresh_model
            if roundtrip_error != 0:
                raise RuntimeError(f'Freshly compiled and saved/reloaded {variant["variant"]} differ: {roundtrip_error}')
            if original_witness is None:original_witness = witness
            difference = {s: {'max_abs_reconstruction_difference': (y-original_witness[s]).abs().max().item(),
                              'rms_reconstruction_difference': (y-original_witness[s]).square().mean().sqrt().item()}
                          for s, y in witness.items()}
            row = {'variant': variant['variant'], 'serialized_bytes': variant['serialized_bytes'],
                   'serialized_reduction_fraction': variant['serialized_reduction_fraction'],
                   'parameter_count': sum(p.numel() for p in model.parameters()),
                   'fresh_vs_reloaded_max_abs_difference': roundtrip_error,
                   'paired_witness_difference': difference,
                   'repeats': [{'repeat': i, 'metrics': evaluate(model, images, indices, cfg, i, budget)}
                               for i in range(3)],
                   'latency': latency(model, images, indices, cfg, budget)}
            report['variants'].append(row)
            write_json(output.with_suffix('.progress.json'), report)
            print(json.dumps({k: v for k, v in row.items() if k not in ('repeats', 'latency')}), flush=True)
            del model; torch.cuda.empty_cache()
        report['status'] = 'completed'
        write_json(output, report)
        print('GATE_TABLE_PILOT_COMPLETED', flush=True)
    except BaseException as error:
        report['status'] = 'incomplete'; report['error'] = repr(error)
        write_json(output.with_suffix('.progress.json'), report)
        raise


if __name__ == '__main__':
    main()

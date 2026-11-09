"""Paired validation, or a final test admitted only by a saved validation/freeze receipt."""
from pathlib import Path
import argparse
import json
import math
import shutil
import sys
import torch
import torchvision
from witt_support import ROOT, upstream_version, write_json
from evaluate_gate_tables import load_deployment, freshly_compile
from training_budget import TrainingWindow
from validation_data import frozen_validation


@torch.no_grad()
def evaluate_cell(model, images, indices, cfg, snr, repeat, budget):
    if budget.should_checkpoint():raise TimeoutError('Approved computation window exhausted')
    seed = cfg['evaluation_noise_seed_base']+repeat*100000+int(round(snr*1000))
    torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    batches = []
    for position, idx in enumerate(indices.split(cfg['batch_size'])):
        if budget.should_checkpoint():raise TimeoutError('Approved computation window exhausted between batches')
        x = images[idx].to(cfg['device'], dtype=torch.float32)/255.
        y, cbr, *_ = model(x, given_SNR=snr)
        if not torch.isfinite(y).all():raise RuntimeError('Nonfinite reconstruction')
        error = (y.clamp(0, 1)-x).square().flatten(1).mean(1)
        batches.append({'position': position, 'images': len(idx), 'mse_sum': error.sum().item(),
                        'image_psnr_sum': (-10*torch.log10(error.clamp_min(1e-12))).sum().item()})
    count = sum(b['images'] for b in batches)
    mse = sum(b['mse_sum'] for b in batches)/count
    return {'snr_db': snr, 'noise_seed': seed, 'images': count, 'cbr': cbr,
            'mse_0_1': mse, 'psnr_from_mean_mse_db': -10*math.log10(max(mse, 1e-12)),
            'mean_image_psnr_db': sum(b['image_psnr_sum'] for b in batches)/count, 'batches': batches}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preparation', required=True); ap.add_argument('--protocol', required=True)
    ap.add_argument('--output', required=True); ap.add_argument('--budget-file', required=True)
    args = ap.parse_args()
    assert Path(sys.prefix).resolve() == (ROOT/'.conda').resolve()
    read = lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
    protocol = read(args.protocol); prep = read(args.preparation); output = Path(args.output)
    if output.suffix != '.json' or output.exists():raise ValueError('Use a fresh .json output')
    snapshots = ROOT/'runs'/protocol['run_id']/'source'
    if snapshots.exists():raise ValueError('Run source directory already exists; do not reopen evaluation')
    if protocol['split'] not in ('validation', 'test'):raise ValueError('Unknown split')
    if protocol['variants'][0] != 'original':raise ValueError('Original must be the first reference')
    if (protocol['noise_repeats'] < 1 or len(set(protocol['snrs'])) != len(protocol['snrs']) or
        not all(math.isfinite(s) and 1 <= s <= 13 for s in protocol['snrs'])):
        raise ValueError('Invalid fixed protocol')
    budget = TrainingWindow(args.budget_file, 1200)
    source = upstream_version(); lookup = {v['variant']: v for v in prep['variants']}
    models = [lookup[name] for name in protocol['variants']]
    first = torch.load(ROOT/models[0]['artifact'], map_location='cpu', weights_only=True)
    cfg = dict(first['config'], device='cuda:0')
    cfg['evaluation_noise_seed_base'] = protocol.get('noise_seed_base', 51001)
    if first['source'] != source or source['worktree_status']:raise ValueError('Author source mismatch')
    torch.set_num_threads(cfg['cpu_threads'])
    torch.backends.cudnn.benchmark = False; torch.backends.cudnn.deterministic = True
    if protocol['split'] == 'validation':
        images, indices = frozen_validation(cfg, protocol['samples'])
    else:
        freeze = read(protocol['freeze_file'])
        intended = {k:v for k,v in protocol.items() if k != 'freeze_file'}
        if (not freeze['validation_gate']['passed'] or freeze['test_protocol'] != intended or
            freeze['source_checkpoint'] != prep['source_checkpoint'] or
            freeze['preparation_id'] != prep['pilot_id'] or protocol['samples'] != 10000):
            raise ValueError('Final test does not match the passed, frozen validation protocol')
        for name in ('original','linear13'):
            path = (ROOT/lookup[name]['artifact']).resolve(); saved = freeze['artifacts'][name]
            if str(path)!=saved['path'] or path.stat().st_size!=saved['bytes']:
                raise ValueError('Final deployment path/size differs from freeze')
            deployment = first if name=='original' else torch.load(path,map_location='cpu',weights_only=True)
            if (deployment['source_checkpoint']!=freeze['source_checkpoint'] or
                deployment['source_global_step']!=freeze['source_global_step'] or
                deployment['config']['batch_size']!=freeze['batch_size'] or
                deployment['source']!=source or deployment['variant']!=name):
                raise ValueError('Final deployment metadata differs from freeze')
            if name!='original':del deployment
        if cfg['batch_size']!=128 or 1-freeze['artifacts']['linear13']['bytes']/freeze['artifacts']['original']['bytes']<.25:
            raise ValueError('Final batch or storage constraint violated')
        dataset = torchvision.datasets.CIFAR10(str(ROOT/'data'), train=False, download=False)
        images = torch.from_numpy(dataset.data).permute(0,3,1,2).contiguous()
        if len(images) != 10000:raise ValueError('Unexpected official test count')
        indices = torch.arange(len(images))
    snapshots.mkdir(parents=True, exist_ok=False)
    names = ['evaluate_gate_tables_paired.py', 'evaluate_gate_tables.py', 'snr_gate_table.py',
             'witt_support.py', 'witt_conditioning.py', 'validation_data.py', 'training_budget.py',
             'analyze_paired_gate_results.py', 'freeze_gate_test.py']
    for name in names:shutil.copy2(ROOT/'scripts'/name, snapshots/name)
    write_json(snapshots/'protocol.json', protocol); write_json(snapshots/'budget.json', budget.config)
    if protocol['split']=='test':write_json(snapshots/'freeze.json',freeze)
    report = {'pilot_id': protocol['run_id'], 'preparation_id': prep['pilot_id'],
              'source_checkpoint': prep['source_checkpoint'], 'source_global_step': first['source_global_step'],
              'source': source, 'protocol': protocol, 'split': protocol['split'], 'evaluation_indices': indices.tolist(),
              'test_partition_used': protocol['split']=='test', 'snrs': protocol['snrs'], 'noise_repeats': protocol['noise_repeats'],
              'gpu': torch.cuda.get_device_name(), 'torch': torch.__version__, 'cuda_runtime': torch.version.cuda,
              'cpu_threads': cfg['cpu_threads'], 'argv': sys.argv,
              'execution_source': str(snapshots.relative_to(ROOT)), 'status': 'running', 'variants': []}
    del first
    try:
        for variant in models:
            model, _, metadata = load_deployment(ROOT/variant['artifact'], cfg['device'])
            if metadata['source'] != source or metadata['source_checkpoint'] != prep['source_checkpoint']:
                raise ValueError('Variant source mismatch')
            fresh = freshly_compile(metadata, cfg)
            witness_error = 0.
            with torch.no_grad():
                x = (torch.linspace(0,1,8*3*32*32,device=cfg['device']).reshape(8,3,32,32)
                     if protocol['split']=='test' else images[indices[:8]].to(cfg['device'],dtype=torch.float32)/255.)
                for snr in [1., 1.5, 2.375, 7., 13.]:
                    torch.manual_seed(71001); torch.cuda.manual_seed_all(71001)
                    y = model(x, given_SNR=snr)[0]
                    torch.manual_seed(71001); torch.cuda.manual_seed_all(71001)
                    z = fresh(x, given_SNR=snr)[0]
                    if not torch.isfinite(y).all() or not torch.isfinite(z).all():
                        raise RuntimeError('Nonfinite round-trip witness')
                    witness_error = max(witness_error, (y-z).abs().max().item())
            del fresh
            if witness_error != 0:raise RuntimeError('Saved/reloaded deployment differs from freshly compiled')
            row = {'variant': variant['variant'], 'serialized_bytes': variant['serialized_bytes'],
                   'serialized_reduction_fraction': variant['serialized_reduction_fraction'],
                   'fresh_vs_reloaded_max_abs_difference': witness_error, 'repeats': []}
            report['variants'].append(row)
            for repeat in range(protocol['noise_repeats']):
                current = {'repeat': repeat, 'metrics': []}; row['repeats'].append(current)
                for snr in protocol['snrs']:
                    current['metrics'].append(evaluate_cell(model, images, indices, cfg, snr, repeat, budget))
                    write_json(output.with_suffix('.progress.json'), report)
            print(json.dumps({'variant': row['variant'], 'completed_cells': len(protocol['snrs'])*protocol['noise_repeats']}), flush=True)
            del model; torch.cuda.empty_cache()
        report['status'] = 'completed'; write_json(output, report)
        print('PAIRED_GATE_VALIDATION_COMPLETED', flush=True)
    except BaseException as error:
        report['status'] = 'incomplete'; report['error'] = repr(error)
        write_json(output.with_suffix('.progress.json'), report)
        raise


if __name__ == '__main__':
    main()

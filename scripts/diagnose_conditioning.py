"""Validation-only, paired-noise WITT conditioning diagnostic; no tuning on test."""
from pathlib import Path
import argparse
import json
import math
import sys
import torch
import torchvision
from witt_support import ROOT, build_model, upstream_version, write_json
from witt_conditioning import conditioned_forward


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--checkpoint', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    assert Path(sys.prefix).resolve() == (ROOT/'.conda').resolve()
    output = Path(args.output)
    if output.suffix != '.json' or output.exists():
        raise ValueError('Use a new .json output path')
    ckpt = torch.load(args.checkpoint, map_location='cpu', weights_only=True)
    cfg = ckpt['config']
    expected = ROOT/'checkpoints'/cfg['run_id']/'adaptive_best.pt'
    if Path(args.checkpoint).resolve() != expected.resolve() or ckpt['stage']['model'] != 'WITT':
        raise ValueError('Diagnostic requires the validation-selected adaptive WITT checkpoint')
    status = json.loads((ROOT/'runs'/cfg['run_id']/'status.json').read_text())
    if status['status'] != 'completed':
        raise ValueError('Baseline run must complete before this diagnostic')
    version = upstream_version()
    if version['worktree_status'] or version['commit'] != ckpt['source']['commit']:
        raise RuntimeError('Author source differs from checkpoint source')
    torch.set_num_threads(cfg['cpu_threads'])
    torch.manual_seed(42001); torch.cuda.manual_seed_all(42001)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    model = build_model(cfg, ckpt['stage']['model'])
    model.load_state_dict(ckpt['state_dict'], strict=True); model.eval()
    split_file = ROOT/'data/splits'/f"cifar10_seed{cfg['split_seed']}_val{cfg['validation_size']}.json"
    split = json.loads(split_file.read_text(encoding='utf-8'))
    train_ids, validation = split['train'], split['validation']
    if (len(train_ids) != 45000 or len(validation) != 5000 or
        len(set(train_ids) | set(validation)) != 50000 or set(train_ids) & set(validation)):
        raise ValueError('Existing 45k/5k training-partition split is invalid')
    class TrainOnlyCIFAR10(torchvision.datasets.CIFAR10):
        # Exclude even test-file integrity reads in this validation-only diagnostic.
        test_list = []
    dataset = TrainOnlyCIFAR10(str(ROOT/'data'), train=True, download=False)
    images = torch.from_numpy(dataset.data).permute(0, 3, 1, 2).contiguous()
    val_ids = torch.tensor(validation)
    indices = val_ids[:1000]
    with torch.no_grad():
        x = images[indices[:8]].to(cfg['device'], dtype=torch.float32)/255.
        torch.manual_seed(78001); torch.cuda.manual_seed_all(78001)
        reference = model(x, given_SNR=7)[0]
        torch.manual_seed(78001); torch.cuda.manual_seed_all(78001)
        same = conditioned_forward(model, x, 7, 7)[0]
        difference = (reference-same).abs().max().item()
        if difference != 0:
            raise RuntimeError(f'Matched-SNR adapter differs from author forward: {difference}')
        records = []
        for repeat in range(3):
            for physical in (4, 7, 10):
                for error in (-3, 0, 3):
                    seed = 31001+repeat*10000+physical*100
                    torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
                    mse_sum = psnr_sum = 0.; count = 0
                    for idx in indices.split(cfg['batch_size']):
                        x = images[idx].to(cfg['device'], dtype=torch.float32)/255.
                        y, cbr = conditioned_forward(model, x, physical, physical+error)
                        if not torch.isfinite(y).all():
                            raise RuntimeError('Nonfinite reconstruction')
                        per_image = (y.clamp(0, 1)-x).square().flatten(1).mean(1)
                        mse_sum += per_image.sum().item()
                        psnr_sum += (-10*torch.log10(per_image.clamp_min(1e-12))).sum().item()
                        count += len(idx)
                    row = {'repeat': repeat, 'noise_seed': seed, 'physical_snr_db': physical,
                           'encoder_snr_db': physical+error, 'decoder_snr_db': physical+error,
                           'conditioning_error_db': error, 'images': count, 'cbr': cbr,
                           'mse_0_1': mse_sum/count,
                           'psnr_from_mean_mse_db': -10*math.log10(max(mse_sum/count, 1e-12)),
                           'mean_image_psnr_db': psnr_sum/count}
                    if not all(math.isfinite(row[k]) for k in ('mse_0_1', 'mean_image_psnr_db')):
                        raise RuntimeError('Nonfinite metric')
                    records.append(row); print(json.dumps(row), flush=True)
    write_json(output, {'checkpoint': str(Path(args.checkpoint).resolve()),
               'global_step': ckpt['global_step'], 'source': version,
               'split': 'validation', 'split_file': str(split_file.relative_to(ROOT)),
               'validation_indices': indices.tolist(), 'matched_forward_max_abs_difference': difference,
               'protocol': 'Fixed first 1000 validation images, 3 noise repeats, same error at encoder and decoder; all conditioning values inside 1..13 dB; physical AWGN SNR remains unchanged.',
               'records': records, 'test_partition_used': False})


if __name__ == '__main__':
    main()

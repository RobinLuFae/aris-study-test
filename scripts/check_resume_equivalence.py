"""Real 22-update uninterrupted vs 20+2 checkpoint continuation comparison."""
from pathlib import Path
import json
import subprocess
import sys
import torch
from witt_support import ROOT, write_json


def equal(a, b):
    if isinstance(a, torch.Tensor):
        return isinstance(b, torch.Tensor) and torch.equal(a, b)
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(equal(a[k], b[k]) for k in a)
    if isinstance(a, (tuple, list)):
        return len(a) == len(b) and all(equal(x, y) for x, y in zip(a, b))
    return a == b


def main():
    assert Path(sys.prefix).resolve() == (ROOT/'.conda').resolve()
    original = ROOT/'checkpoints/R000_witt_sanity_seed42/pretrain_final.pt'
    previous = torch.load(original, map_location='cpu', weights_only=True)
    cfg = previous['config']; del previous
    cfg['stages'][-1]['steps'] = 22
    run_ids = ['RSM00_continuous22', 'RSM01_resumed22']
    for i, run_id in enumerate(run_ids):
        config = dict(cfg, run_id=run_id)
        path = ROOT/'configs'/f'{run_id}.json'; write_json(path, config)
        command = [sys.executable, '-B', '-X', 'utf8', str(ROOT/'scripts/train_witt.py'),
                   '--config', str(path)]
        if i: command += ['--resume', str(original)]
        with (ROOT/'logs'/f'{run_id}.log').open('w', encoding='utf-8') as log:
            subprocess.run(command, cwd=ROOT, check=True, stdout=log, stderr=subprocess.STDOUT)
    reference, resumed = [torch.load(ROOT/'checkpoints'/r/'pretrain_final.pt',
                                     map_location='cpu', weights_only=True) for r in run_ids]
    keys = ['state_dict', 'optimizer', 'stage_step', 'global_step', 'validation',
            'sampler_order', 'sampler_offset', 'sampler_epoch', 'sampler_rng',
            'torch_rng', 'cuda_rng', 'python_rng']
    checks = {k: equal(reference[k], resumed[k]) for k in keys}
    record = {'comparison': 'continuous22 versus original R00020 + resumed2',
              'checks': checks, 'passed': all(checks.values()),
              'max_parameter_abs_difference': max((reference['state_dict'][k]-v).abs().max().item()
                                                   for k, v in resumed['state_dict'].items()),
              'scope': 'Same machine/software, fixed-SNR pretrain path; compares final not best checkpoints.'}
    write_json(ROOT/'logs/resume-equivalence.json', record)
    print(json.dumps(record, indent=2))
    if not record['passed']:raise RuntimeError('Resume trajectory diverged')


if __name__ == '__main__':
    main()

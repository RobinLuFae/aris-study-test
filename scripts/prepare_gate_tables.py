"""CPU-only preparation of original and genuinely compressed WITT deployment states."""
from pathlib import Path
import argparse
import json
import sys
import torch
from witt_support import ROOT, build_model, upstream_version, write_json
from snr_gate_table import tabulate_snr_gates, share_snr_computation


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--checkpoint', required=True)
    ap.add_argument('--pilot-id', default='P000_gate_tables_R001')
    args = ap.parse_args()
    assert Path(sys.prefix).resolve() == (ROOT/'.conda').resolve()
    record_path = ROOT/'results'/f'{args.pilot_id}_preparation.json'
    folder = ROOT/'checkpoints'/args.pilot_id
    if record_path.exists() or folder.exists():
        raise RuntimeError('Use a new pilot id; do not overwrite artifacts')
    checkpoint = torch.load(args.checkpoint, map_location='cpu', weights_only=True)
    if checkpoint['stage']['model'] != 'WITT':raise ValueError('Adaptive WITT required')
    version = upstream_version()
    if version != checkpoint['source']:raise ValueError('Author source mismatch')
    cfg = dict(checkpoint['config'], device='cpu')
    torch.set_num_threads(cfg['cpu_threads'])
    folder.mkdir(parents=True)
    rows = []
    for name, anchors, interpolation in [('original', None, None), ('shared_snr', None, None),
            ('linear3', 3, 'linear'), ('linear5', 5, 'linear'), ('linear9', 9, 'linear'),
            ('linear13', 13, 'linear'), ('nearest5', 5, 'nearest')]:
        model = build_model(cfg, 'WITT'); model.load_state_dict(checkpoint['state_dict'], strict=True)
        model.eval()
        transform = tabulate_snr_gates(model, anchors, interpolation) if anchors else None
        if name == 'shared_snr':share_snr_computation(model)
        artifact = {'state_dict': model.state_dict(), 'config': cfg, 'model': 'WITT',
                    'source': version, 'source_checkpoint': str(Path(args.checkpoint).resolve()),
                    'source_global_step': checkpoint['global_step'], 'variant': name,
                    'anchors': anchors, 'interpolation': interpolation,
                    'format': 'witt-snr-table-deployment-v1'}
        path = folder/f'{name}.pt'; torch.save(artifact, path)
        rows.append({'variant': name, 'artifact': str(path.relative_to(ROOT)),
                     'serialized_bytes': path.stat().st_size,
                     'parameter_count': sum(p.numel() for p in model.parameters()),
                     'state_tensor_bytes': sum(t.numel()*t.element_size() for t in model.state_dict().values()),
                     'transformation': transform})
        del artifact, model
    original = rows[0]['serialized_bytes']
    for row in rows:row['serialized_reduction_fraction'] = 1-row['serialized_bytes']/original
    record = {'pilot_id': args.pilot_id, 'source_checkpoint': str(Path(args.checkpoint).resolve()),
              'device_for_preparation': 'cpu', 'gpu_used': False, 'variants': rows,
              'metrics': 'Storage and gate-function approximation only; no image quality evaluated yet.'}
    write_json(record_path, record)
    print(json.dumps({k: v for k, v in record.items() if k != 'variants'}, indent=2))
    print(json.dumps([{k: v for k, v in row.items() if k != 'transformation'} for row in rows], indent=2))


if __name__ == '__main__':
    main()

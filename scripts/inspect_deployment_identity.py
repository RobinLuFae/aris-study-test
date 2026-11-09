"""CPU artifact inspection only; no images, channel samples, or model inference."""
from pathlib import Path
import json
import torch

ROOT=Path(__file__).resolve().parents[1]
paths={name:ROOT/'checkpoints/P002_gate_tables_R003'/f'{name}.pt' for name in ('original','linear13')}
artifacts={k:torch.load(p,map_location='cpu',weights_only=True) for k,p in paths.items()}
states={k:a['state_dict'] for k,a in artifacts.items()}
original={k:v for k,v in states['original'].items() if '.bm_list.' not in k}
table={k:v for k,v in states['linear13'].items() if '.bm_list.' not in k}
assert original.keys()==table.keys()
assert all(torch.equal(original[k],table[k]) for k in original)
for a in artifacts.values():
    assert not any(k in a for k in ('optimizer','optimizer_state_dict','adam'))
report={'inspection':'CPU state comparison and top-level key inventory; no inference',
        'retained_non_gate_tensor_count':len(original),'all_retained_tensors_equal':True,
        'artifacts':{name:{'path':str(paths[name].relative_to(ROOT)),
                           'bytes':paths[name].stat().st_size,
                           'top_level_keys':list(a),'source':a.get('source'),
                           'source_global_step':a.get('source_global_step'),
                           'optimizer_state_present':False} for name,a in artifacts.items()}}
out=ROOT/'results/deployment_identity_receipt_20261109.json'
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('RETAINED_TENSORS_IDENTICAL',len(original),'NO_OPTIMIZER_STATE; receipt:',out)

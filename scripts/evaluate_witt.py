"""Explicit held-out or validation evaluation; never invoked by training."""
from pathlib import Path
import argparse
import json
import sys

from witt_support import ROOT,build_model,upstream_version,write_json
from train_witt import validate
import torch
import torchvision


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--checkpoint',required=True)
    ap.add_argument('--output',required=True)
    ap.add_argument('--split',choices=['validation','test'],default='validation')
    ap.add_argument('--snrs',default='1,4,7,10,13')
    ap.add_argument('--repeats',type=int,default=3)
    ap.add_argument('--preview',action='store_true')
    args=ap.parse_args()
    if args.preview and args.split!='validation':
        raise ValueError('Use validation for pre-final visual diagnostics')
    assert Path(sys.prefix).resolve()==(ROOT/'.conda').resolve()
    output=Path(args.output)
    if output.suffix.lower()!='.json':raise ValueError('Evaluation output must have a .json suffix')
    if output.exists():raise RuntimeError(f'Refusing to overwrite evaluation: {output}')
    if args.preview and output.with_suffix('.png').exists():
        raise RuntimeError('The corresponding preview image already exists')
    if args.repeats<1:raise ValueError('repeats must be positive')
    checkpoint=torch.load(args.checkpoint,map_location='cpu',weights_only=True)
    cfg=dict(checkpoint['config']);cfg['validation_snrs']=[int(s) for s in args.snrs.split(',')]
    torch.set_num_threads(cfg['cpu_threads']);torch.manual_seed(42001);torch.cuda.manual_seed_all(42001)
    torch.backends.cudnn.benchmark=False
    torch.backends.cudnn.deterministic=True
    source=upstream_version()
    if source['commit']!=checkpoint['source']['commit'] or source['worktree_status']:
        raise RuntimeError('The upstream source differs from the checkpoint source')
    model=build_model(cfg,checkpoint['stage']['model']);model.load_state_dict(checkpoint['state_dict'],strict=True)
    # Release the CPU optimizer/sampler payload before evaluation.
    stage=checkpoint['stage'];global_step=checkpoint['global_step'];del checkpoint
    dataset=torchvision.datasets.CIFAR10(str(ROOT/'data'),train=args.split=='validation',download=False)
    images=torch.from_numpy(dataset.data).permute(0,3,1,2).contiguous()
    if args.split=='validation':
        split=json.loads((ROOT/'data/splits'/f"cifar10_seed{cfg['split_seed']}_val{cfg['validation_size']}.json").read_text(encoding='utf-8'))
        indices=torch.tensor(split['validation'])
    else:
        indices=torch.arange(len(dataset))
    results=[]
    for repeat in range(args.repeats):
        rc=dict(cfg,validation_noise_seed=cfg['validation_noise_seed']+repeat*10000)
        metrics=validate(model,images,indices,rc)
        results.append({'repeat':repeat,'noise_seed_base':rc['validation_noise_seed'],'metrics':metrics})
    record={'checkpoint':str(Path(args.checkpoint).resolve()),'split':args.split,'images':len(indices),
            'stage':stage,'global_step':global_step,'source':source,'repeats':results,
            'scope':'Local trained model evaluation; paper-reported numbers are not mixed in.'}
    if args.preview:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        model.eval();selected=indices[:8];x=images[selected].to(cfg['device'],dtype=torch.float32)/255.
        rows=[x.cpu()];labels=['Original']
        with torch.no_grad(),torch.random.fork_rng(devices=[torch.device(cfg['device']).index or 0]):
            for snr in [1,7,13]:
                torch.manual_seed(2000+snr);torch.cuda.manual_seed_all(2000+snr)
                y,*_=model(x,given_SNR=snr);rows.append(y.clamp(0,1).cpu());labels.append(f'{snr} dB')
        fig,axes=plt.subplots(len(rows),len(selected),figsize=(12,6),squeeze=False)
        for r,imgs in enumerate(rows):
            for c,img in enumerate(imgs):
                axes[r,c].imshow(img.permute(1,2,0),interpolation='nearest')
                axes[r,c].set_xticks([]);axes[r,c].set_yticks([])
                if c==0:axes[r,c].set_ylabel(labels[r])
        fig.suptitle(f'WITT validation samples; step {global_step}; CBR=1/3')
        output.parent.mkdir(parents=True,exist_ok=True)
        fig.tight_layout();fig.savefig(output.with_suffix('.png'),dpi=160);plt.close(fig)
    write_json(output,record)
    print(json.dumps(record,ensure_ascii=False,indent=2))

if __name__=='__main__':main()

from pathlib import Path
from types import SimpleNamespace
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def build_model(config, mode):
    import torch
    repo=ROOT/'baselines/upstream/WITT'
    if str(repo) not in sys.path:sys.path.insert(0,str(repo))
    from net.network import WITT
    args=SimpleNamespace(model=mode,channel_type=config['channel'],multiple_snr='1,4,7,10,13',
                         distortion_metric='MSE',trainset='CIFAR10')
    c=SimpleNamespace(device=torch.device(config['device']),CUDA=True,logger=None,norm=False,
                      pass_channel=True,downsample=2)
    c.encoder_kwargs=dict(img_size=(32,32),patch_size=2,in_chans=3,embed_dims=[128,256],
                          depths=[2,4],num_heads=[4,8],C=config['C'],window_size=2,mlp_ratio=4.,
                          qkv_bias=True,qk_scale=None,norm_layer=torch.nn.LayerNorm,patch_norm=True)
    c.decoder_kwargs=dict(img_size=(32,32),embed_dims=[256,128],depths=[4,2],num_heads=[8,4],
                          C=config['C'],window_size=2,mlp_ratio=4.,qkv_bias=True,qk_scale=None,
                          norm_layer=torch.nn.LayerNorm,patch_norm=True)
    return WITT(args,c).to(c.device)

def upstream_version():
    repo=ROOT/'baselines/upstream/WITT'
    cmd=['git','-c',f'safe.directory={repo}','-C',str(repo)]
    return {'url':'https://github.com/KeYang8/WITT',
            'commit':subprocess.check_output(cmd+['rev-parse','HEAD'],text=True).strip(),
            'worktree_status':subprocess.check_output(cmd+['status','--porcelain'],text=True).strip()}

def write_json(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    temp.replace(path)

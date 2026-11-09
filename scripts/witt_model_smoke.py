"""Run the author's CIFAR-10 model without importing its training entrypoint."""
from pathlib import Path
from types import SimpleNamespace
import datetime
import json
import subprocess
import sys
import time

root=Path(__file__).resolve().parents[1]
assert Path(sys.prefix).resolve()==(root/'.conda').resolve()
repo=root/'baselines/upstream/WITT'
sys.path.insert(0,str(repo))
import torch
from net.network import WITT

torch.set_num_threads(4)
torch.manual_seed(42)
torch.cuda.manual_seed_all(42)
torch.backends.cudnn.benchmark=False
args=SimpleNamespace(model='WITT',channel_type='awgn',multiple_snr='1,4,7,10,13',
                     distortion_metric='MSE',trainset='CIFAR10')
config=SimpleNamespace(device=torch.device('cuda:0'),CUDA=True,logger=None,norm=False,
                       pass_channel=True,downsample=2)
config.encoder_kwargs=dict(img_size=(32,32),patch_size=2,in_chans=3,embed_dims=[128,256],
                           depths=[2,4],num_heads=[4,8],C=32,window_size=2,mlp_ratio=4.,
                           qkv_bias=True,qk_scale=None,norm_layer=torch.nn.LayerNorm,patch_norm=True)
config.decoder_kwargs=dict(img_size=(32,32),embed_dims=[256,128],depths=[4,2],num_heads=[8,4],
                           C=32,window_size=2,mlp_ratio=4.,qkv_bias=True,qk_scale=None,
                           norm_layer=torch.nn.LayerNorm,patch_norm=True)
model=WITT(args,config).cuda()
optimizer=torch.optim.Adam(model.parameters(),lr=1e-4)
x=torch.rand(128,3,32,32,device='cuda')
times=[]
losses=[]
torch.cuda.reset_peak_memory_stats()
for step in range(8):
    torch.cuda.synchronize();t=time.perf_counter()
    optimizer.zero_grad(set_to_none=True)
    recon,cbr,snr,mse,loss=model(x,given_SNR=7)
    assert recon.shape==x.shape and abs(cbr-1/3)<1e-12
    assert torch.isfinite(loss)
    loss.backward()
    assert any(p.grad is not None for p in model.encoder.parameters())
    assert any(p.grad is not None for p in model.decoder.parameters())
    assert all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None)
    optimizer.step();torch.cuda.synchronize()
    times.append(time.perf_counter()-t);losses.append(loss.item())
commit=subprocess.check_output(['git','-c',f'safe.directory={repo}','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
result={'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'upstream_commit':commit,
        'model':'Author WITT CIFAR-10 model; C=32; AWGN','batch_size':128,'cbr':cbr,
        'parameters':sum(p.numel() for p in model.parameters()),'input_shape':list(x.shape),
        'step_seconds':times,'steady_step_seconds':sum(times[2:])/len(times[2:]),
        'peak_allocated_mib':torch.cuda.max_memory_allocated()/2**20,
        'synthetic_loss_values':losses,'torch':torch.__version__,
        'scope':'Synthetic model feasibility test only; no dataset training or PSNR replication'}
(root/'logs/witt-model-smoke.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
print('WITT_MODEL_FORWARD_BACKWARD_PASS')

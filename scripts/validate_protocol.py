"""Check physical AWGN SNR and two non-equivalent PSNR aggregations."""
from pathlib import Path
import json
import math
import sys

from witt_support import ROOT,build_model,write_json
from train_witt import validate
import torch

assert Path(sys.prefix).resolve()==(ROOT/'.conda').resolve()
config=json.loads((ROOT/'configs/witt_baseline_seed42.json').read_text(encoding='utf-8'))
torch.set_num_threads(4);torch.manual_seed(6001);torch.cuda.manual_seed_all(6001)
model=build_model(config,'WITT').eval()
features=torch.randn(64,64,32,device='cuda:0')
measurements=[]
for snr in [1,7,13]:
    with torch.no_grad():received=model.channel(features,snr)
    measured=10*torch.log10(features.square().mean()/(received-features).square().mean()).item()
    assert abs(measured-snr)<0.1,(snr,measured)
    measurements.append({'requested_snr_db':snr,'measured_real_domain_snr_db':measured})

class ConstantReconstruction(torch.nn.Module):
    def forward(self,x,given_SNR=None):
        y=torch.full_like(x,0.25)
        return y,1/3,given_SNR,torch.tensor(0.),torch.tensor(0.)

images=torch.stack([torch.zeros((3,32,32),dtype=torch.uint8),
                    torch.full((3,32,32),255,dtype=torch.uint8)])
cfg=dict(config,validation_snrs=[7],batch_size=2)
metrics=validate(ConstantReconstruction().to('cuda'),images,torch.tensor([0,1]),cfg)[0]
expected_mse=(0.25**2+0.75**2)/2
expected_aggregate=-10*math.log10(expected_mse)
expected_mean=(-10*math.log10(0.25**2)-10*math.log10(0.75**2))/2
assert abs(metrics['mse_0_1']-expected_mse)<1e-7
assert abs(metrics['psnr_from_mean_mse_db']-expected_aggregate)<1e-5
assert abs(metrics['mean_image_psnr_db']-expected_mean)<1e-5
assert abs(expected_aggregate-expected_mean)>1
write_json(ROOT/'logs/protocol-validation.json',{'awgn':measurements,'known_ground_truth_metrics':metrics,
           'expected_mse':expected_mse,'expected_psnr_from_mean_mse_db':expected_aggregate,
           'expected_mean_image_psnr_db':expected_mean,'scope':'Protocol unit checks, not model performance'})
print('AWGN_AND_PSNR_PROTOCOL_CHECKS_PASS')

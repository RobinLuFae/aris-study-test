"""Seeded CUDA forward/backward witness for the ARIS compute contract."""
from pathlib import Path
import datetime
import json
import sys
import time

root = Path(__file__).resolve().parents[1]
assert Path(sys.prefix).resolve() == (root/'.conda').resolve()

import torch
import torchvision

torch.set_num_threads(4)
torch.manual_seed(42)
assert torch.cuda.is_available(), 'CUDA is not available'
torch.cuda.manual_seed_all(42)
device = torch.device('cuda:0')
torch.backends.cudnn.benchmark = False
torch.backends.cudnn.deterministic = True

start = time.perf_counter()
conv = torch.nn.Sequential(torch.nn.Conv2d(3,16,3,padding=1), torch.nn.GELU(),
                           torch.nn.ConvTranspose2d(16,3,3,padding=1)).to(device)
attention = torch.nn.MultiheadAttention(64,4,batch_first=True).to(device)
optimizer = torch.optim.Adam([*conv.parameters(),*attention.parameters()],lr=1e-3)
image = torch.rand(8,3,32,32,device=device)
tokens = torch.randn(8,64,64,device=device)
before = conv[0].weight.detach().clone()
reconstruction = conv(image)
attended,_ = attention(tokens,tokens,tokens,need_weights=False)
loss = (reconstruction-image).square().mean()+attended.square().mean()
optimizer.zero_grad(set_to_none=True)
loss.backward()
assert torch.isfinite(loss)
assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in conv.parameters())
assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in attention.parameters())
optimizer.step()
torch.cuda.synchronize()
assert not torch.equal(before,conv[0].weight)
evidence = {
    'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'python_executable':sys.executable,'python':sys.version.split()[0],
    'torch':torch.__version__,'torchvision':torchvision.__version__,
    'cuda_runtime':torch.version.cuda,'device':torch.cuda.get_device_name(0),
    'capability':list(torch.cuda.get_device_capability(0)),
    'compiled_architectures':torch.cuda.get_arch_list(),
    'conv_output_shape':list(reconstruction.shape),'attention_output_shape':list(attended.shape),
    'loss':loss.item(),'finite_gradients':True,'optimizer_changed_parameters':True,
    'elapsed_seconds':time.perf_counter()-start,
    'peak_allocated_mib':torch.cuda.max_memory_allocated()/2**20,
    'scope':'Synthetic kernel-dispatch smoke, not a paper replication experiment',
}
(root/'logs/gpu-smoke.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(evidence,ensure_ascii=False,indent=2))
print('GPU_FORWARD_BACKWARD_PASS')

"""ARIS experiment-bridge implementation of the frozen WITT baseline plan."""
from pathlib import Path
import argparse
import datetime
import json
import math
import random
import shutil
import sys
import time

from witt_support import ROOT, build_model, upstream_version, write_json
from training_budget import TrainingWindow
import torch
import torchvision


def split_data(seed, validation_size):
    # Only the official training partition is opened here.
    dataset=torchvision.datasets.CIFAR10(str(ROOT/'data'),train=True,download=False)
    images=torch.from_numpy(dataset.data).permute(0,3,1,2).contiguous()
    split_file=ROOT/'data/splits'/f'cifar10_seed{seed}_val{validation_size}.json'
    if split_file.exists():
        split=json.loads(split_file.read_text(encoding='utf-8'))
    else:
        order=torch.randperm(len(dataset),generator=torch.Generator().manual_seed(seed)).tolist()
        split={'seed':seed,'official_partition':'train','validation':order[:validation_size],
               'train':order[validation_size:]}
        write_json(split_file,split)
    ti,vi=split['train'],split['validation']
    assert len(ti)==50000-validation_size and len(vi)==validation_size
    assert len(set(ti)|set(vi))==50000 and not set(ti)&set(vi)
    return images,torch.tensor(ti),torch.tensor(vi),split_file


@torch.no_grad()
def validate(model, images, indices, config):
    was_training=model.training;model.eval();result=[]
    try:
        # Isolate evaluation noise from the training random stream.
        with torch.random.fork_rng(devices=[torch.device(config['device']).index or 0]):
            for snr in config['validation_snrs']:
                torch.manual_seed(config['validation_noise_seed']+int(snr)*100)
                torch.cuda.manual_seed_all(config['validation_noise_seed']+int(snr)*100)
                sum_mse=0.;sum_psnr=0.;count=0
                for idx in indices.split(config['batch_size']):
                    x=images[idx].to(device=config['device'],dtype=torch.float32)/255.
                    y,cbr,_,_,_=model(x,given_SNR=snr)
                    if not torch.isfinite(y).all():
                        raise RuntimeError(f'Nonfinite reconstruction in validation at SNR {snr}')
                    per_image=(y.clamp(0,1)-x).square().flatten(1).mean(1)
                    sum_mse+=per_image.sum().item()
                    sum_psnr+=(-10*torch.log10(per_image.clamp_min(1e-12))).sum().item()
                    count+=x.shape[0]
                mse=sum_mse/count
                if not math.isfinite(mse) or not math.isfinite(sum_psnr):
                    raise RuntimeError(f'Nonfinite validation metric at SNR {snr}')
                result.append({'snr_db':snr,'images':count,'mse_0_1':mse,
                               'psnr_from_mean_mse_db':-10*math.log10(max(mse,1e-12)),
                               'mean_image_psnr_db':sum_psnr/count,'cbr':cbr})
    finally:
        model.train(was_training)
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--config',required=True)
    ap.add_argument('--sanity-steps',type=int,default=0)
    ap.add_argument('--resume',help='Continue a checkpoint into a new run_id; restore optimizer and RNGs')
    ap.add_argument('--budget-file',default=str(ROOT/'configs/training_window_2026-11-07.json'))
    ap.add_argument('--max-seconds',type=int,default=1200)
    args=ap.parse_args()
    assert Path(sys.prefix).resolve()==(ROOT/'.conda').resolve()
    config=json.loads(Path(args.config).read_text(encoding='utf-8'))
    budget=TrainingWindow(args.budget_file,args.max_seconds)
    resumed=None
    resume_index=None
    if args.resume:
        if args.sanity_steps:raise ValueError('Do not combine sanity override and resume')
        resumed=torch.load(args.resume,map_location='cpu',weights_only=True)
        previous=resumed['config']
        for key in set(config)|set(previous):
            if key not in ('run_id','stages') and config.get(key)!=previous.get(key):
                raise ValueError(f'Resume changes the training protocol: {key}')
        if config['run_id']==previous['run_id']:raise ValueError('Use a new run_id for each segment')
        if len(config['stages'])!=len(previous['stages']):raise ValueError('Preserve stage count')
        resume_index=next(i for i,s in enumerate(config['stages']) if s['name']==resumed['stage']['name'])
        for i,(new,old) in enumerate(zip(config['stages'],previous['stages'])):
            if any(new[k]!=old[k] for k in ('name','model','snrs')):
                raise ValueError('Preserve each stage protocol')
            if (i<len(config['stages'])-1 and new['steps']!=old['steps']) or new['steps']<old['steps']:
                raise ValueError('Only extend the final stage; do not shorten a planned stage')
        if resume_index==len(config['stages'])-1 and config['stages'][-1]['steps']<=resumed['stage_step']:
            raise ValueError('Resume has no remaining updates')
    if args.sanity_steps:
        config['run_id']='R000_witt_sanity_seed'+str(config['seed'])
        config['stages']=[dict(config['stages'][0],steps=args.sanity_steps)]
    run_dir=ROOT/'runs'/config['run_id']
    if (run_dir/'status.json').exists():
        raise RuntimeError(f'Run already exists; choose another run_id rather than overwrite: {run_dir}')
    run_dir.mkdir(parents=True,exist_ok=True)
    ckpts=ROOT/'checkpoints'/config['run_id'];ckpts.mkdir(parents=True,exist_ok=True)
    torch.set_num_threads(config['cpu_threads'])
    torch.manual_seed(config['seed']);torch.cuda.manual_seed_all(config['seed']);random.seed(config['seed'])
    torch.backends.cudnn.benchmark=False
    torch.backends.cudnn.deterministic=True
    images,train_ids,val_ids,split_file=split_data(config['split_seed'],config['validation_size'])
    version=upstream_version()
    assert not version['worktree_status'], 'Upstream model is modified'
    metadata={'config':config,'source':version,'split_file':str(split_file.relative_to(ROOT)),
              'train_images':len(train_ids),'validation_images':len(val_ids),
              'python':sys.version,'torch':torch.__version__,'torchvision':torchvision.__version__,
              'gpu':torch.cuda.get_device_name(),'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'argv':sys.argv,'test_partition_used':False}
    metadata['training_window']=budget.config
    if resumed:
        if resumed['source']!=version:raise ValueError('Author source differs from resume checkpoint')
        metadata['resume_checkpoint']=str(Path(args.resume).resolve())
        metadata['resumed_global_step']=resumed['global_step']
    write_json(run_dir/'metadata.json',metadata)
    source_dir=run_dir/'source';source_dir.mkdir(exist_ok=True)
    shutil.copy2(Path(__file__),source_dir/'train_witt.py')
    shutil.copy2(Path(__file__).with_name('witt_support.py'),source_dir/'witt_support.py')
    shutil.copy2(Path(__file__).with_name('training_budget.py'),source_dir/'training_budget.py')
    write_json(source_dir/'config.json',config)
    write_json(run_dir/'status.json',{'status':'running','global_step':0})
    model=build_model(config,config['stages'][0]['model'])
    sampler=torch.Generator().manual_seed(config['seed']+1000)
    order=torch.randperm(len(train_ids),generator=sampler);offset=0;epoch=0;global_step=0
    if resumed:
        model.load_state_dict(resumed['state_dict'],strict=True)
        order=resumed['sampler_order'];offset=resumed['sampler_offset'];epoch=resumed['sampler_epoch']
        sampler.set_state(resumed['sampler_rng']);global_step=resumed['global_step']
        torch.set_rng_state(resumed['torch_rng']);torch.cuda.set_rng_state_all(resumed['cuda_rng'])
        random.setstate(resumed['python_rng'])
    began=time.perf_counter();torch.cuda.reset_peak_memory_stats()
    log=(run_dir/'metrics.jsonl').open('a',encoding='utf-8',buffering=1)
    try:
        for stage_index,stage in enumerate(config['stages']):
            if resumed and stage_index<resume_index:continue
            is_resume=resumed is not None and stage_index==resume_index
            model.model=stage['model'];model.train()
            optimizer=torch.optim.Adam(model.parameters(),lr=config['learning_rate'])
            if is_resume:optimizer.load_state_dict(resumed['optimizer'])
            best=math.inf
            if is_resume:
                prior_best=Path(args.resume).parent/(stage['name']+'_best.pt')
                if prior_best.exists():
                    incumbent=torch.load(prior_best,map_location='cpu',weights_only=True)
                    best=sum(m['mse_0_1'] for m in incumbent['validation'])/len(incumbent['validation'])
                    shutil.copyfile(prior_best,ckpts/(stage['name']+'_best.pt'))
                    write_json(run_dir/(stage['name']+'_inherited_best.json'),
                        {'source':str(prior_best.resolve()),'global_step':incumbent['global_step'],
                         'selection_mean_mse_0_1':best,'scope':'Prior eligible incumbent retained unchanged'})
                    del incumbent
            start_step=resumed['stage_step'] if is_resume else 0
            for step in range(start_step+1,stage['steps']+1):
                if budget.remaining_wall()<=0:
                    raise RuntimeError('Approved absolute training deadline has expired')
                started=time.perf_counter()
                if offset+config['batch_size']>len(order):
                    order=torch.randperm(len(train_ids),generator=sampler);offset=0;epoch+=1
                indices=train_ids[order[offset:offset+config['batch_size']]];offset+=config['batch_size']
                x=images[indices].to(device=config['device'],dtype=torch.float32)/255.
                flips=torch.rand(x.shape[0],device=config['device'])<0.5
                x[flips]=x[flips].flip(-1)
                snr=random.choice(stage['snrs'])
                optimizer.zero_grad(set_to_none=True)
                _,cbr,_,_,loss=model(x,given_SNR=snr)
                if not torch.isfinite(loss):raise RuntimeError(f'Nonfinite loss at {global_step}')
                loss.backward()
                # An infinite maximum does not clip: it only checks the real gradient norm.
                grad_norm=torch.nn.utils.clip_grad_norm_(model.parameters(),max_norm=float('inf'),
                                                        error_if_nonfinite=True)
                optimizer.step();global_step+=1
                if global_step==1 or step%50==0:
                    row={'type':'train','stage':stage['name'],'step':step,'global_step':global_step,
                         'train_mse_0_1':loss.item()/255**2,'gradient_norm':grad_norm.item(),'snr_db':snr,'cbr':cbr,
                         'wall_seconds':time.perf_counter()-began,'step_seconds':time.perf_counter()-started,
                         'peak_allocated_mib':torch.cuda.max_memory_allocated()/2**20}
                    log.write(json.dumps(row)+'\n');print(json.dumps(row),flush=True)
                pause_requested=budget.should_checkpoint()
                if step%config['validation_every']==0 or step==stage['steps'] or pause_requested:
                    selection_eligible=step%config['validation_every']==0 or step==stage['steps']
                    metrics=validate(model,images,val_ids,config)
                    criterion=sum(r['mse_0_1'] for r in metrics)/len(metrics)
                    row={'type':'validation','stage':stage['name'],'step':step,'global_step':global_step,
                         'selection_eligible':selection_eligible,
                         'metrics':metrics,'selection_mean_mse_0_1':criterion,'wall_seconds':time.perf_counter()-began}
                    log.write(json.dumps(row)+'\n');print(json.dumps(row),flush=True)
                    checkpoint={'state_dict':model.state_dict(),'optimizer':optimizer.state_dict(),
                                'config':config,'stage':stage,'stage_step':step,'global_step':global_step,
                                'validation':metrics,'selection_eligible':selection_eligible,
                                'source':version,'sampler_order':order,
                                'sampler_offset':offset,'sampler_epoch':epoch,'sampler_rng':sampler.get_state(),
                                'torch_rng':torch.get_rng_state(),'cuda_rng':torch.cuda.get_rng_state_all(),
                                'python_rng':random.getstate()}
                    tmp=ckpts/'latest.tmp';torch.save(checkpoint,tmp);tmp.replace(ckpts/'latest.pt')
                    if selection_eligible and criterion<best:
                        best=criterion
                        tmp=ckpts/(stage['name']+'_best.tmp');torch.save(checkpoint,tmp)
                        tmp.replace(ckpts/(stage['name']+'_best.pt'))
                    if step==stage['steps']:
                        shutil.copyfile(ckpts/'latest.pt',ckpts/(stage['name']+'_final.pt'))
                    write_json(run_dir/'status.json',{'status':'running','stage':stage['name'],
                               'stage_step':step,'global_step':global_step,'elapsed_seconds':time.perf_counter()-began})
                    has_remaining=step<stage['steps'] or stage_index<len(config['stages'])-1
                    if budget.should_checkpoint() and has_remaining:
                        write_json(run_dir/'status.json',{'status':'paused','stage':stage['name'],
                            'stage_step':step,'global_step':global_step,'elapsed_seconds':time.perf_counter()-began,
                            'reason':'segment or approved daily training deadline','checkpoint':str(ckpts/'latest.pt')})
                        print('WITT_TRAINING_SEGMENT_PAUSED',flush=True)
                        return
        write_json(run_dir/'status.json',{'status':'completed','global_step':global_step,
                   'elapsed_seconds':time.perf_counter()-began,'peak_allocated_mib':torch.cuda.max_memory_allocated()/2**20})
        print('WITT_TRAINING_RUN_COMPLETED',flush=True)
    except BaseException as e:
        write_json(run_dir/'status.json',{'status':'failed','global_step':global_step,'error':repr(e)})
        raise
    finally:log.close()

if __name__=='__main__':main()

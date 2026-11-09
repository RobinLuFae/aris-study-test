"""Freeze one final test only after recomputing both actual validation gates."""
import argparse
import datetime
import json
import torch
from pathlib import Path
from analyze_paired_gate_results import analyze
from witt_support import ROOT, write_json


def main():
    ap = argparse.ArgumentParser()
    for name in ['dense','full','preparation','freeze','test-protocol']:ap.add_argument('--'+name, required=True)
    args = ap.parse_args(); read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
    if Path(args.freeze).exists() or Path(args.test_protocol).exists():raise ValueError('Freeze already exists')
    dense, full, prep = read(args.dense), read(args.full), read(args.preparation)
    dense_grid = sorted(set([1+i*.5 for i in range(25)]+[1.75,2.25,2.375,3.375,5.25,8.25,11.25]))
    full_grid = [1,1.5,2.375,3,7,12,12.5,13]
    for report, count, grid in ((dense,1000,dense_grid),(full,5000,full_grid)):
        if (report['status']!='completed' or report['split']!='validation' or report['test_partition_used'] or
            report['snrs']!=grid or report['noise_repeats']!=3 or len(report['evaluation_indices'])!=count or
            report['source_checkpoint']!=prep['source_checkpoint'] or report['preparation_id']!=prep['pilot_id']):
            raise ValueError('Wrong validation scope, source or frozen grid')
    if dense['evaluation_indices']!=full['evaluation_indices'][:1000]:raise ValueError('Subsets differ')
    dense_gate, full_gate = analyze(dense), analyze(full)
    if not dense_gate['engineering_gate']['passed'] or not full_gate['engineering_gate']['passed']:
        raise RuntimeError('Validation failed; test remains unopened')
    artifacts = {}
    for name in ('original','linear13'):
        item = next(v for v in prep['variants'] if v['variant']==name)
        path = (ROOT/item['artifact']).resolve()
        deployment = torch.load(path,map_location='cpu',weights_only=True)
        if (deployment['source_checkpoint']!=prep['source_checkpoint'] or
            deployment['source_global_step']!=full['source_global_step'] or
            deployment['source']!=full['source'] or deployment['variant']!=name or
            deployment['config']['batch_size']!=128):raise ValueError('Wrong deployment metadata')
        artifacts[name] = {'path':str(path),'bytes':path.stat().st_size}
        del deployment
    actual_reduction = 1-artifacts['linear13']['bytes']/artifacts['original']['bytes']
    if actual_reduction < .25:raise ValueError('Actual deployment files fail storage gate')
    test = {'run_id':'P004_R003_final_test','split':'test','samples':10000,'noise_repeats':3,
            'snrs':full_grid,'variants':['original','linear13'],'noise_seed_base':91001}
    freeze = {'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'source_checkpoint':prep['source_checkpoint'],'source_global_step':full['source_global_step'],
              'preparation_id':prep['pilot_id'],'artifacts':artifacts,'actual_storage_reduction':actual_reduction,
              'validation_gate':{'passed':True,'dense':dense_gate,'full':full_gate},'test_protocol':test,
              'data_order':'official test indices0..9999,noaugmentation','batch_size':128,
              'batch_membership':'consecutive128,final16,fixed acrossmethods/repeats',
              'policy':'One test of this frozen configuration;reportfailurewithouttest-drivenretuning.'}
    write_json(args.freeze,freeze)
    write_json(args.test_protocol,dict(test,freeze_file=str(Path(args.freeze).resolve())))
    print('FINAL_TEST_PROTOCOL_FROZEN_AFTER_VALIDATION_PASS')


if __name__=='__main__':main()

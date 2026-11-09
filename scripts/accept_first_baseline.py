"""Accept only measured functional reproduction, explicitly not paper-level parity."""
import json
import torch
from witt_support import ROOT, write_json

run = ROOT/'runs/R001_witt_baseline_seed42'
status = json.loads((run/'status.json').read_text())
evaluation = json.loads((ROOT/'results/R001_validation.json').read_text())
diagnostic = json.loads((ROOT/'results/R001_conditioning_diagnostic.json').read_text())
resume = json.loads((ROOT/'logs/resume-equivalence.json').read_text())
checkpoint = torch.load(ROOT/'checkpoints/R001_witt_baseline_seed42/adaptive_best.pt',
                        map_location='cpu', weights_only=True)
checks = {'training_completed': status['status']=='completed' and status['global_step']==8000,
          'evaluation_reproduces_saved_validation': evaluation['repeats'][0]['metrics']==checkpoint['validation'],
          'matched_forward_identical': diagnostic['matched_forward_max_abs_difference']==0,
          'diagnostic_complete': len(diagnostic['records'])==27,
          'resume_trajectory_identical': resume['passed'] and resume['max_parameter_abs_difference']==0,
          'validation_only': evaluation['split']=='validation' and not diagnostic['test_partition_used']}
report = {'checks': checks, 'passed': all(checks.values()),
          'accepted_scope': 'Seed42 finite-budget functional WITT reproduction and diagnostic integrity only',
          'paper_numerical_parity': 'NOT_ESTABLISHED', 'convergence': 'NOT_ESTABLISHED',
          'multiseed_or_test_results': 'NOT_EXECUTED',
          'next': 'Continue baseline convergence in bounded segments; generate hypotheses through ARIS pipeline.'}
write_json(ROOT/'logs/R001-functional-gate.json', report)
print(json.dumps(report, indent=2))
if not report['passed']:raise RuntimeError('Functional gate failed')

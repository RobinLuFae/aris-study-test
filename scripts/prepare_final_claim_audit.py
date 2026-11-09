"""Freeze declared primary inputs and prepare a new zero-context empirical audit."""
from pathlib import Path
import json
import hashlib

ROOT=Path(__file__).resolve().parents[1]
snapshot=ROOT/'_work/paper-final-20261109b'
folder=ROOT/'.aris/traces/paper-claim-audit/2026-11-09_run02'
folder.mkdir(parents=True,exist_ok=True)
primary=[]
for name in ['results/P001_gate_tables_R001_pilot.json','results/P001_gate_tables_R001_preparation.json',
             'results/P002_R003_dense_validation.json','results/P003_R003_full_validation.json',
             'results/P004_R003_final_test.json','results/P002_gate_tables_R003_preparation.json',
             'results/deployment_identity_receipt_20261109.json','logs/R003-checkpoint-selection.json',
             'logs/resume-equivalence.json','configs/environment-gpu.json',
             'configs/witt_baseline_seed42_segment3.json','configs/P004_R003_test_freeze.json',
             'data/splits/cifar10_seed20261107_val5000.json']:
    primary.append(ROOT/name)
for run in ['R001_witt_baseline_seed42','R002_witt_baseline_seed42_segment2','R003_witt_baseline_seed42_segment3']:
    primary.append(ROOT/'runs'/run/'metrics.jsonl')
    primary.extend((ROOT/'runs'/run/'source').glob('*.py'))
for run in ['P002_R003_dense_validation','P003_R003_full_validation','P004_R003_final_test']:
    primary.extend((ROOT/'runs'/run/'source').glob('*.py'))
    primary.extend((ROOT/'runs'/run/'source').glob('*.json'))
for name in ['net/network.py','net/encoder.py','net/decoder.py','net/channel.py','loss/distortion.py']:
    primary.append(ROOT/'baselines/upstream/WITT'/name)
for name in ['scripts/analyze_paired_gate_results.py','scripts/snr_gate_table.py','scripts/prepare_gate_tables.py']:
    primary.append(ROOT/name)
primary=list(dict.fromkeys(primary))
for p in primary:
    if not p.is_file():raise FileNotFoundError(p)
paper_files=[snapshot/'main.tex']+sorted((snapshot/'sections').glob('*.tex'))+sorted((snapshot/'figures').glob('*.tex'))
identities={str(p):'sha256:'+hashlib.sha256(p.read_bytes()).hexdigest() for p in paper_files+primary}
(folder/'declared_inputs.json').write_text(json.dumps(identities,indent=2)+'\n',encoding='utf-8')
scope=(ROOT/'.agents/skills/shared-references/review-scope-limits.md').read_text(encoding='utf-8').split('```')[1]
task=f'''Fresh ZERO-CONTEXT final paper-to-evidence audit. No previous review context.

Read the immutable manuscript snapshot {snapshot.as_posix()}: main.tex, sections/*.tex and figures/table_*.tex. Read the exact primary inputs listed in {folder.as_posix()}/declared_inputs.json. This list provides only raw results, configurations, recorded training/evaluation source, original model source and CPU artifact-inspection records. Source code is supplied solely as primary evidence for technical implementation claims (loss scale, initialization, source preservation, seed rules, normalization, freeze ordering, clamping); do not substitute an executor interpretation for measurement. Do NOT read project narratives, plans, acceptance contracts, handoffs, improvement logs or any previous reviewer/audit output. Those exclusions override general project recovery instructions for this audit.

Verify every numerical, comparative and empirical scope claim, including all table rows and captions. Extract the claim, locate exact primary evidence, check arithmetic and rounding, distinguish unique images / noise repetitions / training trajectories, scheduled selection versus cutoffs, pilot versus final checkpoint, knot versus interpolation conditions, complete-file versus parameter counts, loss scale, latency scope, and conditional intervals. Recompute from per-batch raw errors as needed using only project Conda Python. No GPU use, new training, or image/model inference. Raw dataset pixels are not needed. If reading a saved artifact is needed it must be CPU only.

The appendix also contains a self-reported AI-process account. Do not use its historical review claims as experimental evidence, and do not read prior verdicts to endorse it. Mark historical reviewer-event causality / authorship / bibliographic existence as outside this empirical/numerical audit, with those scope exclusions stated separately. Still audit any empirical number appearing there. This is not authorization to overlook a false scientific or numerical claim.

Return PASS/WARN/FAIL for empirical/numerical reporting, a compact per-claim ledger (group exact repetitions), material mismatches with precise fixes, and explicit scope exclusions/unknowns. Cover all three tables. Limit the written report to about 2,500 words; focus on evidence rather than repeating raw vectors. Save the complete raw response verbatim to {folder.as_posix()}/001-final.response.md and return the verdict. Same-family assurance remains provisional; requested model/effort do not prove serving identity.

{scope}
'''
(folder/'001-final.prompt.md').write_text(task,encoding='utf-8')
message=f'Follow the complete fresh zero-context final audit in {folder.as_posix()}/001-final.prompt.md. Read that task first, use only its declared primary inputs and immutable manuscript snapshot, preserve all exclusions, and save the complete raw response. Do not read previous reviews, project summaries or the acceptance contract.'
(folder/'001-final.request.json').write_text(json.dumps({'tool':'collaboration.spawn_agent','fork_turns':'none',
        'model':'gpt-6-astra','reasoning_effort':'ultra','prompt':message,'task_file':str(folder/'001-final.prompt.md')},indent=2)+'\n',encoding='utf-8')
print(message)

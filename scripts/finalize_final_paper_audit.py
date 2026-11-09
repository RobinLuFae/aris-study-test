"""Archive the actual final PASS, checking frozen inputs against the live paper."""
from pathlib import Path
from datetime import datetime,timezone
import json
import hashlib
import shutil
ROOT=Path(__file__).resolve().parents[1];paper=ROOT/'paper'
folder=ROOT/'.aris/traces/paper-claim-audit/2026-11-09_run02'
snapshot=ROOT/'_work/paper-final-20261109b'
raw=folder/'001-final.response.md';body=raw.read_text(encoding='utf-8')
if '**PASS for empirical and numerical reporting.**' not in body:raise ValueError('No final PASS')
declared=json.loads((folder/'declared_inputs.json').read_text(encoding='utf-8'))
identities={}
for name,expected in declared.items():
    path=Path(name);actual='sha256:'+hashlib.sha256(path.read_bytes()).hexdigest()
    if actual!=expected:raise ValueError('Declared input changed: '+name)
    if path.is_relative_to(snapshot):
        rel=path.relative_to(snapshot)
        if (paper/rel).read_bytes()!=path.read_bytes():raise ValueError('Live paper changed')
        identities[rel.as_posix()]=actual
    else:identities[str(path)]=actual
now=datetime.now(timezone.utc).isoformat();history=paper/'.aris/history/pre-final-20261109'
history.mkdir(parents=True,exist_ok=True)
for name in ('PAPER_CLAIM_AUDIT.json','PAPER_CLAIM_AUDIT.md'):
    if (paper/name).exists() and not (history/name).exists():shutil.copy2(paper/name,history/name)
result={'audit_skill':'paper-claim-audit','verdict':'PASS','reason_code':'all_empirical_numbers_match',
        'summary':'Three tables and quantitative/scientific-scope claims reconcile to frozen primary records.',
        'audited_input_hashes':identities,'trace_path':str(folder),'thread_id':'/root/paper_final_claim_audit_20261109b',
        'executor_model':'gpt-6','executor_family':'openai','reviewer_model':None,
        'requested_reviewer_model':'gpt-6-astra','reviewer_family':'openai','reviewer_reasoning':None,
        'requested_reasoning':'ultra','review_independence':'same-family','acceptance_status':'provisional',
        'generated_at':now,'details':{'material_mismatches':[],'immutable_input_verified':True,
        'live_manuscript_matches_snapshot':True,'raw_response':str(raw.relative_to(ROOT)),
        'scope_exclusions':['historical review-event causality','authorship','bibliographic existence',
                            'independent deployment-binary remeasurement','plot artwork','public-hosting verification'],
        'other_checks':'Separate citation reviewers verified eight entries; writing reviewers/executor inspected pages; executor separately verified deployment files and public hosting.'}}
(paper/'PAPER_CLAIM_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
(paper/'PAPER_CLAIM_AUDIT.md').write_text(body,encoding='utf-8')
meta={'agent_id':result['thread_id'],'backend':'codex','requested_reviewer_model':'gpt-6-astra',
      'reported_reviewer_model':None,'reviewer_model_source':'requested','requested_effort':'ultra',
      'reported_effort':None,'review_completed':True,'review_scope_complete':True,
      'review_positive':True,'verdict':'PASS','status':'completed','review_independence':'same-family',
      'acceptance_status':'provisional','recorded_at':now}
(folder/'001-final.meta.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
(folder/'run.meta.json').write_text(json.dumps({'skill':'paper-claim-audit','run_id':'2026-11-09_run02',
      'executor':'codex','executor_model':'gpt-6','reviewer_backend':'codex','project_dir':str(ROOT),
      'immutable_input':str(snapshot),'recorded_at':now},indent=2)+'\n',encoding='utf-8')
state=json.loads((paper/'PAPER_IMPROVEMENT_STATE.json').read_text(encoding='utf-8'))
state['final_empirical_audit']='PASS; fresh context and immutable manuscript'
(paper/'PAPER_IMPROVEMENT_STATE.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
print('FINAL_AUDIT_PASS_ARCHIVED; declared inputs and live manuscript unchanged')

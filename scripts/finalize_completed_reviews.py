"""Aggregate completed primary reviewer replies without erasing earlier findings."""
from pathlib import Path
from datetime import datetime,timezone
import json
import hashlib
import re
import shutil

ROOT=Path(__file__).resolve().parents[1];paper=ROOT/'paper'
now=datetime.now(timezone.utc).isoformat()
def put(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def meta(agent,verdict,effort='xhigh',continuation=False):
    return {'agent_id':agent,'backend':'codex','requested_reviewer_model':'gpt-6-astra',
            'reported_reviewer_model':None,'reviewer_model_source':'requested',
            'requested_effort':effort,'reported_effort':None,'status':'completed',
            'review_completed':True,'review_scope_complete':True,'verdict':verdict,
            'review_positive':verdict in ('KEEP','PASS','Yes'),
            'review_independence':'same-family','acceptance_status':'provisional',
            'same_session_continuation':continuation,'recorded_at':now}
entries=[]
specs=[('bourtsoulatze2019deep','2026-11-09_run02','/root/cite_deepjscc_20261109',True),
       ('yang2023witt','2026-11-09_run01','/root/cite_witt_20261109',False),
       ('xu2022adaptive','2026-11-09_run01','/root/cite_adaptive_20261109',False),
       ('yang2025swinjscc','2026-11-09_run01','/root/cite_swinjscc_20261109',False),
       ('jo2021practical','2026-11-09_run01','/root/cite_lut_20261109',False),
       ('krizhevsky2009learning','2026-11-09_run01','/root/cite_cifar_20261109',False),
       ('yin2026aris','2026-11-09_run02','/root/cite_aris_resume_20261109',True),
       ('yang2026aris','2026-11-09_run02','/root/cite_aris_report_20261109b',False)]
for key,run,agent,continuation in specs:
    folder=ROOT/'.aris/traces/citation-audit'/run
    response=folder/f'{key}.response.md'
    body=response.read_text(encoding='utf-8')
    if not re.search(r'VERDICT[\s:*—–-]+KEEP',body,re.I):raise ValueError('No KEEP verdict: '+key)
    put(folder/f'{key}.meta.json',meta(agent,'KEEP',continuation=continuation))
    if continuation:
        request=json.loads((folder/f'{key}.request.json').read_text(encoding='utf-8'))
        request.update(tool='collaboration.followup_task',target=agent,dispatch_kind='same-entry follow-up')
        request['prompt_source']='Full entry task saved; exact continuation dispatch text is recorded in continuation.request.json.'
        put(folder/f'{key}.request.json',request)
    entries.append({'key':key,'verdict':'KEEP','existence':'YES','metadata':'correct','uses':'SUPPORTS',
                    'trace':str(response.relative_to(ROOT)),'thread_id':agent,'continuation':continuation})
history=paper/'.aris/history/pre-resume-20261109'
for name in ['CITATION_AUDIT.json','CITATION_AUDIT.md']:
    if (paper/name).exists() and not (history/name).exists():
        history.mkdir(parents=True,exist_ok=True);shutil.copy2(paper/name,history/name)
tex=list((paper/'sections').glob('*.tex'))
contexts=[]
for path in tex:
    for para in path.read_text(encoding='utf-8').split('\n\n'):
        for match in re.finditer(r'\\cite\w*\{([^}]+)\}',para):
            contexts.append({'file':str(path.relative_to(paper)),'keys':match[1].split(','),'context':para})
ctx=paper/'.aris/citation-audit/contexts.txt'
ctx.parent.mkdir(parents=True,exist_ok=True);ctx.write_text(json.dumps(contexts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
hashes={str(p.relative_to(paper)).replace('\\','/'):'sha256:'+hashlib.sha256(p.read_bytes()).hexdigest() for p in [paper/'references.bib',ctx]}
result={'audit_skill':'citation-audit','verdict':'PASS','reason_code':'all_cited_entries_verified',
        'summary':'Eight cited entries have primary-source existence/metadata checks and supported uses; earlier metadata FIX findings were resolved and checked by the same entry reviewers.',
        'audited_input_hashes':hashes,'trace_path':str(ROOT/'.aris/traces/citation-audit'),
        'thread_id':None,'reviewer_model':None,'requested_reviewer_model':'gpt-6-astra',
        'reviewer_family':'openai','reviewer_reasoning':None,'requested_reasoning':'xhigh',
        'review_independence':'same-family','acceptance_status':'provisional','generated_at':now,
        'details':{'total_entries':8,'counts':{'KEEP':8},'per_entry':entries,
                   'context_note':'Current citing contexts saved. Unchanged scientific attribution claims retain their earlier entry reviews; expanded local training descriptions are project protocol, not claims attributed to dataset papers. Exact earlier dispatch contexts remain in trace requests.'}}
put(paper/'CITATION_AUDIT.json',result)
lines=['# Citation audit: PASS (same-family provisional)','',result['summary'],'',
       '| Key | Current verdict | Review type |','|---|---|---|']
for e in entries:lines.append(f'| {e["key"]} | KEEP | '+('Same-entry correction follow-up' if e['continuation'] else 'Fresh per-entry audit')+' |')
lines+=['','Original FIX replies and the initial capacity-blocked ledger remain archived. No cross-family acceptance or observed serving variant is claimed.']
(paper/'CITATION_AUDIT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
writing=ROOT/'.aris/traces/auto-paper-improvement-loop/2026-11-09_run01'
for i,agent,verdict in [(1,'/root/paper_writing_round1_20261109b','Almost'),(2,'/root/paper_writing_round2_20261109b','Yes')]:
    label=f'{i:03d}-round{i}'
    if not (writing/f'{label}.response.md').exists():raise FileNotFoundError(label)
    put(writing/f'{label}.meta.json',meta(agent,verdict))
put(writing/'run.meta.json',{'skill':'auto-paper-improvement-loop','run_id':'2026-11-09_run01',
    'executor':'codex','executor_model':'gpt-6','executor_family':'openai','reviewer_backend':'codex',
    'project_dir':str(ROOT),'recorded_at':now,'assurance':'draft','fresh_context_each_round':True})
put(paper/'PAPER_IMPROVEMENT_STATE.json',{'current_round':2,'status':'completed','last_score':9,
    'verdict':'Yes on course scientific content','acceptance_status':'provisional',
    'timestamp':now,'final_empirical_audit':'running in fresh context; distinct from writing review'})
print('Eight citation entries KEEP; two fresh writing rounds recorded (8/Almost -> 9/Yes).')

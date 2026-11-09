"""Aggregate six completed per-entry reviews, keeping the seventh explicitly blocked."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
paper=ROOT/'paper';folder=ROOT/'.aris/traces/citation-audit/2026-11-09_run01'
agents={'bourtsoulatze2019deep':'/root/cite_deepjscc_20261109',
        'yang2023witt':'/root/cite_witt_20261109','xu2022adaptive':'/root/cite_adaptive_20261109',
        'yang2025swinjscc':'/root/cite_swinjscc_20261109','jo2021practical':'/root/cite_lut_20261109',
        'krizhevsky2009learning':'/root/cite_cifar_20261109'}
entries=[]
for key,agent in agents.items():
    raw=folder/f'{key}.response.md'
    if not raw.exists():raise FileNotFoundError(raw)
    verdict='FIX' if key=='bourtsoulatze2019deep' else 'KEEP'
    meta={'agent_id':agent,'status':'completed','requested_reviewer_model':'gpt-6-astra',
          'reported_reviewer_model':None,'reviewer_model_source':'requested',
          'requested_effort':'xhigh','reported_effort':None,'review_completed':True,
          'review_scope_complete':True,'verdict':verdict,'review_positive':verdict=='KEEP',
          'review_independence':'same-family','acceptance_status':'provisional'}
    (folder/f'{key}.meta.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    entries.append({'key':key,'verdict':verdict,'existence':'YES','contexts':'SUPPORTS',
                    'response':str(raw.relative_to(ROOT)),
                    'fix_status':'Author spelling corrected by executor from primary-source-supported reviewer recommendation; not re-reviewed.' if verdict=='FIX' else None})
entries.append({'key':'yin2026aris','verdict':'REVIEW_UNAVAILABLE',
                'reason':'Fresh native dispatch failed before execution: agent thread limit reached',
                'executor_primary_lookup':'Official GitHub repository was opened; this is not an independent review.'})
inputs=[paper/'references.bib',paper/'.aris/citation-audit/contexts.txt']+sorted((paper/'sections').glob('*.tex'))
hashes={str(p.relative_to(paper)).replace('\\','/'):'sha256:'+hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
result={'audit_skill':'citation-audit','verdict':'BLOCKED','reason_code':'fresh_reviewer_capacity',
        'summary':'Six scientific entries reviewed with supported contexts; one metadata fix applied; seventh software-entry review unavailable.',
        'audited_input_hashes':hashes,'trace_path':str(folder),'thread_id':None,
        'requested_reviewer_model':'gpt-6-astra','reviewer_model':None,'reviewer_family':'openai',
        'reviewer_reasoning':None,'requested_reasoning':'xhigh','review_independence':'same-family',
        'acceptance_status':'provisional','generated_at':datetime.now(timezone.utc).isoformat(),
        'details':{'total_entries':7,'counts':{'KEEP':5,'FIX':1,'REVIEW_UNAVAILABLE':1},
                   'per_entry':entries,'input_note':'File identities recorded at aggregation; six exact per-entry dispatch contexts remain in request/prompt files. Final metadata fixes have not been re-reviewed.'}}
(paper/'CITATION_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
lines=['# Citation audit: BLOCKED (review capacity)','',result['summary'],'',
       '| Entry | Actual review | Status |','|---|---|---|']
for e in entries:
    lines.append(f'| {e["key"]} | {e["verdict"]} | '+('Metadata fix applied; follow-up pending.' if e['verdict']=='FIX' else 'Pending fresh software-entry review.' if e['verdict']=='REVIEW_UNAVAILABLE' else 'Existence, metadata and cited contexts supported.')+' |')
lines+=['','Raw per-entry responses and sources are preserved under `.aris/traces/citation-audit/2026-11-09_run01/`.',
        'Same-family reviews remain provisional. No unavailable review is counted as a pass.',
        'The DeepJSCC correction restores Gündüz and the reviewer-preferred compound family name Burth Kurka. Raw publisher BibTeX is preserved separately.']
(paper/'CITATION_AUDIT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(result['summary'])

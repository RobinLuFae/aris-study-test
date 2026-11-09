"""Preserve the real WARN review and explicitly distinguish subsequent executor fixes."""
from pathlib import Path
from datetime import datetime,timezone
import json
import hashlib
from collections import Counter

ROOT=Path(__file__).resolve().parents[1];paper=ROOT/'paper'
folder=ROOT/'.aris/traces/paper-claim-audit/2026-11-09_run01'
raw=folder/'001-audit.response.md'
text=raw.read_text(encoding='utf-8')
statuses={'exact_match','rounding_ok','ambiguous_mapping','missing_evidence','config_mismatch',
          'aggregation_mismatch','number_mismatch','scope_overclaim','unsupported_claim'}
claims=[]
for line in text.splitlines():
    if not line.startswith('|'):continue
    row=[v.strip() for v in line.split('|')]
    if len(row)>4 and row[-2] in statuses:
        claims.append({'location':row[1],'claim':row[2],'evidence':row[3],
                       'status':row[-2]})
counts=Counter(c['status'] for c in claims)
now=datetime.now(timezone.utc).isoformat()
files=[paper/'main.tex']+sorted((paper/'sections').glob('*.tex'))+sorted((paper/'figures').glob('table_*.tex'))
identity={str(p.relative_to(paper)).replace('\\','/'):'sha256:'+hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
meta={'tool':'collaboration.spawn_agent','agent_id':'/root/paper_claim_audit_20261109',
      'requested_reviewer_model':'gpt-6-astra','reported_reviewer_model':None,
      'reviewer_model_source':'requested','requested_effort':'ultra','reported_effort':None,
      'review_completed':True,'review_scope_complete':True,'verdict':'WARN',
      'review_positive':False,'review_independence':'same-family','acceptance_status':'provisional',
      'generated_at':now}
(folder/'001-audit.meta.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
request={'tool':'collaboration.spawn_agent','model':'gpt-6-astra','reasoning_effort':'ultra','fork_turns':'none',
         'prompt':'Follow the full zero-context paper-to-evidence audit in '+(folder/'001-audit.prompt.md').as_posix()+'. Read that task first. Preserve its input exclusions and save your complete raw response to the specified path. Do not read project summaries, plans, the acceptance contract, or earlier reviewers.',
         'secondary_message':'Quota-management update: the account five-hour window is now 67% used; the user requires saving and stopping near 90% used. Please finish the current audit from the checks already performed, save your full raw findings promptly, and avoid broadening into additional investigation. Record any incomplete coverage explicitly. No new experiment or inference.'}
(folder/'001-audit.request.json').write_text(json.dumps(request,indent=2)+'\n',encoding='utf-8')
result={'audit_skill':'paper-claim-audit','verdict':'WARN','reason_code':'wording_fixes_and_provenance_gaps',
        'summary':'Raw numerical results reconcile; initial headline rounding and pixel-unit wording required correction, and restricted evidence omitted implementation/history provenance.',
        'audited_input_hashes':{},'trace_path':str(folder),'thread_id':meta['agent_id'],
        'executor_model':'gpt-6','executor_family':'openai','reviewer_model':None,
        'requested_reviewer_model':'gpt-6-astra','reviewer_family':'openai','reviewer_reasoning':None,
        'requested_reasoning':'ultra','review_independence':'same-family','acceptance_status':'provisional',
        'generated_at':now,'details':{'total_claim_rows':len(claims),'counts':dict(counts),'claims':claims,
        'mismatches':[c for c in claims if c['status'] not in ('exact_match','rounding_ok')],
        'provenance_note':'Reviewer read the initial draft. Small executor corrections were applied while it finished its findings. No dispatch-time immutable source snapshot exists; current source identities below are NOT claimed as the originally audited input set. A fresh post-edit audit is pending.',
        'post_edit_source_identities':identity,
        'post_review_fixes':['Direct rounding 0.000186 dB in abstract/introduction/conclusion',
                            '3072 scalar RGB values, rather than 3072 spatial pixels',
                            'Bootstrap scope explicitly P002-P004',
                            'Source-snapshot statement limited to P002-P004'],
        'new_executor_evidence':'results/deployment_identity_receipt_20261109.json; CPU only, no inference; not yet independently reviewed'}}
(paper/'PAPER_CLAIM_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
report='''# Paper-to-evidence audit: WARN

The fresh reviewer independently reproduced the core empirical results, checkpoint choice, validation admission, all 18 result-table rows and the 48 primary SNR-cell interval pairs. The complete raw review is retained under `.aris/traces/paper-claim-audit/2026-11-09_run01/001-audit.response.md`.

The initial draft double-rounded the headline maximum loss and called 3,072 RGB scalar channel values “pixels.” Both have been corrected by the executor. The bootstrap paragraph now specifies P002–P004, and the appendix limits the source-snapshot statement to those three runs. A CPU inspection additionally records 223 identical retained tensors and absence of optimizer state in `results/deployment_identity_receipt_20261109.json`.

Some implementation and historical-review assertions lacked provenance within the deliberately restricted audit input set. Existing raw source, configuration and review records remain available in the workspace. These exceptions must be checked rather than automatically treated as false or silently accepted.

**Status remains WARN.** The small source corrections overlapped the end of the initial audit; no dispatch-time immutable source snapshot was captured. A fresh post-edit audit is pending because native reviewer thread capacity is exhausted. Current source identities are recorded separately, not misrepresented as the initial audited input identities. Same-family review remains provisional.
'''
(paper/'PAPER_CLAIM_AUDIT.md').write_text(report,encoding='utf-8')
print('Archived WARN:',len(claims),'claim rows; post-edit fresh audit pending.')

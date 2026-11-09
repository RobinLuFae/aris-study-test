"""Archive actual review provenance; missing historic prompts remain explicitly missing."""
from pathlib import Path
from datetime import datetime, timezone
import json

ROOT=Path(__file__).resolve().parents[1]
now=datetime.now(timezone.utc).isoformat()
route={'backend':'codex','host':'codex','source':'host-default','model':'gpt-6-astra',
       'effort':'xhigh','transport':'native','fresh_tool':'spawn_agent'}

def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

historic=[('auto-review-loop','2026-11-08_run01','/root/final_evidence_audit','ultra',
           [('001-joint-review','WARN'),('002-final','PASS')]),
          ('paper-writing','2026-11-08_contract','/root/paper_contract_review','xhigh',
           [('001-contract','CONTRACT_ACCEPTED: no'),('002-contract','CONTRACT_ACCEPTED: yes')])]
for skill,run,agent,effort,calls in historic:
    folder=ROOT/'.aris/traces'/skill/run
    write(folder/'run.meta.json',{'skill':skill,'run_id':run,'executor':'codex',
          'executor_model':'gpt-6','executor_family':'openai','reviewer_backend':'codex',
          'project_dir':str(ROOT),'archived_at':now,'historical_recovery':True,
          'note':'Existing raw responses retained. Exact historical dispatch prompts unavailable here; not reconstructed as originals.'})
    for label,verdict in calls:
        if not (folder/f'{label}.response.md').exists():raise FileNotFoundError(label)
        write(folder/f'{label}.request.json',{'tool':'collaboration.spawn_agent' if label.startswith('001') else 'collaboration.followup_task',
              'agent_id':agent,'backend':'codex','requested_reviewer_model':'gpt-6-astra',
              'requested_effort':effort,'prompt':None,'prompt_status':'unrecovered',
              'raw_response_preserved':True,'archived_at':now})
        write(folder/f'{label}.meta.json',{'agent_id':agent,'requested_reviewer_model':'gpt-6-astra',
              'reported_reviewer_model':None,'reviewer_model_source':'requested',
              'requested_effort':effort,'reported_effort':None,'review_completed':True,
              'review_scope_complete':True,'verdict':verdict,'status':'completed',
              'review_independence':'same-family','acceptance_status':'provisional',
              'trace_completeness':'raw response present; exact dispatch prompt unrecovered',
              'review_positive':verdict in ('PASS','CONTRACT_ACCEPTED: yes'),'archived_at':now})

current=[('paper-figure','2026-11-09_run01','001-visual','/root/paper_figure_review_20261109','WARN','xhigh')]
for skill,run,label,agent,verdict,effort in current:
    folder=ROOT/'.aris/traces'/skill/run
    write(folder/'run.meta.json',{'skill':skill,'run_id':run,'executor':'codex','executor_model':'gpt-6',
          'executor_family':'openai','reviewer_backend':'codex','route':route,'project_dir':str(ROOT)})
    write(folder/f'{label}.request.json',{'tool':'collaboration.spawn_agent','model':'gpt-6-astra','effort':effort,
          'fork_turns':'none','prompt_file':str((folder/f'{label}.prompt.md').relative_to(ROOT)),
          'prompt':f'Follow the full review task in {folder.as_posix()}/{label}.prompt.md. Read that file first, then the actual evidence and rendered figures. Save the complete final review to the specified response path. Do not run model inference or modify research outputs. Return your verdict and what you actually inspected.',
          'exact_dispatch_wording':False,'note':'Task file is exact; dispatch wrapper transcribed from current session with a minor wording difference. See task message in host history.'})
    write(folder/f'{label}.meta.json',{'agent_id':agent,'requested_reviewer_model':'gpt-6-astra',
          'reported_reviewer_model':None,'reviewer_model_source':'requested','requested_effort':effort,
          'review_completed':True,'review_scope_complete':True,'verdict':verdict,
          'review_independence':'same-family','acceptance_status':'provisional','review_positive':False})
print('Review provenance archived; historical prompt gaps explicitly retained.')

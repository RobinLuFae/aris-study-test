"""Prepare a context-naive, artifact-grounded ARIS writing-review slot."""
from pathlib import Path
import argparse
import json

ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--round',type=int,required=True);args=ap.parse_args()
round_id=args.round
snapshot=ROOT/'_work'/f'paper-review-20261109-round{round_id}'
folder=ROOT/'.aris/traces/auto-paper-improvement-loop/2026-11-09_run01'
folder.mkdir(parents=True,exist_ok=True)
label=f'{round_id:03d}-round{round_id}'
scope=(ROOT/'.agents/skills/shared-references/review-scope-limits.md').read_text(encoding='utf-8').split('```')[1]
body=f'''Fresh independent paper-writing review, with no prior review context.

Read ONLY the current paper snapshot {snapshot.as_posix()}: main.tex, sections/*.tex, figures/*.tex, references.bib, main.pdf, and preview/page-*.png. Inspect all rendered pages through the image viewer as well as the source. A text-only read cannot complete visual review. You may read the original raw results/configurations in {ROOT.as_posix()}/results and configs if needed for checking a claim. Do not read project narratives, plans, earlier audits, earlier review outputs, improvement logs or handoffs. Do not edit manuscript/evidence. Save the full final response verbatim as {folder.as_posix()}/{label}.response.md.

Target: a bounded empirical COURSE paper using official CVPR 2026 format, not a claim of CVPR research acceptance. Give two clearly separated judgments: (a) course writing/readiness score 1–10 and Yes/Almost/No; (b) top-venue original-research assessment. The latter does not expand the authorized course scope or require a new experimental campaign.

Review every section for self-contained method, notation, scientific precision, evidence/claim alignment, writing structure, placement of generic limitations, units, appropriate precision, references, table/figure/caption alignment and visual presentation. Judge calibration in BOTH directions: keep supported advantages direct and retain unfavorable measured results. Do not add defensive boilerplate. Flag progress-report narrative, stacked hedges, ambiguity about what was trained/compiled/tested, unsupported novelty and latency claims. Tone fixes must preserve numbers, scope, modality and comparison direction. Keep the strongest genuine result clear in the title/abstract/introduction and make every experiment support that result. Avoid inventing missing problems or requiring decorative figures.

Output: overall course score/verdict; summary; ranked strengths; CRITICAL/MAJOR/MINOR weaknesses with concrete fixes; per-section findings; missing references if actually needed; visual review (explicit pages opened); top-venue assessment; completion/identity limitations. Prefer concise, actionable findings over rewriting the entire paper. State plainly when a section is correct. Same-family review remains provisional; requested model/effort are not evidence of the serving variant.

{scope}
'''
(folder/f'{label}.prompt.md').write_text(body,encoding='utf-8')
message=f'Follow the complete fresh writing-review task in {folder.as_posix()}/{label}.prompt.md. Read the task first, inspect the immutable current paper snapshot and all page images, and save the full raw response to the specified path. Do not inspect prior reviews or modify the paper.'
request={'tool':'collaboration.spawn_agent','fork_turns':'none','model':'gpt-6-astra','reasoning_effort':'xhigh',
         'prompt':message,'task_file':str((folder/f'{label}.prompt.md').relative_to(ROOT)),
         'input_snapshot':str(snapshot),'input_manifest':str(snapshot/'SNAPSHOT_INPUTS.json')}
(folder/f'{label}.request.json').write_text(json.dumps(request,indent=2)+'\n',encoding='utf-8')
print(message)

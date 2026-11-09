"""Prepare exact prompts and citation contexts from the current source draft."""
from pathlib import Path
import json
import re
import argparse

ap=argparse.ArgumentParser()
ap.add_argument('--run',default='2026-11-09_run01')
ap.add_argument('--keys',nargs='*')
args=ap.parse_args()

ROOT=Path(__file__).resolve().parents[1]
paper=ROOT/'paper'
scope=(ROOT/'.agents/skills/shared-references/review-scope-limits.md').read_text(encoding='utf-8').split('```')[1]
texfiles=[paper/'main.tex']+sorted((paper/'sections').glob('*.tex'))+sorted((paper/'figures').glob('*.tex'))
bib=(paper/'references.bib').read_text(encoding='utf-8')
matches=list(re.finditer(r'@\w+\{([^,]+),',bib))
folder=ROOT/'.aris/traces/citation-audit'/args.run
folder.mkdir(parents=True,exist_ok=True)
contexts=[]
for n,match in enumerate(matches):
    key=match[1];entry=bib[match.start():matches[n+1].start() if n+1<len(matches) else len(bib)]
    if args.keys and key not in args.keys:continue
    if (folder/f'{key}.request.json').exists():raise ValueError('Preserve old dispatch records; choose a new run directory')
    uses=[]
    for f in texfiles:
        text=f.read_text(encoding='utf-8')
        for para in text.split('\n\n'):
            if any(key in m[1].split(',') for m in re.finditer(r'\\cite\w*\{([^}]+)\}',para)):
                uses.append({'file':str(f.relative_to(paper)),'context':para})
    contexts.append({'key':key,'uses':uses})
    prompt=f'''Fresh per-entry citation audit. Project: {ROOT.as_posix()}. Review ONLY the entry and its cited contexts below. Use actual web lookup of primary publisher/author/CVF/arXiv sources. Verify existence, all author names/order, title/year/venue/DOI, and support for every use. Do not rely on executor conclusions. Return EXISTENCE YES/NO/UNCERTAIN; METADATA correct/wrong with correction; per-use SUPPORTS/WEAK/WRONG; VERDICT KEEP/FIX/REPLACE/REMOVE. If unable to verify online, say UNCERTAIN. Include verifying URLs. Record access limits. Do not modify bibliography or manuscript. Save the full final response verbatim to {folder.as_posix()}/{key}.response.md and return it. Same-family assurance is provisional, requested model identity is not observed proof.

ENTRY:\n{entry}\nUSES:\n{json.dumps(uses,ensure_ascii=False,indent=2)}\n{scope}'''
    (folder/f'{key}.prompt.md').write_text(prompt,encoding='utf-8')
    request={'tool':'collaboration.spawn_agent','backend':'codex','model':'gpt-6-astra','effort':'xhigh',
             'fork_turns':'none','prompt_file':str((folder/f'{key}.prompt.md').relative_to(ROOT)),
             'prompt':f'Follow the full fresh citation-audit task in {folder.as_posix()}/{key}.prompt.md. Read that task first, verify the entry through actual primary-source web lookup, and save the complete raw response to its specified path. Do not inspect unrelated project summaries or other reviewers. Return the verdict and verified sources.'}
    (folder/f'{key}.request.json').write_text(json.dumps(request,indent=2),encoding='utf-8')
target=paper/'.aris/citation-audit';target.mkdir(parents=True,exist_ok=True)
(target/'contexts.txt').write_text(json.dumps(contexts,ensure_ascii=False,indent=2),encoding='utf-8')
print('Prepared',len(contexts),'fresh per-entry tasks.')

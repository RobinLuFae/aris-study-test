"""Allowlisted local submission bundle: no dataset, weights, environment or tokens."""
from pathlib import Path
import json
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/submission'
OUT.mkdir(parents=True,exist_ok=True)
files=set()
for skill,run in [('paper-claim-audit','2026-11-09_run01'),('citation-audit','2026-11-09_run01'),
                  ('paper-figure','2026-11-09_run01'),('auto-review-loop','2026-11-08_run01'),
                  ('research-refine','2026-11-08_run01'),('research-review','2026-11-08_run01')]:
    files.update((ROOT/'.aris/traces'/skill/run).glob('*.response.md'))
for base,pattern in [('scripts','*.py'),('scripts','*.ps1'),('configs','*.json'),
                     ('results','*.json'),('paper','*.tex'),('paper','*.bib'),
                     ('paper','*.sty'),('paper','*.bst'),('paper','main.pdf'),
                     ('paper/sections','*.tex'),('paper/figures','*.py'),
                     ('paper/figures','*.tex'),('paper/figures','*.json'),
                     ('paper/figures','*.pdf'),('paper/figures','*.png'),
                     ('notes','*.md'),('data/splits','*.json')]:
    files.update((ROOT/base).glob(pattern))
for name in ['CODE_README.md','THIRD_PARTY_NOTICES.md','GPU_ENVIRONMENT.md',
             'PAPER_PLAN.md','PAPER_ACCEPTANCE_CONTRACT.md',
             'refine-logs/EXPERIMENT_PLAN.md','refine-logs/EXPERIMENT_TRACKER.md',
             'refine-logs/EXPERIMENT_RESULTS.md','paper/PAPER_CLAIM_AUDIT.json',
             'paper/PAPER_CLAIM_AUDIT.md','paper/CITATION_AUDIT.json','paper/CITATION_AUDIT.md',
             'paper/PAPER_IMPROVEMENT_LOG.md','paper/ACCEPTANCE_CHECK.md',
             'logs/R003-checkpoint-selection.json','logs/resume-equivalence.json',
             'third_party/ARIS-LICENSE']:
    if (ROOT/name).is_file():files.add(ROOT/name)
archive=OUT/'witt_snr_gate_course_source_results.zip'
manifest={'scope':'local code/results/paper; no weights, dataset pixels or environments',
          'public_url':None,'files':[str(p.relative_to(ROOT)).replace('\\','/') for p in sorted(files)],
          'file_count':len(files),'source_bytes':sum(p.stat().st_size for p in files)}
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(files):
        name=str(p.relative_to(ROOT)).replace('\\','/')
        z.write(p,'AIRS/'+name)
    z.writestr('AIRS/PACKAGE_MANIFEST.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(archive) as z:
    bad=z.testzip()
    if bad:raise ValueError('Archive CRC failed: '+bad)
(OUT/'PACKAGE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'files':len(files),'crc':'PASS'}))

"""Stage the reviewed allowlist into the user's existing empty repository."""
from pathlib import Path
import json
import shutil
import re

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'publication/aris-study-test'
if not (DEST/'.git').is_dir():raise RuntimeError('Clone the specified user repository first')
manifest=json.loads((ROOT/'output/submission/PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
for name in manifest['files']:
    src=ROOT/name;target=DEST/name
    if not src.is_file() or not target.resolve().is_relative_to(DEST.resolve()):raise ValueError(name)
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,target)
readme=(ROOT/'CODE_README.md').read_text(encoding='utf-8')
readme=readme.replace('Public hosting is pending until the user supplies and authorizes the target repository.',
    'Target repository: https://github.com/RobinLuFae/aris-study-test. The included paper remains a course draft awaiting final independent review and student author details.')
readme+='''
## Review and course-submission status

This is a research-course paper with real measured results and an AI-process record. Two fresh writing reviews were completed; eight cited references were verified; the final empirical/numerical audit returned PASS. All semantic reviews remain same-family and provisional, and course readiness is separate from top-venue original-research acceptance. Author and institution fields intentionally use placeholders at the student's request. The student will write personal reflections after reading `notes/ARIS语义通信研究全过程记录.md`. See the current audit records and `paper/ACCEPTANCE_CHECK.md`.

The repository intentionally excludes author source repositories, checkpoint binaries, dataset pixels, Python environments and credentials. Original raw records retain historical absolute machine paths; the reproduction guide explains new-machine use. No credentials are embedded in those paths.
'''
(DEST/'README.md').write_text(readme,encoding='utf-8')
(DEST/'.gitignore').write_text('''.conda/
__pycache__/
*.pyc
.env
*.key
downloads/
checkpoints/
data/cifar-10-batches-py/
baselines/upstream/
templates/upstream/
third_party/texmf/
output/
paper/preview/
paper/*.aux
paper/*.log
paper/*.bbl
paper/*.blg
paper/*.out
''',encoding='utf-8')
findings=[]
patterns=[('GitHub token',r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b'),
          ('OpenAI token',r'\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}\b'),
          ('Private key',r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----')]
for path in DEST.rglob('*'):
    if not path.is_file() or '.git' in path.relative_to(DEST).parts:continue
    if path.suffix in ('.pdf','.png'):continue
    content=path.read_text(encoding='utf-8',errors='replace')
    for label,pattern in patterns:
        if re.search(pattern,content):findings.append({'file':str(path.relative_to(DEST)),'kind':label})
if findings:raise RuntimeError(json.dumps(findings))
report={'target':'https://github.com/RobinLuFae/aris-study-test','visibility':'public',
        'authorized_by':'User supplied repository and public visibility on 2026-11-09',
        'files':len(manifest['files'])+2,'credential_pattern_findings':findings,
        'excludes':['dataset pixels','model checkpoints','environments','third-party author repositories','credentials'],
        'status':'local content prepared; not yet pushed'}
(ROOT/'logs/github-publication-preparation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('PUBLICATION_CONTENT_PREPARED',report['files'],'files; credential pattern scan clean')

"""Immutable input copy for a review; never modifies measurements or paper sources."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--name',required=True);args=ap.parse_args()
out=ROOT/'_work'/args.name
if out.exists():raise ValueError('Use a new snapshot name')
source=ROOT/'paper';files=[]
for folder,pattern in [('', '*.tex'),('', '*.bib'),('', '*.sty'),('', '*.bst'),('', 'main.pdf'),
                       ('sections','*.tex'),('figures','*.tex'),('figures','*.pdf'),('figures','*.png'),
                       ('preview','*.png')]:
    files.extend((source/folder).glob(pattern))
manifest={}
for p in files:
    rel=p.relative_to(source);dest=out/rel;dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(p,dest)
    manifest[rel.as_posix()]='sha256:'+hashlib.sha256(dest.read_bytes()).hexdigest()
(out/'SNAPSHOT_INPUTS.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(out,len(manifest),'files')

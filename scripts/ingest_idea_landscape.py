"""Ingest already-fetched ARIS metadata; do not manufacture full-text readings."""
import json
import subprocess
import sys
from pathlib import Path
from witt_support import ROOT, write_json

assert Path(sys.prefix).resolve() == (ROOT/'.conda').resolve()
rows = json.loads((ROOT/'logs/aris-idea-landscape-metadata-ids.json').read_text(encoding='utf-8-sig'))
expected = {'2501.04732','2604.04413','2606.17940','2511.18884','2503.12907','2608.21743','2609.30629','2609.20150'}
assert {r['id'] for r in rows} == expected and all(r['title'] and r['abstract'] for r in rows)
receipt = {'expected_ids': sorted(expected), 'covered_ids': sorted(r['id'] for r in rows),
           'coverage_complete': True, 'scope': 'Official ARIS API metadata and complete abstracts; not a full-text reading audit',
           'full_text_available_and_read': ['2501.04732','2604.04413'], 'ingestion': []}
for row in rows:
    command = [sys.executable, '-B', '-X', 'utf8', str(ROOT/'ARIS/tools/research_wiki.py'),
               'ingest_paper', 'research-wiki', '--title', row['title'], '--authors', ', '.join(row['authors']),
               '--year', row['published'][:4], '--venue', 'arXiv reading version',
               '--thesis', f"Related-work metadata/abstract read: arXiv:{row['id']}; see idea-stage/NOVELTY_CONTEXT.md for evidence scope.",
               '--tags', 'deep-jscc,related-work,idea-landscape']
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    receipt['ingestion'].append({'id': row['id'], 'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
    if result.returncode:raise RuntimeError(result.stderr)
write_json(ROOT/'logs/idea-landscape-coverage.json', receipt)
print('IDEA_LANDSCAPE_METADATA_COVERAGE_PASS_8_OF_8')

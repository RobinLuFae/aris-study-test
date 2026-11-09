"""Capture deployment evidence using the project Conda interpreter only."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
assert Path(sys.prefix).resolve() == (root / '.conda').resolve()

def git(*args):
    repo = str(root / 'ARIS')
    return subprocess.check_output(['git', '-c', f'safe.directory={repo}', '-C', repo, *args], text=True).strip()

manifest = root / '.aris/installed-skills-codex.txt'
entries = [line.split('\t') for line in manifest.read_text(encoding='utf-8-sig').splitlines()]
skills = [row for row in entries if row[0] == 'skill']
for row in skills:
    assert (root / row[3] / 'SKILL.md').is_file(), row
assert len(skills) == 33
assert (root / 'research-wiki/index.md').is_file()
papers = sorted((root / 'research-wiki/papers').glob('*.md'))
assert len(papers) >= 1
data = {
    'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'upstream': 'https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep',
    'commit': git('rev-parse', 'HEAD'),
    'upstream_worktree_status': git('status', '--porcelain'),
    'python_executable': sys.executable,
    'python_prefix': sys.prefix,
    'python_version': sys.version,
    'skills_installed': len(skills),
    'manifest_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest(),
    'installer_adaptation': 'Skipped only optional Ensure-GlobalPointer call; upstream file unchanged.',
    'research_wiki_papers': [p.name for p in papers],
    'gpu_training_validated': False,
    'model_review_executed': False,
    'baseline_reproduced': False,
}
assert data['upstream_worktree_status'] == ''
(root / 'logs/deployment-evidence.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(data, ensure_ascii=False, indent=2))

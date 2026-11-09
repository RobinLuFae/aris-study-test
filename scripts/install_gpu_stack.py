"""Download and install binary wheels entirely within the authorized D: project.

tempfile.tempdir is a Python API setting, not an environment-variable change.
No source builds are allowed; installation uses the project Conda interpreter.
"""
from pathlib import Path
import argparse
import json
import runpy
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
assert Path(sys.prefix).resolve() == (root / '.conda').resolve()
assert root.drive.upper() == 'D:'
spec = json.loads((root/'configs/environment-gpu.json').read_text(encoding='utf-8'))
ap = argparse.ArgumentParser()
ap.add_argument('phase', choices=['download', 'install', 'download-analysis', 'install-analysis'])
args = ap.parse_args()
wheels = root/'downloads/wheels'
tmp = root/'downloads/tmp'
wheels.mkdir(parents=True, exist_ok=True)
tmp.mkdir(parents=True, exist_ok=True)
tempfile.tempdir = str(tmp)
assert Path(tempfile.gettempdir()).resolve() == tmp.resolve()
requirements = spec['pip_phases'][0]
if args.phase.endswith('-analysis'):
    requirements = requirements + spec['pip_phases'][1]
if args.phase.startswith('download'):
    command = ['download', '--dest', str(wheels), '--no-cache-dir', '--only-binary=:all:',
               '--find-links', str(wheels), '--index-url',
               ('https://pypi.org/simple' if args.phase.endswith('-analysis') else spec['index_url']),
               *requirements]
else:
    command = ['install', '--no-index', '--find-links', str(wheels), '--no-cache-dir',
               '--only-binary=:all:', '--report', str(root/'logs/pip-gpu-install.json'), *requirements]
print(json.dumps({'phase': args.phase, 'interpreter': sys.executable, 'tempdir': tempfile.gettempdir(),
                  'command': ['pip', *command]}, ensure_ascii=False), flush=True)
sys.argv = ['pip', *command]
runpy.run_module('pip', run_name='__main__')

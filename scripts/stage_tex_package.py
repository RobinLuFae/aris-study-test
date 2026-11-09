"""Stage a bounded TeX Live run-file archive locally; never register a TeX root."""
from pathlib import Path
import argparse
import hashlib
import json
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('packages', nargs='+')
    ap.add_argument('--mirror', default='https://mirror.aria-on-the-planet.es/CTAN')
    args = ap.parse_args()
    target = ROOT / 'third_party/texmf'
    cache = ROOT / 'downloads/tex'
    cache.mkdir(parents=True, exist_ok=True)
    target.mkdir(parents=True, exist_ok=True)
    for package in args.packages:
        if not package.replace('-', '').replace('.', '').isalnum():
            raise ValueError('Invalid package identifier')
        url = f'{args.mirror.rstrip("/")}/systems/texlive/tlnet/archive/{package}.tar.xz'
        archive = cache / f'{package}.tar.xz'
        if not archive.exists():
            with urllib.request.urlopen(url, timeout=40) as response:
                if int(response.headers.get('Content-Length', 0)) > 10 * 2**20:
                    raise RuntimeError('Package exceeds 10 MiB; ask before larger installation')
                payload = response.read(10 * 2**20 + 1)
                if len(payload) > 10 * 2**20:
                    raise RuntimeError('Package exceeds bounded download size')
                archive.write_bytes(payload)
                resolved_url = response.url
        else:
            resolved_url = 'cached; see prior receipt if available'
        with tarfile.open(archive, 'r:xz') as tf:
            members = tf.getmembers()
            if sum(m.size for m in members) > 40 * 2**20:
                raise RuntimeError('Unexpectedly large expanded package')
            for member in members:
                dest = (target / member.name).resolve()
                if not dest.is_relative_to(target.resolve()) or not (member.isfile() or member.isdir()):
                    raise RuntimeError(f'Unsafe archive member: {member.name}')
            tf.extractall(target, members=members, filter='data')
        receipt = {'package': package, 'source': url, 'resolved_url': resolved_url,
                   'bytes': archive.stat().st_size,
                   'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
                   'files': [m.name for m in members if m.isfile()],
                   'scope': 'project-local files only; no TeX registration or environment changes'}
        (cache / f'{package}.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
        print(json.dumps({k: v for k, v in receipt.items() if k != 'files'}), flush=True)


if __name__ == '__main__':
    main()

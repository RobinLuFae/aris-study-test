from pathlib import Path
import json
import subprocess
import sys

root=Path(__file__).resolve().parents[1]
assert Path(sys.prefix).resolve()==(root/'.conda').resolve()
rows=json.loads((root/'logs/aris-candidate-metadata.json').read_text(encoding='utf-8-sig'))
publication={
 '1809.01733':(2019,'IEEE Transactions on Cognitive Communications and Networking','10.1109/TCCN.2019.2919300'),
 '2012.00533':(2022,'IEEE Transactions on Circuits and Systems for Video Technology','10.1109/TCSVT.2021.3082521'),
 '2211.00937':(2023,'ICASSP','10.1109/ICASSP49357.2023.10094735'),
 '2308.09361':(2025,'IEEE Transactions on Cognitive Communications and Networking','10.1109/TCCN.2024.3424842'),
 '2408.16340':(2025,'AAAI','10.1609/aaai.v39i12.33442'),
 '2507.20467':(2025,'arXiv preprint',''),
}
with (root/'logs/aris-literature-ingest.log').open('w',encoding='utf-8') as log:
 for row in sorted(rows,key=lambda r:r['id']):
  year,venue,doi=publication[row['id']]
  cmd=[sys.executable,'-B','-X','utf8',str(root/'ARIS/tools/research_wiki.py'),'ingest_paper','research-wiki',
       '--title',row['title'],'--authors',', '.join(row['authors']),'--year',str(year),'--venue',venue,
       '--thesis','Candidate for image transmission reproduction. Evidence and limitations: literature/LITERATURE_REVIEW.md; not a local experimental result.',
       '--tags','deep-jscc,image-transmission,baseline-candidate']
  if doi:cmd+=['--external-id-doi',doi]
  r=subprocess.run(cmd,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8')
  log.write(json.dumps({'paper_id':row['id'],'command':cmd,'returncode':r.returncode},ensure_ascii=False)+'\n'+r.stdout+'\n')
  print(row['id'],r.returncode,r.stdout.strip().splitlines()[-1])
  if r.returncode:raise SystemExit(r.returncode)
receipt=json.loads((root/'literature/evidence/coverage_receipt.json').read_text(encoding='utf-8'))
covered={p for s in receipt['shards'] for p in s['covered_unit_ids']}
assert covered==set(receipt['frozen_unit_ids']) and not receipt['uncovered_unit_ids']

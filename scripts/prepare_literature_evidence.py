from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
ids=['1809.01733','2012.00533','2211.00937','2308.09361','2408.16340','2507.20467']
rows=json.loads((root/'logs/aris-candidate-metadata.json').read_text(encoding='utf-8-sig'))
by_id={r['id']:r for r in rows}
assert set(by_id)==set(ids)
repos={'2012.00533':'ADJSCC','2211.00937':'WITT','2308.09361':'SwinJSCC'}
repo_urls={'ADJSCC':'https://github.com/alexxu1988/ADJSCC',
           'WITT':'https://github.com/KeYang8/WITT','SwinJSCC':'https://github.com/semcomm/SwinJSCC'}
out=[]
for paper_id in ids:
    r=by_id[paper_id]
    item={'paper_id':paper_id,'dedup_key':'arxiv:'+paper_id,'title':r['title'],
          'authors':r['authors'],'published':r['published'],'updated':r['updated'],
          'verification_status':'ARIS_ARXIV_API_IDENTITY_VERIFIED','abstract':r['abstract'],
          'source_url':r['abs_url'],'source_excerpt':'','local_pdf_path':None,'local_note_paths':[],
          'evidence_status':'ABSTRACT_AVAILABLE'}
    if paper_id in repos:
        name=repos[paper_id];p=root/'baselines/upstream'/name/'README.md'
        item['source_excerpt']=p.read_text(encoding='utf-8')
        item['local_note_paths']=[str(p)]
        item['author_code_url']=repo_urls[name]
    if paper_id=='1809.01733':
        p=root.parent/'论文全文/04_2019_Bourtsoulatze_DeepJSCC.pdf'
        item['local_pdf_path']=str(p) if p.exists() else None
    if paper_id=='2211.00937':
        item['local_pdf_path']=str(root/'literature/2211.00937.pdf')
        item['code_excerpt_paths']=[str(root/'baselines/upstream/WITT/train.py'),str(root/'baselines/upstream/WITT/net/network.py')]
    if paper_id=='2408.16340':
        item['author_code_url']='https://github.com/zhang-guangyi/HJSCC'
        item['source_excerpt']='Author GitHub README states Python 3.9.21 is recommended, builds on QARV and NTSCC, and links pretrained checkpoints on Baidu. Verified by executor from https://github.com/zhang-guangyi/HJSCC; no GPU-memory requirement was established.'
    if paper_id=='2507.20467':
        item['code_status']='No author code was established from the retrieved abstract; unverified, not a claim of absence.'
    out.append(item)
dest=root/'literature/evidence';dest.mkdir(parents=True,exist_ok=True)
(dest/'candidate_evidence.json').write_text(json.dumps({'sources':['ARIS arxiv_fetch.py','author GitHub README','existing user local PDF library'],
    'frozen_ids':ids,'papers':out},ensure_ascii=False,indent=2),encoding='utf-8')
print('FROZEN_CANDIDATES',','.join(ids))

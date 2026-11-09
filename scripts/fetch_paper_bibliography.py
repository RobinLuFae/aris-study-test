"""Fetch primary Crossref BibTeX verbatim, then normalize only citation keys."""
from pathlib import Path
import json
import re
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
SOURCES={
    'bourtsoulatze2019deep':'10.1109/TCCN.2019.2919300',
    'yang2023witt':'10.1109/ICASSP49357.2023.10094735',
    'xu2022adaptive':'10.1109/TCSVT.2021.3082521',
    'yang2025swinjscc':'10.1109/TCCN.2024.3424842',
    'jo2021practical':'10.1109/CVPR46437.2021.00075',
}
folder=ROOT/'literature/evidence/paper-bibtex'
folder.mkdir(parents=True,exist_ok=True)
entries=[]; receipt=[]
for key,doi in SOURCES.items():
    url='https://api.crossref.org/works/'+doi+'/transform/application/x-bibtex'
    req=urllib.request.Request(url,headers={'User-Agent':'ARIS-course-reproducibility/1.0'})
    cached=folder/f'{key}.bib'
    if cached.exists():
        body=cached.read_text(encoding='utf-8')
    else:
        with urllib.request.urlopen(req,timeout=45) as response:
            body=response.read().decode('utf-8')
    if not body.lstrip().startswith('@'):
        raise RuntimeError('No BibTeX returned: '+doi)
    (folder/f'{key}.bib').write_text(body,encoding='utf-8')
    normalized=re.sub(r'(@\w+\{)[^,]+,',lambda m:m[1]+key+',',body,count=1)
    normalized=normalized.replace('–','--')
    normalized=re.sub(r'month=(\w+)',lambda m:'month={'+m[1]+'}',normalized)
    # Correct name segmentation against the author versions / official CVF page.
    normalized=normalized.replace('Joo Kim, Seon','Kim, Seon Joo')
    normalized=normalized.replace('Gunduz, Deniz',r'G{\"u}nd{\"u}z, Deniz')
    for acronym in ('WITT','SwinJSCC'):
        normalized=normalized.replace(acronym,'{'+acronym+'}')
    entries.append(normalized)
    receipt.append({'key':key,'doi':doi,'source':url,'raw':str((folder/f'{key}.bib').relative_to(ROOT))})
# Author-published technical report and software repository have no Crossref record.
entries.append('''@techreport{krizhevsky2009learning,
 author={Krizhevsky, Alex}, title={Learning Multiple Layers of Features from Tiny Images},
 institution={University of Toronto}, year={2009},
 url={https://www.cs.toronto.edu/~kriz/learning-features-2009-TR.pdf}}
@misc{yin2026aris,
 author={{wanshuiyin}}, title={{ARIS}: Auto-claude-code-research-in-sleep},
 year={2026}, howpublished={Software repository},
 url={https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep},
 note={Commit 2901234ad2954cd2388ced8d3aed2ed9de42803a}}
''')
(ROOT/'paper/references.bib').write_text('\n\n'.join(entries),encoding='utf-8')
(folder/'sources.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print('Fetched',len(SOURCES),'publisher BibTeX records; two primary-source records added.')

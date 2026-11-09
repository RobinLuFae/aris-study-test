"""CPU-only recomputation of the published P004 numerical analysis."""
from pathlib import Path
import json
from analyze_paired_gate_results import analyze

ROOT=Path(__file__).resolve().parents[1]
raw=json.loads((ROOT/'results/P004_R003_final_test.json').read_text(encoding='utf-8'))
recorded=json.loads((ROOT/'results/P004_R003_analysis.json').read_text(encoding='utf-8'))
recomputed=analyze(raw,'linear13')
if recomputed!=recorded:
    raise AssertionError('Raw-result recomputation differs from recorded analysis')
out=ROOT/'output/recomputed-analysis'
out.mkdir(parents=True,exist_ok=True)
(out/'P004_R003_analysis.json').write_text(json.dumps(recomputed,indent=2)+'\n',encoding='utf-8')
print('P004_RAW_ANALYSIS_REPRODUCED_EXACTLY; no model inference; output:',out)

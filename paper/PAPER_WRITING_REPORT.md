# ARIS paper-writing completion report

Date: 2026-11-09. Target: course empirical paper using CVPR 2026 format. Assurance: **draft**. Course-ready: **provisional**, because semantic reviewers share the executor's model family. Top-venue original-research acceptance is not claimed.

| Stage | Actual outcome | Evidence |
|---|---|---|
| Plan and acceptance contract | Completed; contract accepted in two rounds | PAPER_PLAN.md; PAPER_ACCEPTANCE_CONTRACT.md; contract traces |
| Figures and tables | Two vector plots, three source-driven tables; reviewed | paper/figures; figure-review trace |
| Writing review 1 | 8/10, Almost; implementation clarity fixes applied | immutable round1 snapshot; 001-round1.response.md |
| Writing review 2 | 9/10, Yes on course scientific content; presentation fixes applied | immutable round2 snapshot; 002-round2.response.md |
| Final empirical/numerical audit | PASS, fresh context, frozen declared inputs verified unchanged | PAPER_CLAIM_AUDIT.json; run02 raw response |
| Citation audit | PASS, eight KEEP outcomes; two metadata fixes checked in same-entry follow-ups | CITATION_AUDIT.json and per-entry raw replies |
| Compile / visual inspection | Five pages; all pages inspected, no undefined reference/citation or overflow warning | main.pdf; preview; main.log |
| Proof check | Not applicable: empirical paper, no theorem/proof claims | manuscript |
| Strict submission verifier / integrity forensics | Not run: draft assurance; forensics not requested | paper/.aris/assurance.txt |
| Local code/results package and public repository | Prepared with measured results, source and process record; remote revision recorded separately | output/submission; logs/github-publication.json |

The final audit covers empirical/numerical claims, not historical review causality, authorship or bibliography. Citation reviewers checked bibliography; writing reviewers and the executor checked page artwork; the executor separately checked deployment files and public availability. Requested model/effort strings are not treated as observed serving identity. Earlier blocked and WARN records remain archived.

User-directed scope: author and institution are intentional placeholders. The standalone Chinese process record is `notes/ARIS语义通信研究全过程记录.md`; the user will write personal reflections after reading it. The original training remained one finite-budget trajectory, and original-paper numerical parity remains unestablished. No new training or frozen-test inference was performed during this writing phase.

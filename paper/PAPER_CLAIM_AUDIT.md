# Paper-to-evidence audit: WARN

The fresh reviewer independently reproduced the core empirical results, checkpoint choice, validation admission, all 18 result-table rows and the 48 primary SNR-cell interval pairs. The complete raw review is retained under `.aris/traces/paper-claim-audit/2026-11-09_run01/001-audit.response.md`.

The initial draft double-rounded the headline maximum loss and called 3,072 RGB scalar channel values “pixels.” Both have been corrected by the executor. The bootstrap paragraph now specifies P002–P004, and the appendix limits the source-snapshot statement to those three runs. A CPU inspection additionally records 223 identical retained tensors and absence of optimizer state in `results/deployment_identity_receipt_20261109.json`.

Some implementation and historical-review assertions lacked provenance within the deliberately restricted audit input set. Existing raw source, configuration and review records remain available in the workspace. These exceptions must be checked rather than automatically treated as false or silently accepted.

**Status remains WARN.** The small source corrections overlapped the end of the initial audit; no dispatch-time immutable source snapshot was captured. A fresh post-edit audit is pending because native reviewer thread capacity is exhausted. Current source identities are recorded separately, not misrepresented as the initial audited input identities. Same-family review remains provisional.

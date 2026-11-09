# Fresh writing review, round 1

**Course-paper readiness: 8/10 — Almost.** The central result stands. Replacing 14 trained scalar-SNR networks with FP32 lookup tables reduced the complete inference file from 54,987,545 to 38,644,489 bytes (29.72%). On the selected CIFAR-10/AWGN checkpoint, the largest observed PSNR decrease across the eight frozen test SNRs was 0.000186 dB at 2.375 dB. The remaining work is local writing and presentation. No new experiment is needed for this verdict.

## Ranked strengths

1. **The storage claim has the right denominator.** Table 1 measures complete inference files from the same checkpoint. The 4,150,272 removed parameters, 70,070 stored FP32 values, and 223 equal retained tensors make the intervention intelligible. The same-variant reload check is clearly distinguished from reconstruction fidelity relative to the original.
2. **The test measures what interpolation changes.** The reader can distinguish five stored knots from three fractional conditions, see absolute reconstruction quality, and recover both signs of the paired difference. The largest decrease and the largest absolute change occur at different SNRs. Table 2 and Figure 2 correctly show this.
3. **The controls explain a practical choice.** The dense grid shows what the extra knots buy. The pilot contains a same-size linear versus nearest-neighbor comparison and retains a measured failure. The pointwise, checkpoint-conditional interpretation of the intervals is appropriate.

## Weaknesses and concrete fixes

**CRITICAL — None found.** The main storage, validation, and test numbers agree with the records inspected.

**MAJOR — Make the training-to-deployment path self-contained (§§3–4).** The paper describes the validation metric and optimizer but never specifies the training loss. It also leaves open what happens to the weights when the first 2,000 updates on the non-adaptive model end. An Adam reset alone does not answer that. State the actual optimized distortion and its scale, which weights initialize the adaptive model and how newly introduced parameters are initialized. Add one sentence showing where each scalar gate output is applied to the image-dependent feature transformation in the encoder or decoder. This will let a reader distinguish the locally trained baseline, the retained feature path, and the post-training substitution without opening the code. Verify these implementation details before wording them.

**MINOR — Improve the interpretation and precision of existing evidence.**

- The pilot paragraph compares three-node linear with five-node nearest lookup, changing two factors. Table 3 already supplies the controlled comparison. At five knots the files are both 38,472,457 bytes. Linear interpolation has a maximum loss of 0.009071 dB and nearest lookup 0.129533 dB, both at 2.25 dB. The latter exceeds the 0.1 dB tolerance used for subsequent validation. Keep the three-node result (0.093756 dB) as evidence about density. Use the fixed-knot comparison to explain interpolation.
- Report the frozen result in the same units and precision as Table 2. At 2.375 dB the loss is +0.186 mdB with pointwise interval [−0.041, +0.412] mdB. At 1.5 dB the largest absolute change is 0.338 mdB, a gain for the table. The nine-decimal prose and four-decimal percentage obscure these comparisons. Exact file bytes remain valuable.
- The conclusion says the pilot timings “vary.” The recorded 13-node median was 40.4 versus 36.2 ms for the original at batch size 1, and 43.7 versus 46.3 ms at batch size 128. Reporting the slower and faster observations together, with their fixed-order pilot context, is more informative and supports the existing decision against claiming a speedup.
- Distinguish the seed base for the paired deployment validations from the checkpoint-selection validation seed. The training configuration uses 9917 for checkpoint validation. “Validation uses noise seed base 51001” in §4 should name the deployment evaluations it describes. Define mean squared error (MSE) at first use.

## Per-section findings

- **Title and abstract.** The abstract already gives the storage benefit, test scope, and signed decrease directly. A title such as “Reducing WITT Model Storage by Tabulating Scalar SNR Gates” foregrounds the result more clearly than “A Reproducible Study of WITT.” The last abstract sentence can use the space to state how many test conditions actually exercise interpolation (three).
- **Introduction.** The question and numerical answer are clear. Replace “author-component reproduction” with a concrete description of training a local model using the WITT authors’ components. Use “later checkpoint” in place of “stronger checkpoint” unless a matched quality comparison is given there.
- **Related work and references.** The WITT, adaptive JSCC, and learned-table citations serve distinct purposes. The paper correctly treats tabulation as established. No missing reference is necessary for the bounded claims reviewed.
- **Method.** Equations (1)–(3), gate parameter arithmetic, CBR definition and table storage accounting are internally consistent. Clarify the feature multiplication described above. “Same-variant witness” can be written as “reload check.”
- **Protocol.** The selection rule, pilot, dense validation, full validation and frozen test have distinct roles. Equation (4), the signed difference and paired batch resampling are clear. Introduce P002–P004 alongside reader-facing names, and condense the pause at update 22,645 to the inclusion rule for scheduled validations.
- **Results.** Both plots and all three tables support the central result. The five-node dense maximum of 0.015405 dB and thirteen-node maximum of 0.000454 dB explain the cost of saving another 172,032 bytes. Table 2’s rounded near-zero knot entries are correctly qualified. Preserve the unfavorable fractional test result and nearest-neighbor failure. Table 3 could add that the shared-SNR result rounds to zero.
- **Discussion and conclusion.** The measured storage decrease belongs in the opening sentence. Keep the one-trajectory and measured-SNR boundaries. The last paragraph spends substantial space listing applications the study never attempted. Condense those examples and use the space for the actual timing observations.
- **Appendix.** Keep the source revision, evidence locations, AI’s role, and the specific review-induced change to fractional-SNR validation. Remove the narrative about user correction, pipeline bookkeeping, the count of sessions serving checklists, and pending publication decisions. For final delivery reconcile “Anonymous course-project author” with the course’s actual author instructions. Do not invent a name.

## Visual review

I opened **pages 1, 2, 3, 4, 5 and 6 individually** in the image viewer and inspected the corresponding six-page letter PDF. Page 1 has a readable title and abstract. Page 2 fits all three equations and Table 1 within the two columns. Page 3’s dense plot makes the low-SNR separation visible. Page 4’s signed error bars, knot markers, table headers, and units are legible. The conspicuous break splitting “interpo- / lation” across pages 3 and 4, with floats before the continuation, is worth fixing on the next typeset. Pages 5 and 6 each leave a largely empty right column. Removing the forced break between references and appendix, if course formatting permits, would improve use of space. Page 6’s long code filenames create wide interword gaps. Short linked labels or one entry point per line would read better. No clipping, overlap, or missing figure was visible.

## Top-venue original-research assessment

**Below the bar for a top-venue original-research submission.** This is a careful application of a known tabulation technique to a specific scalar conditioning path. The evidence supports a useful storage result on one locally trained model and channel setting. It does not establish a broadly new method, a speed advantage, or robustness across learned systems. Those distinctions do not reduce the course value of the existing experiment or require a new campaign.

## Completion and identity

This was a fresh review of the supplied snapshot, its TeX and figure/table sources, bibliography, PDF and six previews, with selected checks against local results and configurations. I did not retrain a model, rerun inference, or verify remote repository availability. I did not inspect earlier reviews or change the manuscript or evidence. This same-family assessment is provisional. The serving model variant and reasoning effort were not independently verified.

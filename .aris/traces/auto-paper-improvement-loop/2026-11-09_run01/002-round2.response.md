# Fresh writing review

**Course writing and readiness: 9/10 — Yes on scientific content.** The paper answers a concrete deployment question. For one locally trained WITT checkpoint, tabulating fourteen image-independent SNR maps reduces the complete inference file from 54,987,545 to 38,644,489 bytes (29.72%). Across the eight frozen CIFAR-10/AWGN test conditions, the largest measured PSNR decrease is 0.000186 dB. I reproduced the eight point differences from the recorded per-batch error sums. The largest absolute change is a gain of 0.338 mdB at 1.5 dB. The paper preserves both directions correctly. The remaining edits concern presentation and interpretation of the pilot.

## Ranked strengths

1. The title, abstract and opening explain what was trained locally, what was replaced after training and what was measured. The headline uses a complete file size, and the raw table-buffer calculation makes the saving intelligible.
2. The validation and final test serve distinct purposes. Pairing images and channel noise, preserving batches during resampling, separating stored knots from interpolation points, and defining signed loss give the tiny numerical differences a precise interpretation.
3. The pilot includes a useful unfavorable result. At identical file size, five-knot nearest lookup loses up to 0.129533 dB, versus 0.009071 dB for linear interpolation. The mixed latency medians also remain visible. Neither selling a speedup nor softening the measured storage advantage would be justified.

## Weaknesses and fixes

**CRITICAL:** None found.

**MAJOR, presentation only:** Page 5 contains only the tail of the conclusion in the upper left. The explicit page break before the bibliography in the main source pushes the references and appendix to page 6. Let the bibliography follow the conclusion in normal flow and re-render. A dedicated references page, if required by the course, can instead be preserved by tightening the main text enough to bring the conclusion onto page 4. The margins and type size already work.

**MINOR:**

- The pilot has 13 evaluation SNRs and the main table has 13 knots. Section 4 gives the pilot count but leaves their overlap implicit. Add that four pilot points, 2.25, 5.25, 8.25 and 11.25 dB, exercise interpolation for the 13-knot table. This explains the nonzero 13-knot pilot loss and why the later dense validation matters.
- The last paragraph of the introduction spends more space describing evaluation stages and retained records than explaining what the controls showed. A sentence giving the equal-size five-knot comparison above would expose the reason to interpolate early. Keep the archive details in the appendix.
- Introduce WITT as the wireless image transmission transformer on first use in the abstract. Define N immediately before Eq. (5) as the number of distinct images per SNR. Replace the phrase “successful serialization witness” in Section 4 with “a successful save-and-reload check,” already explained in Section 3.
- Page 1 visibly contains “Author Name / Institution / Department.” If identity is intentionally reserved for the student, retain that handoff. A named submission needs the student's actual details.

## Section findings

- **Title and abstract:** The storage claim leads, the local-checkpoint qualifier is present, and the five knots and three interpolated test conditions are identified. Keep the direct numerical result.
- **Introduction and related work:** The research question is clear. The comparison to established lookup-table work defines the contribution at a defensible scale. I found no missing reference necessary to support the central claim.
- **Method:** The map dimensions and biases give 296,448 parameters per gate and 4,150,272 overall. The equations, raw buffer size of 280,280 bytes, retained parameter count and separation of image-dependent processing from scalar tabulation are consistent. The reload check and original-versus-table experiment are distinguished correctly.
- **Protocol:** The split, two training stages, checkpoint criterion, new test noise, pooled MSE and conditional bootstrap are sufficiently explicit. The pilot-grid clarification above would make the historical comparison self-contained.
- **Results:** The dense-validation maxima agree with the records: 0.000454 dB for 13 knots and 0.015405 dB for five. The full-validation maximum is 0.000264 dB. Table 2 and Figure 2 agree on signs, units and pointwise intervals. The five displayed zeros at knots are explicitly rounded. Keep the adverse nearest-neighbor result and the measured test loss.
- **Discussion and conclusion:** The limitations are concentrated appropriately. The single checkpoint used for the final claim, the shared training trajectory, bounded SNR range and descriptive intervals are clear. The batch-size-1 slowdown and batch-size-128 improvement are correctly attributed to a fixed-order pilot. No new timing study is necessary for this paper.
- **Appendix:** The source commit, execution entry points and actual AI-assisted review decisions are concrete. The requested model identifiers are distinguished from evidence of reviewer identity. The appendix can stay with the references after reflow.

## Visual review

I opened pages **1, 2, 3, 4, 5 and 6** individually. Page 1 has a readable title and the identity placeholder. Page 2 fits the storage table and displayed equations within their columns. Page 3's protocol, PSNR equation and results are legible. Page 4 holds both figures and both remaining tables without clipping. The common scale in Figure 1 makes the five-knot penalty visible, while the text gives the smaller 13-knot peak. Figure 2 distinguishes knots and interpolation clearly. Page 5 has the whitespace described above. On page 6, the references and appendix are legible, including the wrapped reproduction paths. No additional figure is needed.

## Top-venue original-research judgment

**Below the threshold for an original-research CVPR paper.** The operation is established scalar-function tabulation, and the evidence establishes a useful tradeoff in one WITT configuration. It gives limited grounds for an architectural or broadly transferable research claim. This judgment does not call for expanding the course experiments.

## Completion and reviewer identity

I inspected the current source, tables, bibliography, six-page PDF and all six rendered pages, and checked the headline figures against the permitted saved results. I did not rerun training or inference. This is a provisional same-family review. The serving model variant and effort cannot be authenticated from a requested identifier.

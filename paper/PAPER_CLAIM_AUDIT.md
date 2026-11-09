# Fresh paper-to-evidence audit

**PASS for empirical and numerical reporting.** The three tables reproduce to the stated precision. The headline reduction applies to complete serialized inference files. The 0.000186 dB result is the largest **signed decrease** on the eight-point frozen grid for the selected checkpoint. No material mismatch or scientific correction was identified.

I compared the immutable `paper-final-20261109b` manuscript, sections, included table rows and captions against the inputs in `declared_inputs.json`. I used the project Conda environment on CPU for arithmetic, split verification, and independent batch-bootstrap recomputation. No model forward, training, GPU computation or dataset-pixel access was performed. Paths below are relative to AIRS.

## Claim ledger

**Architecture, training and compilation.** The recorded `witt_support.py:9–31` imports upstream WITT and sets CIFAR-10 input 3×32×32, latent width 32, depths [2,4], dimensions [128,256], window 2 and reversed decoder stages. `baselines/upstream/WITT/net/{encoder,decoder}.py` constructs seven scalar modulators on each side, with width 384. Each applies 1→384→384→384, two ReLUs and a sigmoid. The image-derived projections, elementwise modulation and final feature rescaling are present. `net/channel.py:25–30,44–70,81–87` uses a whole-batch power mean, packs the real features into complex symbols, adds independent real/imaginary noise with standard deviation √(1/(2·10^(s/10))) and restores scale. `net/network.py:57–70` defines CBR as half the latent real element count divided by source element count. Every recorded deployment evaluation cell has CBR 1/3. Evaluation records give upstream commit `2460db52264ad35d0d7521c9f505fc318134c086` and clean worktree status. The original/linear13 inspection record retains that metadata.

**Split, optimizer and checkpoint selection.** The CPU seed-20261107 permutation matches the stored split exactly, with 45,000 distinct train and 5,000 distinct validation IDs partitioning 0–49,999. The R003 config, R001/R003 recorded trainers and upstream distortion implementation show seed 42, Adam at 0.0001, batch size 128, FP32 inputs normalized to [0,1], independent per-image horizontal flips with probability 0.5, and the optimized mean squared difference of pixels scaled by 255 after reconstruction clipping (`loss/distortion.py:190–221`, `net/network.py:67–70`). Logged normalized MSE and the optimized objective differ by the stated factor 255². R001 constructs the model once before both stages, bypasses its constructed modulation branch for the first 2,000 updates at 7 dB, then switches mode, starts new Adam and samples uniformly from {1,4,7,10,13}. The branch retains its seeded constructor weights until activation. R002/R003 restore model, optimizer, sampler order/position/RNG and Python/Torch/CUDA RNGs. The separate resume-equivalence record applies only to its short fixed-SNR pretraining comparison.

The three training JSONLs yield 12+14+15=41 scheduled adaptive checks, at total steps 2,500 to 22,500 in increments of 500. The extra 15,300 and 22,645 cutoff checks are ineligible. Recomputing the arithmetic mean of the three normalized MSEs selects step 21,500, mean 0.0009668555493932219, agreeing with `logs/R003-checkpoint-selection.json`. The trainer evaluates 1, 7, 13 dB at seeds 9917+100s and replaces the incumbent only for strict improvement. The 8,000- and 21,500-step checkpoints belong to the same trajectory. The runtime records identify PyTorch 2.9.1+cu128, CUDA 12.8 and the RTX 5070 Laptop GPU.

**Table 1, complete-file storage.** The rows below come from `results/P002_gate_tables_R003_preparation.json`, also corroborated for original and linear13 by `results/deployment_identity_receipt_20261109.json`.

| Step 21,500 deployment | Learned parameters | Complete file bytes |
|---|---:|---:|
| Original | 13,715,056 | 54,987,545 |
| Linear 5 | 9,564,784 | 38,472,457 |
| Linear 13 | 9,564,784 | 38,644,489 |

One gate has 296,448 parameters, including biases. Fourteen remove 4,150,272. For 13 nodes, 69,888 gate outputs plus 182 knots give 70,070 FP32 buffer entries or 280,280 raw bytes. The file reduction is 29.7213778%, and linear5 saves 172,032 further bytes. `scripts/{snr_gate_table,prepare_gate_tables}.py` changes only the scalar MLPs, tabulates uniform knots on [1,13] with no retraining, clamps at the boundaries and implements the given linear interpolation or nearest lookup. Shared-SNR computes the retained original map once per batch and broadcasts it. The CPU inspection records equality for all 223 retained non-gate tensors and absence of optimizer state in original/linear13. Independent of the original-versus-table difference, the measured fresh-versus-reloaded maximum is zero for the recorded witnesses.

**Dense and full validation, gating and captions.** `results/P002_R003_dense_validation.json` and `P003_R003_full_validation.json` use checkpoint 21,500, the first 1,000 and all 5,000 IDs of the same frozen validation sequence, respectively. P002's 32 points include all 25 half-step points from 1–13 and seven additional fractions. Linear5 knots are 1,4,7,10,13; linear13 knots lie at every integer. From the recorded batch error sums, maximum signed P002 loss is 0.015405200 dB at 2.5 for linear5 and 0.000453562 dB at 2.25 for linear13. P003 yields 0.000264182 dB at 2.375 for linear13 on the eight eventual test SNRs. Both dense variants meet tolerance. For the primary variant both validations meet maximum loss ≤0.1 dB, reduction ≥25% and zero reload difference. The freeze generator consumes completed validations, checks artifacts and writes the test protocol. The paired evaluator checks the freeze, file sizes and checkpoint metadata **before** opening the official test partition. The saved and run-copied freezes agree. The test uses a separate deterministic synthetic ramp for reload checks. Validation noise base is 51001 and test base is 91001, with offsets 100000r + round(1000s) for repeat r=0,1,2. Seeds match across variants within every condition. The records establish the deployed choice and freeze order. Reviewers' influence on choosing the method is a separate historical question.

**Table 2, frozen official test.** `results/P004_R003_final_test.json` contains official indices 0–9,999 in order, eight SNRs and three paired channel realizations. I pooled per-batch sums of per-image MSEs over all realizations with their actual counts, computed PSNR from pooled MSE and signed loss as 10 log10(table MSE/original MSE), then resampled batch positions jointly with the recorded bootstrap seeds. The 3,072 RGB values per image correspond to 3×32×32. The 2,000 draws per SNR preserve pairing across methods and noises and weight the short last batch. P002 has 8 clusters (last 104 images), P003 has 40 (last 8), P004 has 79 (last 16). The resulting 2.5th/97.5th percentiles are pointwise, conditional on the checkpoint, batch composition and realized noises.

| SNR dB | Original PSNR dB | Linear13 PSNR dB | Loss mdB | 95% interval mdB |
|---:|---:|---:|---:|---:|
| 1 | 27.09260 | 27.09260 | 0.000 | [0.000, 0.000] |
| 1.5 | 27.53395 | 27.53429 | −0.338 | [−0.479, −0.188] |
| 2.375 | 28.27304 | 28.27285 | +0.186 | [−0.041, +0.412] |
| 3 | 28.78591 | 28.78591 | 0.000 | [0.000, 0.000] |
| 7 | 31.84959 | 31.84959 | 0.000 | [0.000, 0.000] |
| 12 | 34.87276 | 34.87276 | 0.000 | [0.000, 0.000] |
| 12.5 | 35.11328 | 35.11354 | −0.258 | [−0.269, −0.246] |
| 13 | 35.33646 | 35.33646 | 0.000 | [0.000, 0.000] |

The largest signed loss is +0.000186487920 dB at 2.375 dB. The largest absolute change is a gain of 0.337846 mdB at 1.5 dB. All five integer-knot differences have magnitude below 3×10⁻⁸ dB, including the largest, 2.78648×10⁻⁸ at 7 dB. Their displayed zeros are rounded. The three fractional conditions exercise interpolation and include both signs. The eight-point-grid and bootstrap captions correctly describe 10,000 unique images and three repetitions per condition.

**Table 3, historical pilot and timings.** From `results/P001_gate_tables_R001_{pilot,preparation}.json`, the step-8,000 pilot uses the first 1,000 validation images at 13 fixed SNRs, three paired repeats each. Four SNRs (2.25,5.25,8.25,11.25) lie off the 13-node knots. Recomputing all 13 losses from the three repeat MSEs for each variant gives:

| Pilot deployment | Complete file bytes | Maximum signed loss dB |
|---|---:|---:|
| Original | 54,987,481 | 0.000000 |
| Shared-SNR MLP | 54,989,849 | 0.000000 |
| Linear 3 | 38,429,449 | 0.093756 |
| Linear 5 | 38,472,457 | 0.009071 |
| Linear 9 | 38,558,473 | 0.000389 |
| Linear 13 | 38,644,489 | 0.000258 |
| Nearest 5 | 38,472,457 | 0.129533 |

The shared-control maximum is +8.607×10⁻⁸ dB before rounding; it retains the original parameter count. Linear3's full-grid maximum, also quoted in the appendix, is 0.093756326 dB at 4 dB. The equally sized five-knot variants differ only by lookup rule. Pilot timing sample medians confirm original/linear13 at 36.176/40.392 ms for batch 1 and 46.269/43.695 ms for batch 128. These are fixed-order synchronized encoder–AWGN–decoder forwards at 7 dB, 30 samples after 10 warmups, inputs already on the GPU. The opposite ordering across batch sizes supports the limited timing conclusion.

## Scope and unknowns

The evidence supports one local WITT trajectory, simulated AWGN, CIFAR-10, CBR 1/3, discrete in-domain SNRs and the recorded paired noises. It does not establish training-seed variability, convergence, parity to external WITT benchmarks, continuous/out-of-domain fidelity, semantic utility, real-link performance or a general latency advantage. Raw pixels, training/inference re-execution and independent remeasurement of deployment binaries were outside this audit; the supplied CPU artifact-inspection record supports the tensor comparison. The figure captions' empirical content was checked; figure artwork and plotting code were outside the declared input set.

Historical reviewer-event causality, AI/student authorship and bibliographic existence were outside the empirical audit. Public repository availability, inclusion of a reproduction guide, and the implementation of the plot generators were not independently established from the declared materials. No prior verdict or project narrative was used. Same-family assurance remains provisional; requested model or effort settings do not authenticate serving identity.

# WITT SNR-gate tabulation: course reproduction package

This package accompanies **Reducing WITT Model Storage by Tabulating Scalar SNR Gates**. It contains the local research wrappers, frozen configurations, measured results, figure generators, and paper sources. The study uses one finite-budget training trajectory; numerical parity with the original paper and convergence remain unestablished.

## Main measured result

For the selected 21,500-update checkpoint, replacing 14 scalar SNR MLPs with 13-node FP32 tables changes complete inference-file size from 54,987,545 to 38,644,489 bytes (29.7214% smaller). P004 uses CIFAR-10's 10,000 official test images, simulated AWGN, CBR 1/3, eight frozen SNR points, and three paired noise realizations. Exact maximum signed PSNR loss: **0.00018648792025736705 dB**. Maximum absolute change: **0.0003378461331543206 dB**, a gain at a different condition. The tables are a post-training deployment transformation; no latency improvement is established.

## Files

- `scripts/snr_gate_table.py`: tabulation and interpolation; image-dependent components retained.
- `scripts/train_witt.py`: bounded, resumable training with fixed split and checkpoint selection.
- `scripts/prepare_gate_tables.py`: CPU compilation and actual saved-file measurements.
- `scripts/evaluate_gate_tables_paired.py`: paired validation and admitted frozen testing.
- `scripts/freeze_gate_test.py`: checks validation gates before a write-once test freeze.
- `scripts/analyze_paired_gate_results.py`: pooled MSE, PSNR, conditional batch bootstrap.
- `results/P004_R003_final_test.json`: original per-batch test error sums and image counts.
- `configs/`: actual historical configurations, including frozen protocol.
- `paper/figures/`: independent figure/table generators reading saved JSON; no inference.
- `notes/`: actual AI workflow, corrections and user decisions; student reflections remain separately authored.

## Recreate the tables and figures without GPU inference

Use a Conda environment rooted at `.conda`. From the package root in PowerShell:

```powershell
conda create --prefix ./.conda python=3.11 pip --yes
& ./.conda/python.exe -m pip install numpy==1.26.4 matplotlib==3.10.7
& ./.conda/python.exe -B -X utf8 paper/figures/gen_validation.py
& ./.conda/python.exe -B -X utf8 paper/figures/gen_test.py
& ./.conda/python.exe -B -X utf8 paper/figures/gen_tables.py
& ./.conda/python.exe -B -X utf8 scripts/reproduce_saved_analysis.py
```

The final command recomputes the P004 summary and all recorded conditional intervals from per-batch raw results, verifies their agreement, and writes a separate output. This reproduces the analysis, rather than rerunning model inference. The current user's installed environment is already available; these setup commands are instructions for a new operator, not commands automatically rerun by the project.

## Model inference and training

Acquire the original author code separately and preserve its citation:

```powershell
git clone https://github.com/KeYang8/WITT baselines/upstream/WITT
git -C baselines/upstream/WITT checkout 2460db52264ad35d0d7521c9f505fc318134c086
```

The original source is excluded from this code release. Dependency versions are in `configs/environment-gpu.json`. The measured environment uses Python 3.11, torch 2.9.1+cu128, torchvision 0.24.1+cu128, numpy 1.26.4, timm 0.9.16, and float32. Install GPU dependencies into a Conda environment at a suitable location after checking disk space and driver compatibility. Dataset pixels, environment binaries, and checkpoints are not tracked in the code repository.

Obtain the CIFAR-10 Python data from its author website and place the extracted `cifar-10-batches-py` folder under `data/`. Preserve the recorded split indices under `data/splits/`. New training uses `scripts/train_witt.py --config CONFIG --budget-file WINDOW --max-seconds 1200`; both JSON arguments must describe a **new run ID and a currently authorized time window**. Historical windows are expired. Training refuses to overwrite a run, and analysis refuses to overwrite an existing output. The selected historical checkpoint and compiled weights are retained in the local course workspace, separately from the code bundle.

Frozen configurations contain historical absolute paths and identify completed runs. On another machine, create a separate experimental copy with local paths and new IDs. This is a new reproduction run, not a replacement for P004. To repeat training, follow the two-stage protocol and selection rule in the paper; do not use the test set to choose knots or checkpoints. Running a new model evaluation requires dataset pixels, author code, saved weights or new training, and a fresh compute budget. Do not reopen the completed local P004 merely to recreate plots.

## Paper and third-party sources

`paper/main.tex` uses the official CVPR 2026 author-kit style; this is a course paper, not a CVPR submission. `scripts/Compile-CoursePaper.ps1` is adapted to the original machine's existing MiKTeX location, disables automatic package installation and shell escape, and uses project-local TeX components. On another machine, compile `paper/main.tex` with an already configured LaTeX distribution. The `.sty` and `.bst` files retain their upstream notices.

See `THIRD_PARTY_NOTICES.md`. WITT, ARIS, CIFAR-10, and downloaded papers retain their original authorship. The source bundle excludes author repositories, dataset pixels, downloaded research PDFs, account credentials, environments, and private CLI state. Public code and measured results: https://github.com/RobinLuFae/aris-study-test . Two fresh writing reviews and the final empirical/citation audits are complete with same-family provisional assurance. Author/institution placeholders are intentional. The student will write personal reflections after reading the separate Chinese research-process record.

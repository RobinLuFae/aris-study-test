# Experiment Tracker

| ID | Purpose | System | Split | Status | Evidence |
|---|---|---|---|---|---|
| ENV-GPU | 环境计算验证 | PyTorch CUDA | 合成输入 | PASS | logs/gpu-smoke.json |
| ENV-WITT | 作者模型可运行性 | WITT C32 | 合成输入 | PASS | logs/witt-model-smoke.json |
| R000 | 数据与训练入口检查 | WITT | train/validation | PASS | logs/R000-acceptance.json；重载验证差值为0 |
| R001 | seed42 初始基线 | WITT 两阶段 | train/validation | COMPLETED, 8000更新，未收敛 | logs/R001-functional-gate.json；refine-logs/EXPERIMENT_RESULTS.md |
| R001-D | 条件SNR偏差诊断 | 冻结WITT | 固定1000验证图 | COMPLETED,27格 | results/R001_conditioning_diagnostic.json；适配前向差值0 |
| RSM00/01 | 连续22步与20+2恢复 | WITT预训练路径 | train/validation | PASS,参数/Adam/RNG/指标相同 | logs/resume-equivalence.json |
| R002 | seed42基线续训段2 | WITT,继承Adam/RNG | 同一划分 | PAUSED,总15300步 | checkpoints/R002_witt_baseline_seed42_segment2/latest.pt；logs/R002-launch.log |
| P001 | 冻结R001的查表部署pilot | 原始/广播/5查表变体 | 固定1000验证图,13SNR,3噪声 | COMPLETED,critical review已完成 | results/P001_gate_tables_R001_pilot.json；results/P001_pilot_summary_v2.json（各变体完整网格/真实节点统计） |
| R003 | seed42续训段3 | WITT,继承Adam/RNG | 相同划分 | PAUSED总22645步,合格best21500步 | logs/R003-checkpoint-selection.json；checkpoints/R003_witt_baseline_seed42_segment3/latest.pt |
| P002 | 加密SNR验证 | 原始/linear5/linear13 | 1000val,32SNR,3noise | COMPLETED,primarygatePASS | results/P002_R003_dense_validation.json；P002_R003_analysis.json |
| P003 | 全量验证闭合 | 原始/linear13 | 5000val,8SNR,3noise | COMPLETED,primarygatePASS | results/P003_R003_full_validation.json；P003_R003_analysis.json |
| P004 | 冻结正式测试 | 原始/linear13 | 10000test,8SNR,3noise | COMPLETED,engineeringgatePASS | results/P004_R003_final_test.json；P004_R003_analysis.json；configs/P004_R003_test_freeze.json |

今日硬限制：2026-11-07 17:17:02中国时间前停止GPU训练，约20分钟分段。预算配置configs/training_window_2026-11-07.json，scripts/training_budget.py强制检查。续期需要用户新指令。

用户在约15:48要求因额度不足提前收尾、明日继续。本日实验已全部退出，不再使用剩余预算。恢复从SESSION_HANDOFF.md开始。

2026-11-08用户恢复并授权约一小时，硬截止11:01:19中国时间，configs/training_window_2026-11-08.json。R003/P002/P003已完成当前段；P004只有两组实际验证均通过后才冻结启动。当前恢复入口TODAY_PROGRESS_20261108.md。昨天的暂停记录为历史，不代表今日仍暂停。

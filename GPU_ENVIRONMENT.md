# 本地 GPU 环境

2026-11-07，用户批准将环境放在本项目 `.conda`，安装包放在 `downloads/`。

环境由既有 Conda 环境扩展。使用官方 CUDA 12.8 二进制 wheel，固定 PyTorch 2.9.1+cu128、TorchVision 0.24.1+cu128。辅助依赖见 `configs/environment-gpu.json`。未修改环境变量；安装和下载临时目录由 Python tempfile API 指向 D 盘项目目录。

## 验证命令

在 AIRS 文件夹中执行：

```powershell
& './.conda/python.exe' -B -X utf8 './scripts/gpu_smoke.py'
```

预期末行 `GPU_FORWARD_BACKWARD_PASS`。脚本实际运行 CUDA 卷积、转置卷积和多头注意力，检查有限梯度及一次 Adam 更新后的权重变化，并将结果保存到 `logs/gpu-smoke.json`。其结果属于合成输入的环境验证，不是基线复现或算法性能指标。

首次验证识别到 RTX 5070 Laptop GPU、计算能力 12.0，编译架构列表包含 sm_120，CUDA runtime 为 12.8。峰值显存仅反映小型验证输入，不能用于估计完整基线显存。

## 安装记录

```powershell
& './.conda/python.exe' -B -X utf8 './scripts/install_gpu_stack.py' download
& './.conda/python.exe' -B -X utf8 './scripts/install_gpu_stack.py' install
& './.conda/python.exe' -B -X utf8 './scripts/install_gpu_stack.py' download-analysis
& './.conda/python.exe' -B -X utf8 './scripts/install_gpu_stack.py' install-analysis
```

下载目录 `downloads/wheels/`，临时目录 `downloads/tmp/`，离线安装到 `.conda`。日志：`logs/pytorch-download.log`、`logs/pytorch-install.log`、`logs/analysis-download.log`、`logs/analysis-install.log`。

版本选择依据：PyTorch 官方历史版本页面提供该 wheel 配对，现有驱动 573.24 对应 CUDA 12 系列；最终以实际 kernel-dispatch witness 为准。来源：https://pytorch.org/get-started/previous-versions/ ，https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html 。

完整基线的前向、反向、数据读取和训练速度另行测试。若某个模型依赖当前环境未支持的旧算子或版本，须记录适配及复现差异。

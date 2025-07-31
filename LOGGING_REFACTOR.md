# Causal-Copilot Logging System Refactor

## 概述

本次重构将项目中所有的 `print()` 语句替换为专业的、结构化的日志系统，提供更清晰、更易读的命令行输出，特别适合学术研究项目的需求。

## 主要改进

### 🎯 **简洁整洁的输出**
- 移除冗余的调试信息
- 重点突出核心流程和结果
- 专业的学术风格输出

### 🎨 **可视化改进**
- 彩色输出区分不同消息类型
- 图标标识提高可读性
- 清晰的章节和进度显示

### 📊 **结构化信息展示**
- 标准化的指标表格
- 清晰的状态显示
- 进度条和检查点标记

### 🔧 **灵活的日志级别**
- `INFO`: 正常操作信息（默认）
- `WARNING`: 非关键问题警告
- `ERROR`: 可恢复错误
- `DEBUG`: 详细技术信息（可选）

## 使用示例

### 运行演示
```bash
python demo_logger.py
```

### 在代码中使用
```python
from utils.logger import logger

# 基本消息
logger.info("Processing data")
logger.success("Task completed")
logger.warning("Non-critical issue")
logger.error("Recoverable error")

# 专业输出
logger.header("Analysis Session")
logger.section("Data Processing")
logger.checkpoint("Phase completed")

# 状态和进度
logger.status("Dataset shape", "(1000, 10)")
logger.progress(50, 100, "Processing")

# 结果展示
metrics = {"Precision": 0.85, "Recall": 0.72}
logger.metrics_table(metrics, "Results")
```

### 日志级别控制
```python
from utils.logger import set_quiet_mode, set_verbose_mode

# 静默模式（仅警告和错误）
set_quiet_mode()

# 详细模式（所有消息）
set_verbose_mode()
```

## 重构范围

### ✅ 已完成的文件
- `main.py` - 主流程输出
- `postprocess/judge.py` - 图评估和后处理
- `postprocess/visualization.py` - 可视化模块
- `causal_inference/inference.py` - 因果推断模块
- `data/simulator/dummy.py` - 数据模拟器
- `global_setting/Initialize_state.py` - 全局状态
- `causal_inference/DRL/*.py` - DRL子模块
- `postprocess/judge_functions.py` - 评估函数

### 🎯 输出特点
- **简洁性**: 默认只显示关键信息
- **专业性**: 学术研究导向的输出风格  
- **可读性**: 清晰的结构和视觉层次
- **可控性**: 可调节的详细程度

## 实际效果

### 重构前
```
Real-world data loaded successfully.
Algorithm selected: PC
User query processed.
-------------------------------------------------- Global State --------------------------------------------------
<GlobalState object with 200 lines of debug info>
----------------------------------------------------------------------------------------------------
Preprocessed Data:  <DataFrame with full content dump>
Statistics Info:  Very long unformatted text...
Bootstrap Pruning Decisioning...
Selected Algorithm:  PC
```

### 重构后
```
== CAUSAL-COPILOT ANALYSIS SESSION ================

📊 Dataset loaded successfully
📊 Dataset shape: (7466, 11)
📊 Data type: Continuous

✓ Preprocessing completed

--- Algorithm Selection -------------------------
🧠 PC Algorithm: Selected algorithm
⚙ Running PC Algorithm

✓ 🏁 Causal discovery completed

--- Performance Evaluation -------------------
Structural Hamming Distance : 8.0000
Precision                  : 0.8571
Recall                     : 0.7500
F1-Score                   : 0.8000

✓ 🏁 Analysis session completed
⏱ Total analysis time: 1m 23.4s
```

## 技术细节

- 新增 `utils/logger.py` 模块
- 兼容现有代码结构
- 支持并发安全
- 可扩展的图标和颜色系统
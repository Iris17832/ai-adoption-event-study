# REPRODUCE 可复现说明（Reproducibility Guide）

> 交付物 #7。目标：换一台干净机器，按本文档从原始数据跑出论文主表的每一个数字。
> 撰写原则：每跑通一个环节就更新一节，不要留到 11.22 补写。

## 1. 环境要求

- Python：3.10+（本机使用 3.13.12，需注明）
- 依赖：`requirements.txt`（代码目录生成并冻结版本：`pip freeze > requirements.txt`）
- 关键依赖：pandas, numpy, statsmodels, jieba, akshare（或 tushare）, matplotlib, openai/deepseek SDK
- API：DeepSeek（或 Qwen）API key，环境变量 `DEEPSEEK_API_KEY`；预计调用量与费用写明

## 2. 目录结构

```
research-package/
├── code/                 # 全部脚本，编号即执行顺序
│   ├── 01_download_reports.py   # 下载年报 MD&A
│   ├── 02_extract_mda.py        # 抽取 MD&A 段落
│   ├── 03_llm_scoring.py        # LLM 逐段判读 AI 采纳强度
│   ├── 04_dict_baseline.py      # 73词词典法 baseline
│   ├── 05_fetch_prices.py       # 事件窗口行情
│   ├── 06_car_analysis.py       # 市场模型 + CAR 事件研究
│   ├── 07_cross_section.py      # 横截面回归
│   ├── 08_placebo_chatgpt.py    # ChatGPT 安慰剂检验
│   └── 09_make_figures.py       # 全部图表
├── data/
│   ├── raw/       # 原始数据（只进不改）
│   └── processed/ # 中间与最终数据（由脚本生成）
├── results/       # 表格(TXT/PDF)与图(PDF/PNG)，文件名与论文表号一致
```

## 3. 一键复现流程

```bash
# 1) 安装依赖
pip install -r code/requirements.txt
# 2) 依次执行（每步产物落盘，可断点续跑）
python code/01_download_reports.py
python code/02_extract_mda.py
export DEEPSEEK_API_KEY=sk-xxx
python code/03_llm_scoring.py        # ⚠️ 耗时+费用：约 N 次调用，约 XX 元
python code/04_dict_baseline.py
python code/05_fetch_prices.py
python code/06_car_analysis.py       # → 主表 Table 1-3
python code/07_cross_section.py
python code/08_placebo_chatgpt.py
python code/09_make_figures.py       # → Figure 1-4
```

## 4. 随机种子与确定性

- 所有涉及随机性的步骤（如抽样校验、bootstrap）固定 `random_state=42`。
- LLM 打分的复现性说明：temperature=0；同时保存原始 API 返回 JSON 于 `data/processed/llm_raw/`，即使模型升级导致打分不可严格复现，原始响应也构成审计证据。

## 5. 版本快照（提交时填写）

- Python 与关键包版本：
- AKShare/tushare 版本与数据拉取日期：
- DeepSeek API 模型名与版本（如 deepseek-chat, 2026-xx）：
- git commit hash（最终版）：

## 6. 已知限制

- （如实写，例如：巨潮年报下载受频率限制，我们提供了已下载快照；LLM 打分非严格确定，提供原始响应存档等）

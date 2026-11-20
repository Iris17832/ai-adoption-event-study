# 代码仓库 README

> 交付物 #2 的入口。研究题目：大语言模型度量的企业人工智能采纳与股票回报——来自DeepSeek冲击的事件研究证据

## 这是什么

用 LLM 从 A 股上市公司 2023 年报 MD&A 中度量企业真实 AI 采纳强度，以 DeepSeek-R1 发布（2025-01-20）为外生技术冲击，检验高/低 AI 采纳组的累计超额收益（CAR）差异，并与词典法、AI 概念股名单两种 baseline 度量对比。

## 快速开始

见 `../reproducibility/REPRODUCE.md`（一键复现流程、环境、随机种子、API 费用预估）。

## 代码结构（按执行顺序编号）

| 脚本 | 功能 | 输入 | 输出 |
|------|------|------|------|
| 01_download_reports.py | 下载年报 | 巨潮 | data/raw/annual_reports/ |
| 02_extract_mda.py | 抽取 MD&A 段落 | 年报 PDF | data/processed/mda.parquet |
| 03_llm_scoring.py | LLM 逐段 AI 采纳判读 | MD&A | data/processed/ai_adoption_llm.csv |
| 04_dict_baseline.py | 73词词典法 baseline | MD&A | data/processed/ai_adoption_dict.csv |
| 05_fetch_prices.py | 事件窗口行情 | AKShare | data/prices/ |
| 06_car_analysis.py | 市场模型+CAR 主结果 | 价格+分组 | results/table1-3 |
| 07_cross_section.py | 横截面回归 | CAR+特征 | results/table4 |
| 08_placebo_chatgpt.py | ChatGPT 安慰剂 | 同上 | results/table5 |
| 09_make_figures.py | 全部图表 | 上述 | results/figures/ |

## 与论文的对应

- Table 1 → `06_car_analysis.py`
- Figure 1（分组 CAR 走势）→ `09_make_figures.py`
- （提交前补全对应关系表）

## 复现注意

- git 提交策略：每个实验阶段完成后 commit 一次（时间戳即过程证据），禁止最后一次性打包。
- `data/raw/` 只进不改；所有加工产物由脚本生成，不手改数据文件。

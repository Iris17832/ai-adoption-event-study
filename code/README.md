# 代码仓库 README

> 交付物 #2 入口。题目：**大语言模型度量的企业AI采纳与股票回报——来自DeepSeek冲击的事件研究**
> 队伍：张锦悦、孔佳怡（山东财经大学）｜赛道四（经济金融与社会科学智能分析）
> 全部数据来自公开接口，全部结果由脚本从原始数据生成，无手工改数。
> 本版为 2026-11-21 提交前终版，`code/` 内 **20 个 Python 脚本 + 2 个 shell 链** 全部登记，与 `REPRODUCE.md` 一一对应。

## 研究一句话

用 LLM（GLM-4-Flash）逐段判读 A 股 2023 年报 MD&A 中的"真实 AI 应用 / 战略口号 / 无关"三分类，构建企业 AI 采纳指数；以 DeepSeek-R1 发布（2025-01-20）为外生冲击做事件研究，检验高/低 AI 采纳组的 CAR 差异；词典法（73 词 AI 词典）为基线度量，ChatGPT 发布（2022-11-30）为安慰剂事件。

## 代码结构（编号即执行顺序）

| 脚本 | 功能 | 输入 | 主要输出 |
|------|------|------|----------|
| `data_client.py` | 公开数据薄客户端：巨潮年报查询/下载、腾讯日K（前复权，主通道）、新浪K线（兜底）、东财（兜底）；指数退避 + 限速 + 双通道容灾 | — | 供各脚本 import |
| `figstyle.py` | 图表样式统一（橙蓝双主色、中文字体栈、白底、300dpi） | — | 供 09 import |
| `01_fetch_stock_list.py` | 获取沪深 A 股清单 | 东财接口 | `data/processed/stock_list.csv`（5,565 只） |
| `02_download_reports.py` | 定位并下载 2023 年报 PDF（巨潮主/东财备双通道，断点续跑，`--sample all/100`） | stock_list | `data/raw/annual_reports/` + `report_index.csv` |
| `03_extract_mda.py` | pypdf 提取 MD&A 章节 + 含 AI 关键词段落表（段落 ID 稳定，支持增量） | 年报 PDF | `data/processed/mda_text/` + `mda_paragraphs.csv` |
| `04_llm_scoring.py` | GLM-4-Flash 逐段三分类判读（temperature=0，few-shot 锚定，断点续跑按 `llm_raw/{para_id}.json` 缓存，容错读 + 原子写 + JSON 解析兜底），聚合公司级 `ai_index = 0.5×应用密度 + 0.3×场景广度 + 0.2×投入` | mda_paragraphs | `ai_adoption_llm.csv` + `ai_adoption_firm.csv` + `llm_raw/`（原始响应审计存档） |
| `04_dict_baseline.py` | 词典法基线（73 词 AI 词典 v1），输出与 LLM 法的 Spearman/分歧对比 | mda_text | `ai_adoption_dict.csv` + `results/dict_vs_llm_correlation.txt` |
| `05_fetch_prices.py` | 事件窗口行情：DeepSeek 主窗（2025.1）+ ChatGPT 安慰剂窗（2022.11）；`--codes-from firm/sample --workers N`（并发 + 断点续跑） | stock_list / firm 表 | `data/prices/deepseek/`、`data/prices/placebo/` + 指数 |
| `06_car_analysis.py` | 市场模型（估计窗 OLS）+ CAR 组间 t 检验 + 指数回归；主检验与安慰剂并跑 | prices + firm 表 | `results/car_panel_deepseek.csv`、`table_*_groups/regression.csv` |
| `07_cross_section.py` | 横截面回归（控制规模/波动/动量；成交额以成交量×收盘价合成，见代码注释） | CAR 面板 | `results/table4_cross_section.csv` |
| `09_make_figures.py` | 全部论文图表（统一橙蓝配色 300dpi） | results CSV | `results/figures/fig1–fig4`（5 张） |
| `10_robustness.py` | 稳健性：等权指数 / 仅应用密度 / 二值采纳 / 高分位分组四类替代度量（分组退化时回退 `>0/=0` 并登记 split） | CAR 面板 | `results/table6_robustness.csv` |
| `11_make_citation_checklist.py` | 生成 30 条参考文献人工核实清单 Excel（可点链接 + 下拉勾选） | 文献登记表 | `references/citation_human_checklist.xlsx` |
| `12_aggregate_partial.py` | 从 `llm_raw/` 缓存重建最终公司级指数（awk 批量读、容错解析、仅保留段落表真实 `para_id`，排除 724 个历史重复缓存） | llm_raw + mda_paragraphs | `ai_adoption_llm.csv` + `ai_adoption_firm.csv`（最终 N=2,082） |
| `13_diagnostics.py` | 学术诚信诊断 D1–D4：完整打分子样本重估、beta 组间差异与控制、安慰剂窗口边界、公司特征控制 | 面板 + 行情 | `results/table7_diagnostics.csv`、`diagnostics_report.txt`、`car_panel_placebo.csv` |
| `14_final_report.py` | 从 `results/*.csv` 程序化生成论文数字快照（杜绝手工抄数） | results CSV | `results/final_numbers.md` |
| `15_patch_missing.py` | 精准补打缺失/损坏缓存段落（awk 批量校验 + 复用 04 提示词，串行避限流） | 段落表 + llm_raw | 补齐的 `llm_raw/*.json` |
| `16_md_to_pdf.py` | 论文 `manuscript.md` → 提交版 PDF（自建 md→html，公式简化渲染，Chrome 无头打印 + CSS @page 页码，剥离内部稿本元信息） | manuscript.md | `paper/manuscript.pdf`（18 页 / 5 图内嵌） |
| `17_package_check.py` | 提交前全包自检（8 项交付物存在性 + 数字一致性 + 安全检查 40 余项） | 全项目 | `results/final_package_check.md` |
| `18_make_defense_ppt.py` | 生成 5 分钟答辩 PPT（交付物 #9 备用件；学术白底版式，橙蓝配色，嵌入 4 张真实图表，数字取自 final_numbers.md） | results + figures | `team/presentation/5分钟答辩PPT.pptx`（9 页） |
| `run_full_sample.sh` / `run_final_chain.sh` | 自动接力链：等打分完成 → 缓存聚合 → 行情补拉 → 全链路重估 → 数字快照 | — | 过程日志 |
| `prompts/llm_scoring_prompt_v1.md` | LLM 判读系统提示词 v1 存档（判读标准的正式版本） | — | — |

## 与论文的对应关系

| 论文位置 | 产物文件 | 生成脚本 |
|---|---|---|
| 表1 度量对比 | `results/dict_vs_llm_correlation.txt`、`ai_adoption_dict.csv` | 04_dict_baseline |
| 表2/表3 主结果 | `results/table_deepseek_groups.csv`、`table_deepseek_regression.csv` | 06_car_analysis |
| 表4 横截面 | `results/table4_cross_section.csv` | 07_cross_section |
| 表5 安慰剂 | `results/table_placebo_groups.csv`、`table_placebo_regression.csv` | 06_car_analysis |
| 表6 稳健性 | `results/table6_robustness.csv` | 10_robustness |
| 表7 诊断 | `results/table7_diagnostics.csv` | 13_diagnostics |
| 图1–图4 | `results/figures/*.png` | 09_make_figures |
| 全文数字快照 | `results/final_numbers.md` | 14_final_report |
| 度量审计 | `data/processed/llm_raw/*.json`（每个判读的原始模型响应 + 证据摘录） | 04_llm_scoring |

## 环境与依赖

- Python 3.13（3.10+ 均可）；第三方依赖共 **9 个**：
  `pandas numpy scipy statsmodels pypdf requests matplotlib openpyxl python-pptx`（前者 8 个为数据分析链，末项仅用于生成答辩 PPT；无 jieba/akshare/tushare 等重依赖；版本冻结见 `requirements.txt`）
- LLM：智谱 GLM-4-Flash（免费额度）。API Key 放在 `research-package/.env`：`GLM_API_KEY=...`（**已 gitignore，不入库**）
- 论文 PDF 生成额外需要本机 Google Chrome（无头打印）；该步骤不参与数据分析，结果表与图不依赖它
- 联网需求：巨潮/东财/腾讯/新浪公开接口（均为无需鉴权的公开行情与公告数据）

## 一键复现

见 `../reproducibility/REPRODUCE.md`（含环境安装、执行顺序、随机种子、成本与限流应对、已知实现细节的诚实披露）。

## 复现红线

- `data/raw/` 只进不改；所有加工产物由脚本生成。
- 每个实验阶段完成即 git commit（时间戳即过程证据），禁止最后一晚一次性打包。
- 论文每个数字都能在 `results/*.csv` 中找到对应来源；图表数值一律由 CSV 生成，AI 不手填数字。

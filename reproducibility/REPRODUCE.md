# REPRODUCE 可复现说明（Reproducibility Guide）

> 交付物 #7。目标：换一台干净机器，按本文档从原始数据跑出论文主表的每一个数字。
> 本版为 2026-11-21 提交前终版，与 `code/` 实际 20 个脚本一一对应。

## 1. 环境要求

- **Python 3.13.12**（3.10+ 均可，本机版本）
- 第三方依赖共 **9 个**（无 jieba/akshare/tushare 等重依赖）：

```
pandas  numpy  scipy  statsmodels  pypdf  requests  matplotlib  openpyxl  python-pptx
```

安装：`pip install -r requirements.txt`（清华 TUNA 镜像可加速）。`python-pptx` 仅用于第 9 项答辩 PPT（备用件），不参与数据分析。`scipy` 被 04_dict_baseline / 06_car_analysis / 10_robustness / 13_diagnostics 使用，虽为 statsmodels 的传递依赖，仍显式冻结以保证干净环境可复现。

- **LLM API**：智谱 GLM-4-Flash（`glm-4-flash`，永久免费额度）。Key 写入 `research-package/.env`：
  `GLM_API_KEY=<你的key>`（该文件已 gitignore）
- **论文 PDF**（可选）：本机 Google Chrome（无头打印 `16_md_to_pdf.py`）；不参与数据分析。
- 联网需求：巨潮资讯网（cninfo.com.cn）、东方财富、腾讯财经（web.ifzq.gtimg.cn）、新浪财经公开接口；均无需鉴权。

## 2. 目录结构

```
research-package/
├── code/                      # 19 个脚本 + 2 个 shell 接力链（编号即执行顺序）
│   ├── data_client.py         # 公开数据薄客户端（双通道+限速+断点续跑）
│   ├── figstyle.py            # 图表样式（橙蓝配色/中文字体栈/300dpi）
│   ├── 01_fetch_stock_list.py # A股清单
│   ├── 02_download_reports.py # 年报PDF下载（cninfo主/EM备）
│   ├── 03_extract_mda.py      # MD&A提取+关键词段落表
│   ├── 04_llm_scoring.py      # GLM逐段三分类+公司级聚合（容错读+原子写+解析兜底）
│   ├── 04_dict_baseline.py    # 73词词典基线
│   ├── 05_fetch_prices.py     # 行情（DeepSeek窗+安慰剂窗，并发）
│   ├── 06_car_analysis.py     # 市场模型+CAR（主检验+安慰剂）
│   ├── 07_cross_section.py    # 横截面回归
│   ├── 09_make_figures.py     # 图表 fig1–fig4
│   ├── 10_robustness.py       # 四类替代度量稳健性
│   ├── 11_make_citation_checklist.py  # 文献核实清单 xlsx
│   ├── 12_aggregate_partial.py# 从缓存重建最终样本（排除重复缓存）
│   ├── 13_diagnostics.py      # 学术诚信诊断 D1–D4
│   ├── 14_final_report.py     # 论文数字快照（程序化）
│   ├── 15_patch_missing.py    # 缺失/损坏缓存精准补打
│   ├── 16_md_to_pdf.py        # 论文提交版 PDF
│   ├── 17_package_check.py    # 提交前全包自检
│   ├── 18_make_defense_ppt.py  # 5分钟答辩PPT（交付物#9备用件）
│   ├── run_full_sample.sh / run_final_chain.sh  # 自动接力链
│   ├── requirements.txt / README.md
│   └── prompts/llm_scoring_prompt_v1.md   # 判读提示词v1存档
├── data/
│   ├── raw/annual_reports/    # 原始年报PDF（只进不改）
│   ├── processed/             # 脚本生成的中间/最终数据
│   │   ├── llm_raw/           # ⭐ 每次LLM判读的原始响应JSON（审计证据）
│   │   └── pilot96/           # 试点96家与中间901家原始表（复现对照）
│   └── prices/                # deepseek/ placebo/ 两窗口行情
├── results/                   # 论文表格CSV + figures/ + 数字快照 + 自检报告
├── paper/                     # manuscript.md（工作稿）+ manuscript.pdf（提交件）+ references.md
├── references/                # 引用核验表 + 人工核实清单 + 73词词典原文抄录
├── team/  agent_log/  reproducibility/   # 分工声明 / Agent日志 / 本文档
└── 00_RESEARCH_PACKAGE_CHECKLIST.md      # 交付物总控清单
```

## 3. 一键复现流程

```bash
cd research-package/code

# 1) 股票清单
python3 01_fetch_stock_list.py            # → stock_list.csv (5565只)

# 2) 年报下载（断点续跑；首次全量数小时，受巨潮限流影响）
python3 02_download_reports.py --sample all
#   已提供下载数据快照时此步可跳过（重跑自动跳过已下载）

# 3) MD&A 提取（纯CPU，约15家/分钟）
python3 03_extract_mda.py                 # → mda_text/ + mda_paragraphs.csv (27821段/2082家)

# 4) LLM 打分（GLM-4-Flash；断点续跑按 llm_raw/*.json 缓存）
python3 04_llm_scoring.py --workers 16    # → ai_adoption_llm.csv + ai_adoption_firm.csv
#   ⚠️ 全量约2.8万段；实测吞吐60–270段/分钟（API延迟瓶颈，曾触发429限流需降并发）
#   ⚠️ 成本：GLM-4-Flash免费额度内，全程数元以内
#   若个别缓存半写/解析失败：python3 15_patch_missing.py 精准补打缺失段
#   最终样本建议用 12 从缓存一致性重建（自动排除724个历史重复缓存）：
python3 12_aggregate_partial.py           # → 最终 N=2082 / 27821段 / 覆盖率100%

# 5) 词典法基线（纯CPU，秒级）
python3 04_dict_baseline.py               # → ai_adoption_dict.csv + 对比统计

# 6) 行情拉取（两窗口，6并发；已有文件自动跳过）
python3 05_fetch_prices.py --codes-from firm --workers 6
#   最终：deepseek 2210家 / placebo 2118家落盘，异常=新股/长期停牌

# 7) 事件研究主分析 + 安慰剂（一次跑完两个事件）
python3 06_car_analysis.py                # → car_panel_* / table_deepseek_* / table_placebo_*

# 8) 横截面回归
python3 07_cross_section.py               # → table4_cross_section.csv

# 9) 图表
python3 09_make_figures.py                # → results/figures/fig1–fig4（5张）

# 10) 稳健性 / 诊断 / 数字快照
python3 10_robustness.py                  # → table6_robustness.csv
python3 13_diagnostics.py                 # → table7_diagnostics.csv + diagnostics_report.txt
python3 14_final_report.py                # → final_numbers.md（论文全部数字的机器可读来源）

# 11) 论文 PDF 与交付自检（可选）
python3 16_md_to_pdf.py                   # → paper/manuscript.pdf
python3 17_package_check.py               # → results/final_package_check.md
python3 18_make_defense_ppt.py            # → team/presentation/5分钟答辩PPT.pptx（第9项备用件）
```

> 步骤 2/4/6 依赖外部接口，若接口变更或限流，`data/` 中已落盘的原始 PDF、LLM 缓存与行情 CSV 即为重跑起点；步骤 5、7–10 全部为本地确定性计算，可在无网环境执行。

## 4. 随机种子与确定性

- 人工校验抽样（20段分层）固定 `random_state=42`（脚本内嵌）；数据合规抽查固定 `random.seed(21)`；均可复做。
- LLM 打分：`temperature=0`；**每次判读的原始响应均存档于 `data/processed/llm_raw/{para_id}.json`**（含逐字证据摘录与段落头部）——即使上游模型升级导致严格复现不可行，原始响应构成完整的审计证据链，也是一致性校验的底稿。
- 事件研究/回归为确定性计算，无随机性。

## 5. 关键实现细节（诚实披露）

1. **数据源容灾**：巨潮对高频请求限流（403/连接池错误），`02` 采用巨潮主通道+东财公告备通道，指数退避重试；`05` 行情以腾讯为主（前复权+日期区间）、新浪兜底（datalen=1500 不复权）、东财最后兜底。指数代码 `000300` 沪市前缀 `sh`（曾修复的 bug：交易所前缀规则不适用于指数）。
2. **成交额代理**：腾讯接口不提供成交额字段，`07` 的规模控制变量以 `成交量×收盘价` 合成（代码注释已注明）；新浪兜底通道为不复权数据，仅在腾讯失败时启用，并标记来源。
3. **词典 v1**：73 词 AI 词典以 Li, Diep & Li (2026, Energies 19(22):5413, 附录 Table A2) 为对齐目标 + 吴非等(2021) AI 子词表补充；**词表原文已逐词抄录于 `references/ai_dictionary_73words.txt`**（从论文 PDF 第 28–29 页 Table A2 提取，恰好 73 词）。
4. **剔除规则**：新股/长期停牌无法获得完整事件窗行情的公司剔除；最终样本 2,082 家中 DeepSeek 事件面板 2,067 家、安慰剂面板 1,911 家（论文 3.1 节披露）。
5. **断点续跑**：02（report_index 状态）、03（段落 ID 稳定：`{code}_{i}`，增量不漂移）、04（llm_raw 缓存，容错读 + `os.replace` 原子写）、05（按文件存在跳过）。04 曾因非原子写产生 2 个半写 JSON 导致续跑崩溃，已修复；另有 9 段因模型把中文引号写进证据摘录形成非法 JSON，已通过三级解析兜底处理（`evidence_quote` 置空、不伪造，该字段不参与 ai_index）。
6. **缓存去重**：早期 724 个"纯数字行号"格式缓存与现行 `{code}_{i}` 格式 100% 重复（涉及 43 家公司），`12` 只保留段落表中真实存在的 `para_id`，避免虚高计数。

## 6. 版本快照

- Python 3.13.12（WorkBuddy 内置解释器）
- 关键包版本：`pandas 3.1.1 / numpy 2.5.5 / scipy 1.18.1 / statsmodels 0.15.0 / pypdf 7.1.0 / requests 2.34.2 / matplotlib 3.11.2 / openpyxl 3.1.5 / python-pptx 1.0.2`（`requirements.txt` 冻结）
- LLM：glm-4-flash（智谱开放平台，2026-11-20/21 调用，temperature=0，提示词 v1）
- 数据拉取窗口：2026-11-20 ~ 11-21
- 代码版本：GitHub 仓库 `https://github.com/Iris17832/ai-adoption-event-study`（`git log` 含 19+ 次分阶段提交，时间戳即过程证据）

## 7. 已知限制

- 巨潮/东财限流导致下载需多次重试：5,565 家中 **3,460 家下载成功**、1,830 家限流未恢复、268 家确无 2023 年报（次新股/退市）、7 家杂项错误；下载顺序按股票代码，与公司特征无关（论文披露样本构造）。
- LLM 度量的可复现边界：同 key 重放可复现（缓存存档），跨模型版本不保证严格一致——这正是论文 5.3 节声明的内容。
- 行情接口的前复权口径以数据源（腾讯 qfq）为准；跨源核对（新浪）在 2025-01-20 收盘价上零差异，见 `results/data_compliance_precheck.md`。
- 安慰剂宽窗口存在前视偏差（以 2023 年报度量分组 2022 年事件），论文 5.4 节已如实披露并将因果权重置于短窗口。

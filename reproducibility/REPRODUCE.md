# REPRODUCE 可复现说明（Reproducibility Guide）

> 交付物 #7。目标：换一台干净机器，按本文档从原始数据跑出论文主表的每一个数字。
> 本版为 2026-11-21 终稿版，与 `code/` 实际脚本一一对应（旧版骨架已废弃）。

## 1. 环境要求

- **Python 3.13.12**（3.10+ 均可，本机版本）
- 第三方依赖（仅 7 个，无 jieba/akshare/tushare 等重依赖）：

```
pandas  numpy  statsmodels  pypdf  requests  matplotlib  openpyxl
```

安装：`pip install -r requirements.txt`（清华 TUNA 镜像可加速）

- **LLM API**：智谱 GLM-4-Flash（`glm-4-flash`，永久免费额度）。Key 写入 `research-package/.env`：
  `GLM_API_KEY=<你的key>`（该文件已 gitignore）
- 联网需求：巨潮资讯网（cninfo.com.cn）、东方财富、腾讯财经（web.ifzq.gtimg.cn）、新浪财经公开接口；均无需鉴权。

## 2. 目录结构

```
research-package/
├── code/                      # 全部脚本（编号即执行顺序）
│   ├── data_client.py         # 公开数据薄客户端（双通道+限速+断点续跑）
│   ├── 01_fetch_stock_list.py # A股清单
│   ├── 02_download_reports.py # 年报PDF下载（cninfo主/EM备）
│   ├── 03_extract_mda.py      # MD&A提取+关键词段落表
│   ├── 04_llm_scoring.py      # GLM逐段三分类+公司级聚合
│   ├── 04_dict_baseline.py    # 73词词典基线
│   ├── 05_fetch_prices.py     # 行情（DeepSeek窗+安慰剂窗）
│   ├── 06_car_analysis.py     # 市场模型+CAR（主检验+安慰剂）
│   ├── 07_cross_section.py    # 横截面回归
│   ├── 09_make_figures.py     # 图表（figstyle.py统一橙蓝配色）
│   └── prompts/llm_scoring_prompt_v1.md   # 判读提示词v1存档
├── data/
│   ├── raw/annual_reports/    # 原始年报PDF（只进不改）
│   ├── processed/             # 脚本生成的中间/最终数据
│   │   ├── llm_raw/           # ⭐ 每次LLM判读的原始响应JSON（审计证据）
│   │   └── ...
│   └── prices/                # deepseek/ placebo/ 两窗口行情
├── results/                   # 论文表格CSV + figures/
└── paper/                     # manuscript.md + references.md
```

## 3. 一键复现流程

```bash
cd research-package/code

# 1) 股票清单
python3 01_fetch_stock_list.py            # → stock_list.csv (5565只)

# 2) 年报下载（断点续跑；首次全量约需数小时，受巨潮限流影响）
python3 02_download_reports.py --sample all
#   已提供下载数据快照时此步可跳过（重跑会自动跳过已下载）

# 3) MD&A 提取（纯CPU，约15家/分钟）
python3 03_extract_mda.py                 # → mda_text/ + mda_paragraphs.csv

# 4) LLM 打分（GLM-4-Flash；断点续跑按 llm_raw/*.json 缓存）
python3 04_llm_scoring.py --workers 16    # → ai_adoption_llm.csv + ai_adoption_firm.csv
#   ⚠️ 全量约2.8万段；实测吞吐60-80段/分钟（API延迟瓶颈）
#   ⚠️ 成本：GLM-4-Flash免费额度内，全程<5元

# 5) 词典法基线（纯CPU，秒级）
python3 04_dict_baseline.py               # → ai_adoption_dict.csv + 对比统计

# 6) 行情拉取（两窗口并行；94/96→1341/1434成功率，异常=新股/停牌）
python3 05_fetch_prices.py --codes-from firm
python3 05_fetch_prices.py --codes-from sample   # 扩容样本

# 7) 事件研究主分析 + 安慰剂（一次跑完两个事件）
python3 06_car_analysis.py                # → table_deepseek_* / table_placebo_*

# 8) 横截面回归
python3 07_cross_section.py               # → table4_cross_section.csv

# 9) 图表
python3 09_make_figures.py                # → results/figures/fig1-fig4
```

## 4. 随机种子与确定性

- 人工校验抽样（20段分层）固定 `random_state=42`（脚本内嵌）。
- LLM 打分：`temperature=0`；**每次判读的原始响应均存档于 `data/processed/llm_raw/{para_id}.json`**（含逐字证据摘录与段落头部）——即使上游模型升级导致严格复现不可行，原始响应构成完整的审计证据链，也是人机一致性校验的底稿。
- 事件研究/回归为确定性计算，无随机性。

## 5. 关键实现细节（诚实披露）

1. **数据源容灾**：巨潮对高频请求限流（403/连接池错误），`02` 采用巨潮主通道+东财公告备通道，指数退避重试；`05` 行情以腾讯为主（前复权+日期区间）、新浪兜底（datalen=1500 不复权）、东财最后兜底。指数代码 `000300` 沪市前缀 `sh`（曾修复的 bug：交易所前缀规则不适用于指数）。
2. **成交额代理**：腾讯接口不提供成交额字段，`07` 的规模控制变量以 `成交量×收盘价` 合成（代码注释已注明）；新浪兜底通道为不复权数据，仅在腾讯失败时启用，并标记来源。
3. **词典 v1**：73 词 AI 词典以 Li, Diep & Li (2026, Energies 19(22):5413, 附录 Table A2) 为对齐目标 + 吴非等(2021) AI 子词表补充；终稿附录列全词表。词表对齐由人工终检（核验表登记）。
4. **剔除规则**：新股/长期停牌无法获得完整事件窗行情的公司剔除（96 家中剔除 2 家），在论文 3.1 节披露。
5. **断点续跑**：02（report_index 状态）、03（段落 ID 稳定：`{code}_{i}`，增量不漂移）、04（llm_raw 缓存）、05（按文件存在跳过）。

## 6. 版本快照（提交时终填）

- Python 3.13.12（WorkBuddy 内置解释器）
- 关键包：pandas / numpy / statsmodels / pypdf / requests / matplotlib / openpyxl（版本号提交时 `pip freeze` 冻结）
- LLM：glm-4-flash（智谱开放平台，2026-11-20/21 调用，temperature=0，提示词 v1）
- 数据拉取窗口：2026-11-20 ~ 11-21
- git commit hash：（终填）

## 7. 已知限制

- 巨潮/东财限流导致下载需多次重试，全量 5,565 家中约 2,300+ 家完成下载（下载顺序按股票代码，与公司特征无关；论文披露样本构造）。
- LLM 度量的可复现边界：同 key 重放可复现（缓存存档），跨模型版本不保证严格一致——这正是论文 5.3 节声明的内容。
- 行情接口的前复权口径以数据源（腾讯 qfq）为准。

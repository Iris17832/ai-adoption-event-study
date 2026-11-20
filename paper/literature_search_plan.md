# Literature Search Strategy · 文献调研计划（Phase 2）

> 阶段：文献调研（只做检索计划与任务分派，不撰写 Literature Review）。
> 编制：Research Brain，2026-11-20。语境基准：`PROJECT_OVERVIEW.md`（新建）+ `COMPETITION_BRIEF.md`。
> **诚实声明**：截至本计划编制时，Research Brain 已完成的检索仅限此前的引用核验（见 `references/citation_verification.md`，30 条）；**尚未**系统执行本计划中的检索式，也**未实际登录**知网/WoS/SciMaster。所有"待检索"标注均为待办，不得视为已完成。
> 团队分工：张锦悦执行检索/下载；孔佳怡负责最终核验登记（预计 30–45 分钟）；矩阵分析与精读由 Research Brain 完成。

---

## 〇、研究问题回顾（一段话）

企业 AI 采纳强度（LLM 测量年报 MD&A）是否被资本市场定价？以 DeepSeek-R1 发布（2025-01-20）为外生冲击做事件研究，对比词典法基线，回答 RQ1（度量有效性）/ RQ2（CAR 差异）/ RQ3（横截面机制）。

---

## 一、分析研究问题

### 1.1 涉及学科与领域

| 学科 | 具体领域 | 对本研究的作用 |
|------|---------|---------------|
| 金融学（资产定价/公司金融） | 事件研究、信息定价、技术冲击定价 | 主战场：CAR 设计与假设推导 |
| 会计/财务披露 | MD&A 文本分析、信息披露质量 | 度量载体与文本来源 |
| NLP/计算社会科学 | LLM 文本标注、词典法、文本度量 | 测量工具（RQ1 核心） |
| AI 经济学 | AI 生产率、AI 劳动力市场、企业 AI 采纳 | 机制假设与横截面变量来源 |
| 计量方法 | 事件研究计量、横截面回归 | 估计与稳健性 |

### 1.2 RQ 拆解为 6 个检索主题（T1–T6）

| 编号 | 检索主题 | 对应 RQ | 核心追问 |
|------|---------|---------|---------|
| T1 | 企业 AI 采纳的文本度量（词典法 vs LLM 法） | RQ1 | 别人怎么测企业 AI？词典与 LLM 谁更准？ |
| T2 | AI 采纳的市场定价后果（股票回报/企业价值） | RQ2/RQ3 | AI 采纳和股价之间已有哪些因果/相关证据？ |
| T3 | LLM/大模型发布冲击与金融市场 | RQ2 | DeepSeek/ChatGPT 发布事件已被怎么研究？ |
| T4 | 事件研究方法与市场模型 | 方法 | CAR 估计的标准做法与常见陷阱 |
| T5 | LLM 作文本标注工具的有效性与规范 | RQ1 | LLM 打分的信效度如何论证？ |
| T6 | AI 经济学基础（采纳率、生产率、机制） | 假设背景 | 为什么高采纳企业理应被冲击定价？ |

### 1.3 与本研究最接近的方向（第一优先级）

**T2 × T3 的交叉带**："企业 AI 采纳 × 股票回报 × 外生 AI 冲击"。已知该交叉带内最接近的确认文献：
- Zhang, Yi & Cai (2026, Sustainability 18(17):9193)：词典法测 AI 采纳（绿生产力，非定价）
- Babina et al. (2024, JFE)：简历法测 AI 投资 → 市值增长（非事件研究）
- Taboga (2026, arXiv:2610.30886)：DeepSeek R1 发布的市场反应（宏观事件，无企业 AI 采纳度量）

**尚未定位、必须第一轮找到的疑似最近邻**（备案表线索，未核实）：
- Notre Dame 团队 "AI and Law of One Price"（A-H 溢价，中国 LLM 冲击）→ 检索式 S1 重点
- SMU 团队 ChatGPT 断网事件研究 → 检索式 S2 重点

> 若这两篇被证实已做"企业 AI 暴露 × 中国 LLM 冲击定价"，则我们的增量收窄为"**LLM 度量 vs 词典基线的测量对比 + 全样本 MD&A 强度分层**"——届时需重新评估创新性表述，不得强行宣称首创。

### 1.4 需要重点了解的已有研究

1. **逐段精读**（决定我们的定位表述）：上述 3 篇确认最近邻 + 2 篇待定位最近邻
2. **词表级复用**：Li, Diep & Li (2026) 的 73 词词典全文（抄 Table A2，替换我们的 v1 词表）
3. **设计级借鉴**：事件研究窗口/基准选择（T4）、LLM 标注信效度论证套路（T5：Gilardi、Ziems）
4. **机制级引用**：AI 生产率/劳动力证据（T6）用于假设推导，只需摘要级理解
5. **规避级了解**：撞题区（崩盘风险、股价同步性）只需知道其结论与差异点，不必精读

---

## 二、检索策略（Keyword List & Boolean 表达式）

### 2.1 英文关键词及同义词

| 概念组 | 核心词 | 同义词/变体 |
|--------|--------|------------|
| C1 AI 采纳 | artificial intelligence adoption | AI adoption; AI investment; firm-level AI; generative AI adoption; AI exposure; AI uptake |
| C2 AI 技术词 | generative artificial intelligence | large language model(s), LLM; ChatGPT; DeepSeek; GPT |
| C3 文本度量 | textual analysis | text-based measure; dictionary method; word frequency; MD&A; management discussion and analysis; annual report disclosure; 10-K |
| C4 LLM 标注 | LLM annotation | LLM text classification; ChatGPT annotation; few-shot prompting; text-as-data |
| C5 股票回报 | stock returns | abnormal returns; cumulative abnormal return(s), CAR; stock price reaction; market reaction; firm value; asset pricing |
| C6 事件研究 | event study | market model; event window; announcement effect; exogenous shock |
| C7 AI 冲击 | AI shock | technological shock; AI breakthrough; model release; compute shock |

### 2.2 中文关键词

- C1：人工智能采纳 / 企业人工智能应用 / 企业数字化转型（广义对照）/ 智能化转型
- C2：大语言模型 / 生成式人工智能 / 大模型 / DeepSeek / ChatGPT
- C3：年报文本 / 管理层讨论与分析 / 文本分析 / 词频 / 词典法
- C5：股票回报 / 累计超额收益 / 事件研究 / 市场反应 / 股价反应 / 企业价值
- C6：外生冲击 / 准自然实验

### 2.3 Boolean 检索式（S1–S6）

> 适用 Web of Science / Scopus / Semantic Scholar 高级检索；Google Scholar 不支持嵌套布尔，用简化版（括号内改引号短语）。

- **S1（最近邻·最高优先）**：`("artificial intelligence" OR "AI" OR "generative AI" OR LLM) AND (adoption OR exposure OR investment) AND ("stock return*" OR "abnormal return*" OR "asset pricing" OR "stock price" OR "firm value")`
- **S2（冲击事件）**：`(DeepSeek OR ChatGPT) AND ("event study" OR "stock return*" OR "market reaction" OR "asset pricing")`
- **S3（度量方法·英文）**：`("annual report" OR "MD&A" OR "10-K") AND ("artificial intelligence" OR "AI adoption") AND (dictionary OR "textual analysis" OR "large language model")`
- **S4（LLM 标注规范）**：`("large language model*" OR ChatGPT OR GPT) AND (annotation OR "text classification" OR labeling) AND ("social science" OR finance OR economics)`
- **S5（中文主检索式·知网）**：主题 = (人工智能 + 大模型 + 生成式人工智能) AND (年报 + 文本分析 + 管理层讨论与分析) AND (股价 + 股票回报 + 市场反应 + 事件研究)
- **S6（中文撞题侦察·知网）**：主题 = (人工智能应用) AND (股价崩盘 + 股价同步性 + 信息披露)，目的=确认撞题区最新动态、防止立项撞车

### 2.4 推荐数据库与检索平台

| 平台 | 用途 | 说明 |
|------|------|------|
| SciMaster（培训指定工具） | 第一轮主力检索 | 由张锦悦操作执行，本计划检索式直接可用 |
| Google Scholar | 覆盖面兜底 + 引用追踪（"被引"顺藤摸瓜） | 简化布尔；适合追 Taboga 2026 的引用者 |
| Semantic Scholar | 语义检索 + TLDR + 引用图谱 | 免登录；适合 S1/S2 |
| OpenAlex（开放 API） | 元数据核验 + 批量导出 | 免费、无账号，可脚本化 |
| 中国知网 CNKI | 中文文献（S5/S6） | 需校园网/账号；由张锦悦执行 |
| arXiv / SSRN / NBER | 工作论文（AI 金融市场方向新文献多在此） | 直接站内搜 DeepSeek / asset pricing |
| MDPI 官网 | A 组对标论文全文与词表 | 开放获取 |

### 2.5 时间范围

- **核心窗**：2020–2026（AI 采纳度量与定价文献几乎全部在此区间）
- **必备窗**：2025–2026（DeepSeek 相关研究只能在此）
- **方法经典不限年份**：MacKinlay 1997、Brown & Warner 1985、Loughran & McDonald 2011
- 知网中文：2021–2026 优先（年报文本度量范式自吴非等 2021 兴起）

### 2.6 纳入与排除标准

**纳入（全部满足）**：
1. 对象为企业层面 AI 采纳/暴露，或 AI 技术冲击的市场反应（T1–T3 主题命中）
2. 载体为同行评审期刊/会议，或 arXiv/NBER/SSRN 权威工作论文系列，或 CSSCI/北大核心中文期刊
3. 有 DOI 或稳定 URL，元数据可核验
4. 提供可提取的方法/数据描述（能进 Literature Matrix）

**排除（任一即弃）**：
1. 纯算法/纯 NLP 技术论文，无企业或金融情境
2. 主题仅沾边（如医疗 AI、教育 AI、AI 治理综述）
3. 无署名/无出处自媒体与博客文章（新闻可作为背景，不入矩阵）
4. 元数据无法核验或全文完全无法获取
5. 与已确认撞题研究完全同构且无新信息量（只登记不入矩阵）

> **优先级原则**：宁精勿滥。与 RQ 直接相关的每多 1 篇价值大于泛相关 10 篇。第一轮宁可将 S1 命中全部纳入候选，也不把 S6 侦察出的撞题文凑数。

---

## 三、文献阅读计划（五类及价值）

| 类别 | 文献范围（对号 citation_verification.md 编号） | 阅读深度 | 对本研究的价值 |
|------|------|---------|---------------|
| ① 基础理论与经典 | A8 Babina 2024；B3 L&M 2011；B4 Hassan 2019；B1/B2 事件研究经典；C8 Agrawal 2019 | 精读方法章 | 锚定"企业 AI 度量→经济后果"的范式合法性；事件研究设计规范；假设推导的理论地基 |
| ② 与 RQ 最接近 | A1/A2/A3/A4 MDPI 系列；A7 Taboga 2026；A6 GADM 2026；A5 IREF 2026；＋待定位的 ND/SMU 两篇 | **逐段精读 + 矩阵必填** | 直接决定我们的差异化表述与创新点边界；A3 提供词表；Taboga 提供冲击识别先例 |
| ③ 方法与模型 | B6 Gilardi 2023；B7 Ziems 2024；B8 DeepSeek-R1 技术报告；B9/B10/B11 中文文本度量 | 精读 prompt/信效度节 | RQ1 的论证武器：LLM 打分有效性证据链、few-shot 设计规范、词典基线中文范式 |
| ④ 最新进展 | C1–C3、C9 Brynjolfsson/Acemoglu/Jones 2025–2026；S1/S2 检索新增 | 摘要 + 结论 | 引言与讨论部分时效性；防止引用陈旧 |
| ⑤ 不同结论 | 撞题区（赵晶等 2025 等）+ 检索中发现的"AI 未被定价/AI 泡沫"类论文 | 摘要 + 差异点 | 反方证据：审稿人视角反向否定；讨论部分必须回应的异见 |

> 精读判定规则：正文主张只能来自①②③类的全文精读，不得仅凭摘要归纳一篇论文的全部内容（本计划红线）。

---

## 四、Literature Matrix 设计

### 4.1 字段（12 列 + 管理列）

| 字段 | 说明 |
|------|------|
| Matrix ID | M01, M02…（与核验表编号互相引用） |
| Paper Title | 原文标题 |
| Authors | 全部作者 |
| Year | 年份 |
| Journal / Conference | 出处（卷期页） |
| DOI / URL | 可核验链接 |
| Research Question | 该文研究问题（一句话） |
| Dataset | 样本、来源、时间跨度、国家 |
| Methodology | 度量方法 + 识别策略 |
| Experimental Settings | 窗口/控制变量/稳健性设计 |
| Main Findings | 核心结果（含效应方向与量级） |
| Limitations | 作者自述 + 我们判读的局限 |
| Relevance to Our Research | ①对标/②词表/③方法/④背景/⑤反方 + 与我们 RQ1/2/3 的对应 |
| 状态 | 待精读 / 精读中 / 已入矩阵；信息来源标注【全文】【摘要级】 |

### 4.2 预填示例（3 行，信息来源均为已核验元数据；Main Findings 标注【摘要级】者待全文精读后修订）

| 字段 | M01 | M02 | M03 |
|------|-----|-----|-----|
| Title | Can Artificial Intelligence Enhance Corporate Green Productivity? Evidence from Chinese Listed Firms | Artificial Intelligence, Firm Growth, and Product Innovation | The Reaction of Financial Markets to the Releases of DeepSeek R1 and Kimi K3: A Critical Analysis |
| Authors | Zhang, Y.; Yi, Y.; Cai, Z. | Babina, T.; Fedyk, A.; He, A.; Hodson, J. | Taboga, M. |
| Year | 2026 | 2024 | 2026 |
| Journal | Sustainability, 18(17): 9193 | Journal of Financial Economics, 151: 103745 | arXiv:2610.30886 |
| DOI/URL | 10.3390/su18179193 | 10.1016/j.jfineco.2023.103745 | 10.48550/arXiv.2610.30886 |
| RQ | AI 采纳是否提升企业绿色生产率 | 企业 AI 投资是否驱动增长与创新 | DeepSeek R1/Kimi K3 发布如何影响金融市场 |
| Dataset | 中国 A 股 4079 家，2015–2024【摘要级】 | 美国上市公司员工简历，AI 投资度量【摘要级】 | 事件窗口指数与个股收益（半导体/数据中心/中国 AI 实验室）【摘要级】 |
| Methodology | MD&A 词典法（73词+jieba）测 AI 采纳；51job 招聘数据收敛效度 r=0.428【摘要级】 | 简历文本→AI 投资；大学 AI 人才供给作 IV【摘要级】 | 描述性事件窗口收益比较【摘要级】 |
| Settings | 待精读 | 待精读 | 待精读 |
| Main Findings | AI 采纳与绿色生产率正相关【摘要级，待精读】 | AI 投资企业销售/雇佣/市值增长更快，经产品创新渠道【摘要级，待精读】 | DeepSeek R1 冲击集中于算力供应链；开源模型重配租金而非消灭【摘要级，待精读】 |
| Limitations | 未做市场定价；词典法测量误差未与 LLM 对照（我们的切入点） | 美国样本；无中国证据 | 描述性、无正式统计推断（作者自述）【摘要级】 |
| Relevance | ①对标+②词表来源 → RQ1 | ①对标（企业 AI→市值，非事件研究）→ RQ2 | ①对标（冲击识别先例）→ RQ2 |
| 状态 | 全文可得（MDPI 开放），待精读 | 全文可得，待精读 | arXiv 开放，待精读 |

### 4.3 存放

- 主文件：`research-package/references/literature_matrix.csv`（UTF-8，13 列表头见 4.1）
- 目标规模：15–20 篇（培训第三讲标准），上限 25 篇
- 与 `citation_verification.md` 联动：矩阵里每一行必须已有核验登记，未核验不入矩阵

---

## 五、下一步行动计划（第一轮）

### 5.1 检索量目标

| 环节 | 数量 | 说明 |
|------|------|------|
| 检索式命中（S1–S6 去重前） | 不设上限 | 原始导出留档 |
| 去重 + 排除标准筛选后候选池 | **40–60 篇** | 进入标题/摘要级初筛 |
| 精读并入矩阵 | **15–20 篇** | 已核验 30 条中预计 15–18 条直接入矩阵，新检索补 5–10 条 |
| 其中②类（最近邻） | ≥6 篇 | 含必须定位的 ND/SMU 两篇（见 5.2） |

### 5.2 优先下载与阅读清单（Top 10）

| 优先级 | 文献 | 为什么先读 |
|--------|------|-----------|
| P0 | Li, Diep & Li 2026（Energies 19(22):5413） | 抄 73 词词表（Table A2）→ 直接升级词典基线代码 |
| P0 | Zhang, Yi & Cai 2026（Sustainability 18(17):9193） | 头号对标，逐段精读其度量+验证设计 |
| P0 | Taboga 2026（arXiv:2610.30886） | 冲击识别先例，全文开放 |
| P0 | S1 检索命中中疑似 ND/SMU 两篇 | 决定创新性边界，本轮**必须**给出定位结论（找到/证伪） |
| P1 | Gilardi 2023（PNAS） + Ziems 2024（CL） | RQ1 论证套路：LLM 标注信效度写法 |
| P1 | Babina 2024（JFE） | 企业 AI→市值的最强证据，假设推导引用 |
| P2 | L&M 2011 + Hassan 2019 | 文本度量方法章 |
| P2 | 吴非等 2021（管理世界） | 中文年报词频法标准表述 |

### 5.3 各平台操作指引（张锦悦执行）

1. **SciMaster**：按 S1–S4 检索式逐条执行，导出含 DOI 的结果列表
2. **Semantic Scholar / OpenAlex**：对 S1/S2 补充语义检索；OpenAlex 可用 `https://api.openalex.org/works?search=...` 批量取元数据
3. **Google Scholar**：对 Taboga 2026 做"被引"追踪（2026-10 挂出，引用者大概率是同方向新作）；对 "DeepSeek asset pricing" 做相关页追踪
4. **arXiv/SSRN**：站内搜 `DeepSeek + stock/asset pricing`、`ChatGPT + event study`，限 2025–2026
5. **知网**：S5/S6 两条中文检索式，限 2021–2026 + CSSCI/核心
6. **诚实记录**：每条检索式记录"平台 + 日期 + 命中数 + 导出文件名"，写入检索日志（真实检索过程本身就是 Agent 工作流得分项）

### 5.4 真实性核验（孔佳怡）

1. 每篇候选：DOI 能否解析到与登记一致的标题/作者/期刊（doi.org 粘贴即可）
2. 工作论文（arXiv/SSRN/NBER）：核对编号与作者主页
3. 中文文献：知网页面核对卷期页码
4. 结果写回 `citation_verification.md` 状态列；状态非"已核验"的文献不进矩阵、不进正文
5. **AI 检索摘要中的引用一律视为线索**，必须经上述流程

### 5.5 论文原文交付方式（给我做下一步分析）

- 存放：`research-package/references/pdfs/`
- 命名：`[MatrixID预留]_FirstAuthor_Year_ShortTitle.pdf`，例 `Zhang_2026_AI_Green_Productivity.pdf`
- 同时更新 `literature_matrix.csv`（标题/作者/年份/DOI 先填，后五列留空）
- 交付后告诉我"PDF 已放入"，我会：① 提取全文 → ② 精读并回填矩阵 5 列 → ③ 输出单篇精读卡片（RQ/数据/方法/发现/局限/对我们的启示）→ ④ 汇总成研究缺口与创新性评估
- 拿不到 PDF 的文献：提供稳定链接亦可，开放获取优先

---

## 六、红线自查（本计划的合规性）

- ✅ 未编造任何论文/作者/DOI：文中出现的具体文献全部来自已核验的 `citation_verification.md`
- ✅ 未声称已完成本计划中的数据库检索（明确标注"待执行"）
- ✅ ND/SMU 两篇标注为"未核实线索"，列为检索任务而非既定事实
- ✅ 矩阵预填行的【摘要级】信息显式标注，不冒充全文精读结论
- ✅ 未预设"本研究有创新性"——创新性待 S1/S2 命中与 ND/SMU 定位后重新评估
- ✅ 本文件只是检索计划，不撰写 Literature Review；等待实际检索结果提交

---

## 附：第一轮任务清单（Checklist）

- [ ] 张锦悦：SciMaster 执行 S1–S4，导出结果（目标：候选池 40–60 篇）
- [ ] 张锦悦：Google Scholar 追踪 Taboga 2026 被引 + arXiv/SSRN 站内搜
- [ ] 张锦悦：知网执行 S5/S6（限 2021–2026 + 核心）
- [ ] 张锦悦：下载 Top 10 优先文献 PDF → `references/pdfs/`
- [ ] 孔佳怡：核验候选池元数据 → 更新 citation_verification.md
- [ ] 张锦悦/孔佳怡：ND "AI and Law of One Price" 与 SMU ChatGPT 断网文定位结论（找到/证伪）
- [ ] 全员：向 Research Brain 提交 PDF 清单 + 矩阵 CSV 骨架 → 进入精读与 Literature Review 阶段

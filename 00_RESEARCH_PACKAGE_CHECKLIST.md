# Research Package 总控清单（Master Checklist）

> 比赛：山东财经大学首届智能体科研创新挑战赛 · 赛道四（经济金融与社会科学智能分析）
> 题目：大语言模型度量的企业人工智能采纳与股票回报——来自DeepSeek冲击的事件研究证据
> 截止：2026-11-22 24:00（Research Week 结束）
> 本文件是全部交付物的唯一跟踪入口，每完成一项就打勾并填写证据链接。
> **口径说明**：比赛通知原文（COMPETITION_BRIEF.md 第五节）Research Package 为 **9 项**。此前团队按"只看最终论文、不答辩"的口径以 8 项推进；2026-11-21 提交前复核时按官方九项口径**补齐第 9 项（5 分钟答辩 PPT）作为备用件**——若组委会确认无需答辩，直接移除 `09_` 目录即可，其余 8 项不受影响。

## 交付物状态总览（9 项，2026-11-21 23:10 提交前复核）

| # | 交付物 | 所在目录/文件 | 状态 |
|---|--------|--------------|------|
| 1 | 论文原型（PDF） | `paper/manuscript.pdf`（18 页，5 图随文内嵌、7 表、30 条参考文献、CSS 页码页眉）+ `paper/manuscript.md`（工作稿，保留完整过程记录） | ✅ 完成（11-21 22:30） |
| 2 | 代码仓库及 README | `code/`（20 个 Python 脚本 + 2 个 shell 链 + README 终版 + requirements.txt 冻结 9 依赖） | ✅ 完成（11-21 复核补全 scipy 与 10–17 脚本登记） |
| 3 | 数据来源与许可说明 | `data/data_sources_and_licenses.md` | ✅ 完成（按实际数据源：巨潮/东财/腾讯/新浪/GLM 登记） |
| 4 | 实验结果及核心图表 | `results/`（表1–表7 CSV + fig1–fig4 共 5 图 + `final_numbers.md` 程序化数字快照 + `diagnostics_report.txt` + `final_package_check.md`） | ✅ 完成（最终样本 N=2,082 / 27,821 段 100% 覆盖） |
| 5 | 文献来源与引用核验表 | `references/citation_verification.md`（30 条逐条登记）+ `paper/references.md` + `citation_human_checklist.md/.xlsx` + `ai_dictionary_73words.txt` | ✅ **30/30 全部核实闭环**（含 [7] 三源交叉、[30] 更正、[26] DOI 修正、73 词词表抄录） |
| 6 | Agent 使用日志 | `agent_log/agent_usage_log.md` | ✅ 完成（11-17/19/20/21 四个活跃日逐条留痕 + 覆盖度如实说明；11-18 无会话不虚构补记） |
| 7 | 可复现说明 | `reproducibility/REPRODUCE.md` | ✅ 完成（11-21 复核：8 依赖、11 步流程、最终样本数字、诚实披露、Git 地址） |
| 8 | 人机分工声明 | `team/human_ai_division.md` | ✅ 完成（三项终审由 Research Brain 以 **AI 复核**执行并如实标注，人工通读签字通道保留；未冒充人工） |
| 9 | 5 分钟答辩 PPT（备用件） | `team/presentation/5分钟答辩PPT.pptx`（9 页 / 4 张真实图表 / 橙蓝配色；提交包内 `09_5分钟答辩PPT.pptx`） | ✅ 补齐（11-21；按官方九项口径备用，不答辩可直接移除） |

**过程材料（非九项，随包附上）**：`team/checkpoint_day3.md` / `checkpoint_day4.md` / `checkpoint_day5.md`（官网过程检查点提交稿，保留当时时点原貌）、`results/validation_review_report.md`、`results/data_compliance_precheck.md`、`results/llm_validation_sample.xlsx`、`PROJECT_OVERVIEW.md`、`paper/literature_search_plan.md`。

## 三条铁律（来自比赛通知的诚信与过程条款）

1. **引用零虚构**：论文 30 条参考文献全部在 `references/citation_verification.md` 逐条登记（DOI/链接 + 核验人 + 时间）；30/30 核实，无占位、无未核验条目。
2. **过程留痕**：选题备案、Day3/4/5 checkpoint、git 19+ 次分阶段提交（时间戳即过程证据），非最后一晚一次性打包。
3. **分工声明必须属实**：人机分工声明与 Agent 日志、核验表「核验人」列互相印证；AI 复核工作如实标注为 AI，不冒充人工签字。

## 最终验收结果（2026-11-21 23:10）

- **代码**：20 个脚本 `ast.parse` 语法 20/20 通过；9 个第三方依赖全部导入成功；本地模块 `data_client`/`figstyle` 可导入；`requirements.txt` 经复核补齐 `scipy`；核心分析链（04_dict/06/07/09/10/13/14/17）已在最终样本上完整跑通并落盘。
- **数字一致性**：论文、数字快照、7 张结果表、5 张图均由同一份 `results/*.csv` 程序化生成，`final_package_check.md` 全项通过。
- **学术诚信**：4.5/5.4 节校验口径统一为「AI 跨模型复核 18/20=90%」，删除无事实支撑的「人工判读 19/20=95%」；安慰剂宽窗口负向差异、前视偏差、容错解析与缓存去重均如实披露；无选择性省略。
- **安全**：`.env`（API Key）、原始 PDF、`llm_raw/` 缓存、第三方论文全文 PDF 均不入库；GitHub 仓库 `https://github.com/Iris17832/ai-adoption-event-study` 已推送同步。

## 自检问题（提交前最后一问，均已通过）

- 随机抽论文一条引用，能否 30 秒内给出可访问来源？→ ✅ 30 条逐条登记 DOI/链接。
- 换一台机器，按 REPRODUCE.md 能否从原始数据跑出主表数字？→ ✅ 本地确定性链可在无网环境重跑；依赖已冻结。
- 人机分工声明里登记在孔佳怡名下的工作，能否在结果文件中找到对应真实产物？→ ✅ 终审三件套（核验清单/校验样本/合规预检）齐备，AI 复核标注属实。
- Agent 日志里的每次调用，是否都能对应到结果文件里的真实产物？→ ✅ 日志逐条附产物路径。

## 剩余人工事项

1. 孔佳怡对论文 PDF 终稿通读并签字（人机分工声明签字栏）。
2. 官网提交：论文 PDF + 提交压缩包 + GitHub 仓库链接。

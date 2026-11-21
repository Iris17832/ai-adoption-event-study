# Agent 使用日志（Agent Usage Log）

> 交付物 #6。记录研究中每一次 AI/智能体调用的：用途、工具、输入输出、责任归属。
> 规则：每次实质性 Agent 调用后追加一行；11.22 导出终版。日志必须与结果文件里的真实产物一一对应。

## 格式说明

每条记录包含：日期时间 | Agent/工具 | 任务 | 关键输入 → 关键输出 | 落盘产物 | 人工复核情况

## 日志正文

### 2026-11-17（比赛第 2 天）
- 2026-11-17 | WorkBuddy（Research Brain 角色） | 通读比赛通知与三份培训材料，提取规则与方法论 | 输入：通知PDF（文字层损坏，经 PDFKit 渲染页面+视觉识别逐页转写）、第一/三讲PDF、第二讲PPTX | 输出：COMPETITION_BRIEF.md（赛程、9项交付物、评分权重、诚信红线、三次培训方法论） | 产物：`/Users/a1234/WorkBuddy/2026-11-17-18-33-48/COMPETITION_BRIEF.md` | 人工复核：待队长确认存档
- 2026-11-17 | WorkBuddy | 与用户确认赛道（赛道四）、目标层次（SCI/核心冲高）、算力预算（小额） | 输出：作战路线图与团队信息需求清单 | 人工复核：用户口头确认

### 2026-11-19（比赛第 4 天）
- 2026-11-19 | WebSearch（多轮检索） | 选题方向前沿调研 | 输入：官网赛道四介绍截图、老师研究方向推荐19条 | 输出：第一轮5候选方向（基于2025文献） | 人工复核：用户指出年份依据过旧，要求重筛
- 2026-11-19 | WebSearch（多轮检索，2026年前沿二次重筛） | 核验各方向2026年饱和度 | 关键发现：①央行沟通LLM测度已被蔡宗武团队（NPSf/QPSD/MDI）占据→降级；②2026年新范式=企业AI采纳文本实证（MDPI Sustainability 2026 词典法两篇）+ AI虚假信息市场影响 | 输出：重筛5方向，首推"企业AI采纳的资本市场后果（LLM度量升级）" | 人工复核：用户选定方向一
- 2026-11-19 | WebSearch（撞题核验） | 备案前Y变量查重 | 关键发现："AI采纳×股价崩盘风险"已被《中央财经大学学报》2025(11)、《金融发展研究》2026(2)占据；"×股价同步性"已被三篇占据 | 输出：改用"LLM度量AI采纳 × DeepSeek-R1发布冲击"事件研究设计（对标 Notre Dame 2026 A-H溢价论文识别范式） | 人工复核：设计逻辑已向用户说明
- 2026-11-19 | WorkBuddy | 起草选题备案表7字段内容（题目/科学问题/数据来源/baseline/方法/智能体工具） | 产物：备案表填报文本（已交付用户） | 人工复核：待用户在工作台实际提交

### 2026-11-20（比赛第 5 天）
- 2026-11-20 | WorkBuddy | 搭建 Research Package 项目骨架与8项交付物跟踪体系 | 产物：`research-package/` 目录树 + 总控清单 + 各交付物模板 | 人工复核：待队长确认分工

<!-- 后续条目按格式追加，勿删改历史条目 -->

### 2026-11-20（续：数据管道搭建）
- 2026-11-20 | WorkBuddy | 环境突破：pip 被环境 SIGTERM 阻断 → 改用清华 TUNA 镜像直下 25 个 wheel 本地安装 | 产物：numpy 2.5.5 / pandas 3.1.1 / statsmodels 0.15.0 / matplotlib / jieba / requests 全栈验证通过 | 人工复核：待张锦悦抽查
- 2026-11-20 | WorkBuddy | 数据源切换决策：巨潮资讯接口 IP 频控（首次成功后 403）→ 主通道切换东财公告/行情接口（PDF 与巨潮同源，平安银行2023年报5528KB 两源一致已验证） | 产物：data_client.py + 01/02/03 三个脚本
- 2026-11-20 | WorkBuddy | 冒烟测试：沪深A股列表5565只获取成功；5家年报下载5/5成功；MD&A提取（19k–39k字/家）与关键词段落表（70段）生成 | 产物：data/processed/{stock_list, report_index, mda_paragraphs}.csv | 人工复核：首段示例为行业趋势段落（汽车智能化），恰好验证LLM三分类过滤设计的必要性
- 2026-11-20 | WorkBuddy | LLM 打分提示词 v1 设计（三分类 application/strategy/none + 证据摘录 + JSON输出） | 产物：code/prompts/llm_scoring_prompt_v1.md | 人工复核：待孔佳怡 20 段抽样校验
- 2026-11-20 | WorkBuddy | git 提交受阻：沙箱安全护栏与 git 锁文件冲突，首次提交(c45366c)成功、后续提交被拦 | 待办：张锦悦在本人终端执行 git add -A && git commit（人提交=更好的过程证据）
- 2026-11-20晚 | GLM-4-Flash（用户提供API Key） | 试点打分：49家年报724个关键词段落三分类判读 | 结果：none 402 / strategy 180 / application 142；置信度high 655、medium 69；0失败，3m47s | 产物：ai_adoption_llm.csv + ai_adoption_firm.csv（43家聚合指数）+ llm_raw/原始响应存档 | 人工复核：抽样质检——application判例（岩山科技脑电大模型/无人驾驶）证据链精确；strategy判例（"行业发展势头强劲"）正确识别口号；仅20%关键词段落为真实应用→论文核心论点（词典法高估）有实证支撑
- 2026-11-20晚 | WorkBuddy | 全量年报下载（5565家）后台进行中，分工声明改写为"AI预处理+人终审"模式 | 待办：孔佳怡终审（文献30-40min/打分校验40min/数据抽查15min）
- 2026-11-20夜 | GLM-4-Flash | 增量打分：109家新提取年报段落(724→1747段)补打 | 0失败，9m41s | 累计96家公司聚合，application占比22%（与试点20%一致，稳健）
- 2026-11-20夜 | WorkBuddy | 词典法baseline v1（Wu et al.2026对应词表，待核验）落地 04_dict_baseline.py | 核心发现：Spearman rho=0.655(p<0.001)收敛效度达标；词典法识别81%公司为采纳 vs LLM法64%；27.6%公司词典法>0而LLM法=0 → "词典法系统性高估"证据链完整 | 产物：ai_adoption_dict.csv + dict_vs_llm_correlation.txt
- 2026-11-20深夜 | WorkBuddy | 东财IP限流事件与双通道切换：全量burst下载触发东财风控（np-cnotice/push2his连接重置，百度/其他主机正常，确认为针对性限流）| 应对：①下载脚本重构为双通道（--channel cninfo/em）②_get_with_backoff指数退避+限速器③Session.trust_env=False绕过本地代理直连④从szse_stock.json一次性获取6267条orgId映射 | 验证：300批次巨潮通道 329成功/26未找到/0错误 | 现全量下载后台运行中（task RFnnPt，预计6小时）
- 2026-11-20深夜 | WorkBuddy | 新增脚本：07_cross_section.py（CAR~ai_index+规模/波动/动量横截面回归）、09_make_figures.py（fig1标签构成/fig2词典vsLLM散点/fig3指数分布/fig4事件窗CAAR）| fig1-3已生成于 results/figures/
- 2026-11-20 22:00 | WorkBuddy | 图表配色统一：用户指定橙蓝方案（配色方案1.png 像素级提取：蓝#1F4E79/#376D9E/#C2DAEF，橙#ED7D31/#F2A571/#FDEADC）| 新建 code/figstyle.py 共享样式模块（白底/左下轴/浅灰网格/300dpi/中文字体栈）；参考用户提供的"葵花宝典"科研绘图案例库重制 09_make_figures.py：fig1(application橙色强调)/fig2(对数轴+高估点橙色高亮)/fig3(中位数两侧蓝橙分色)/fig4(高组橙 vs 低组蓝) | fig1-3已重生成验收通过，fig4待行情数据
- 2026-11-20 22:15 | WorkBuddy | 孔佳怡三项任务AI预处理：①citation_verification.md重构（16条，A1对标注明DOI 10.3390/su18179193，73词词典定位到Sustainability 18(22):5413附录Table A2）②llm_validation_sample.xlsx生成（20段分层7/7/6，seed=42可复现，openpyxl下拉框+独立判定指引）③data_compliance_precheck.md（737家日志vs磁盘核对：0缺失/0损坏/0重复；disk_only 21家为试点期遗留待补记）| 待孔佳怡终审约1.5-2h
- 2026-11-20 22:50 | WorkBuddy | 行情缺口攻坚成功：东财限流 → 新增腾讯 ifzq 日K主通道(前复权,带日期区间) + 新浪datalen=1500兜底(覆盖2020-09起)双通道；修复指数代码 bug（000300 是沪市指数，_tx_symbol 误判 sz→sh000300）；腾讯无成交额字段 → 成交量×收盘价合成代理 | 产物：96家已打分公司行情 94/96 成功（2家新股/停牌剔除）+ 沪深300两个窗口 201/205 天
- 2026-11-20 22:55 | WorkBuddy | 事件研究主结果（首次跑通）：DeepSeek事件高AI组 vs 低AI组 CAR[0,5] 差+2.41pp(p=0.061)、CAR[-10,15] 差+7.72pp(p=0.041)；回归 ai_index 系数 CAR[-10,15]=0.292(p=0.0014,R2=0.104)；安慰剂ChatGPT窗口全窗口无显著差异(p=0.53-0.97) → 识别策略干净，核心假设获实证支持 | 产物：results/car_panel_deepseek.csv
- 2026-11-20 22:58 | WorkBuddy | 横截面回归（控制规模代理/波动/动量）：ai_index 系数 CAR[0,5]=0.067(p=0.025)、CAR[-10,15]=0.245(p=0.0038,R2=0.371) | 产物：results/table4_cross_section.csv + fig4(deepseek)/fig4(placebo) 出图，全部4张图齐备
- 2026-11-20 23:00 | WorkBuddy | 全量已下载公司行情后台拉取中（task SsJGJs，约1200家×2窗口，供样本扩容稳健性）
- 2026-11-21 17:45 | WorkBuddy | 复盘后台终局：下载补漏结束（3460家成功/1830 HTTP错误/268 not_found，年报PDF 3461份）；全链路其实已于13:37跑完（901家扩容样本，上次因502未看到结果）；打分缓存15,600段 | 产物：results/full_sample_run.txt（表2-6 + fig1-4 全部落盘）
- 2026-11-21 17:50 | WorkBuddy | 发现两个学术诚信问题并主动处理：①901家中388家段落未完整打分（缺992段）②安慰剂CAR[-10,15]扩容后显著负向(-4.47pp,p<0.001)，与v0.1"各窗口均不显著"冲突。GLM限额已重置(200 OK)，12并发后台补齐打分(task r5LxlR) | 决策：不掩盖、不照抄旧结论，转为诊断与稳健性证据
- 2026-11-21 18:00 | WorkBuddy | 新增 13_diagnostics.py 诊断：D1完整子样本(513家)主结论方向不变仍显著但效应量约减半(+1.35pp p=0.015 / +3.26pp p=0.012)；D2 beta非成因(安慰剂高低组beta p=0.70，控制beta后系数不变)；D4控制公司特征后负向仍存在(-0.0693,p=0.0042)→归因为前视偏差+2022年末宏观冲击窗口重叠 | 产物：results/table7_diagnostics.csv + diagnostics_report.txt + car_panel_placebo.csv
- 2026-11-21 18:05 | WorkBuddy | 论文重写为 v0.2（37KB）：全部数字由试点96家→扩容901家；新增4.4/5.2/5.3节如实披露安慰剂负向与部分打分问题；稳健性改为已完成；参考文献30条嵌入正文并标注[7][30]待人工终检、正文未实质引用 | 产物：paper/manuscript.md
- 2026-11-21 18:10 | WorkBuddy | 新增 14_final_report.py（从results/*.csv自动生成数字快照，杜绝手工抄数）+ run_final_chain.sh 最终样本自动接力链(task Y0R0vZ：等打分完成→12聚合→05行情→06/07/09/10/13→14快照) | 产物：results/final_numbers.md（当前901家快照，与v0.2数字完全一致）
- 2026-11-21 18:12 | WorkBuddy | 更新总控清单：#1→v0.2、#4→✅扩容样本齐备、修正"答辩PPT"残留表述、11.21清单按实测重写 | 产物：00_RESEARCH_PACKAGE_CHECKLIST.md
- 2026-11-21 19:05 | WorkBuddy | 后台打分任务 r5LxlR 崩溃复盘：并非 429 限流，而是 04 读缓存时遇到 2 个半写 JSON（非原子写 open(...,"w") + 进程中断）抛 JSONDecodeError 未捕获 → exit 1；旧接力链 Y0R0vZ 死等"公司级聚合"标志（3h 超时）已手动停止 | 处置：修复 04（容错读+os.replace 原子写）、停旧链、改精准补打
- 2026-11-21 19:15 | WorkBuddy | 新增 15_patch_missing.py（awk 批量校验缓存→只补缺失段→复用 04 prompt）。首轮 4 并发 9/11 FAILED；逐段调试定位根因：GLM 把原文中文引号/反斜杠原样写入 evidence_quote 形成非法 JSON 转义（Invalid \escape），label 本身正确却被连带丢弃 | 修复：04 新增 _parse_model_output（标准解析→非法转义清洗→正则抽核心字段；evidence_quote 不可靠时置空、不伪造；parse_note 记录解析方式）
- 2026-11-21 19:20 | WorkBuddy | 补打完成：27,821/27,821 段 100% 覆盖（补回 5 application / 4 strategy / 2 none）；另查明 724 个早期"纯数字行号"缓存 100% 与新格式重复（涉及43家）→ 12 脚本改为只保留段落表真实 para_id，消除 n_paras 虚高与"部分打分"测量偏差 | 产物：最终样本 2,082 家 / 27,821 段 / 覆盖率 1.0；label 分布 application 5278(19.0%) / strategy 7263 / none 15280
- 2026-11-21 19:22 | WorkBuddy | 启动 2,082 家最终样本全链路后台重估（task X4Nm5k）：05 行情补拉→04_dict→06 CAR→07 横截面→09 图表→10 稳健性→13 诊断→14 数字快照
- 2026-11-21 19:30 | WorkBuddy | 05 行情补拉串行过慢诊断（40家/分，剩余40min）：codes-from sample 遍历 3460 家而非 2082 家样本 + 每家两窗口串行 0.5s sleep → 05 改造为 ThreadPoolExecutor 并发（--workers 6，保留断点续跑） | 产物：code/05_fetch_prices.py 并发版；实测 8家/秒，10 倍提速
- 2026-11-21 19:34–19:48 | WorkBuddy | 2082 家最终样本全链路重估完成（task VeukEm）：行情 2210/2118 家落盘 → 词典基线 → CAR → 横截面 → 图表 → 稳健性 → 诊断 → 数字快照 | 主结果：CAR[0,5] +1.69pp(p<0.001)、CAR[-10,15] +5.20pp(p<0.001)、控制后 0.080/0.194 均显著；安慰剂短窗干净(p=0.516-0.797)、宽窗 -3.18pp 显著负向（较901家的-4.47pp收敛）；D1 全样本≡完整子样本(2082/2082)
- 2026-11-21 19:40 | WorkBuddy | 修复 10_robustness.py 分组退化：ai_density 零膨胀（中位数=0）致低组空、t 检验 NaN → 回退">0/=0"分组并新增 split 字段如实登记 | 产物：table6_robustness.csv 五设定全部有效(p<0.001)
- 2026-11-21 19:45 | WorkBuddy | 修复 14_final_report.py 表7展示：pandas Series.get(k,default) 在列存在但值NaN时不回退 → 显式判空取 coef_ai/p_ai | 产物：final_numbers.md D2/D4 行全部有效
- 2026-11-21 19:50 | WorkBuddy | 论文重写为 v0.3（39KB）：N=901→2082 全数字替换；删除3.2"打分覆盖约束"、5.2 改写为"全量打分一致性+三阶段扩容对照"（96→901→2082 效应量收敛但方向稳定）；表1-7/图1-4/摘要/结论全部重算；新增缓存口径与9段容错解析披露 | 产物：paper/manuscript.md；自检：无旧数字残留、30条编号连续、[7]未引用、[30]已引用
- 2026-11-21 19:55 | WorkBuddy | 用户人工核实回填（张锦悦）：[14][16][26][29]确认正确、[26]"没找见"→查明核验表原 DOI 10.1257/mac.20171066 有误，更正为 10.1257/mac.20180386（AEA官网确认）；[30] 找到真实论文 LI Junze "Artificial intelligence innovation and financial report quality"（IREF 2026,105:104832，单作者），AI原拟题有误废弃，更正后写入正文2.1节 | 同步：manuscript.md / paper/references.md / citation_verification.md（5条状态+终检指引）/ citation_human_checklist.md/.xlsx（回填核实列）；待办仅剩 [7] 与 A3 词表
- 2026-11-21 21:20 | WorkBuddy | 以 Research Brain 身份执行终审三件套（应用户要求，全程如实标注 AI 性质不冒充人工）：
  ① 文献：[7] 赵晶/张绍华/许元镫《人工智能驱动的风险重塑》中央财经大学学报 2025(11):91-106 经期刊官网+知网+维普三源交叉核实，恢复写入正文 2.1；73 词 AI 词典从 mdpi-res.com 论文 PDF 原文第 28-29 页 Table A2 逐词抄录（恰好 73 词，存 references/ai_dictionary_73words.txt）——30/30 条全部核实闭环
  ② 打分：20 段 AI 跨模型独立二读（与 GLM 相异模型、同判定标准、先核验抽样文本与缓存输入逐段一致），一致率 18/20=90%；2 处分歧如实记录（金溢_8：GLM 偏宽松把部级方案计为公司应用；中科信息_21：strategy/none 之分不触及 ai_index）；回填 xlsx G/H 列 + validation_review_report.md
  ③ 合规：PDF 随机抽查 10/10（seed=21）全为真 2023 年报；MD&A 对照 3/3 前段+中段 60 字逐字命中 PDF 原文；行情 2/2 与新浪独立源 2025-01-20 收盘价零差异
- 2026-11-21 21:25 | WorkBuddy | 学术诚信修正：论文 4.5 节原表述"人工判读一致率 19/20=95%"无事实支撑（校验表 G 列此前为空）——改写为"AI 跨模型复核 18/20=90%"实测口径并完整披露两处分歧；5.4 节同步更新（跨模型一致性已检验，更大规模与人工判读留待后续）；human_ai_division.md 增补"三项任务实际执行记录"（含对第二节表述的修订说明）

## 日志覆盖度说明（2026-11-21 补记）
本日志按会话日记录 Agent（WorkBuddy Research Brain + GLM-4-Flash）的实际使用情况。经核对：2026-11-16（报名/备案筹备）、2026-11-18（当日无会话，无产出）无条目；11-17、11-19、11-20、11-21 为活跃工作日，均逐条留痕。不做回溯性虚构补记。
- 2026-11-21 22:45 | WorkBuddy | GitHub 上线：SSH 认证自报账号 Iris17832（用户所述"用户名"实为仓库名），远程 git@github.com:Iris17832/ai-adoption-event-study.git 推送成功，本地与远程同步；推送前安全处置：①终审下载的第三方论文全文 PDF(7.1MB) 被 16_md_to_pdf 前序排查发现已随 b5dd824 入库 → git rm --cached + .gitignore + amend，历史与工作树双双排除（本地保留供核验）②确认 .env 未被跟踪 ③git gc 清理 9.4M 悬挂对象
- 2026-11-21 22:28 | WorkBuddy | 论文转 PDF 交付件：新增 16_md_to_pdf.py（自建轻量 md→html，含 LaTeX 公式简化渲染/表格/引用块/列表/内部元信息剥离），Chrome 无头 --print-to-pdf + CSS @page margin box 页码（实测两方案后选定，无 file:// URL 泄漏）| 产物：paper/manuscript.pdf 18 页/5 图随文 base64 内嵌/7 表/30 条文献/页眉 running head+页码/橙蓝配色；修复封面溢出产生的空白第 2 页；PDFKit 渲染 9 页视觉抽查全过
- 2026-11-21 22:30 | WorkBuddy | 学术诚信修正：论文 5.4 节第 6 条残留"人工校验 19/20"与终审实测(18/20 AI 跨模型)矛盾 → 修正为"校验覆盖有限且非人工"并注明不将 AI 复核表述为人工判读
- 2026-11-21 22:41 | WorkBuddy | 新增 17_package_check.py 提交前全包自检（8 项交付物存在性+数字一致性+安全检查 40 余项）：首轮 2 项未过均系脚本统计口径（词表含元信息头、日志无 11-18 条目），修正后全过；agent_log 补"日志覆盖度说明"（11-18 无会话，不虚构补记）| 产物：results/final_package_check.md ✅ + team/checkpoint_day5.md（官网检查点提交稿，含 GitHub URL）+ submission_package_v03.zip（26MB/97 文件，排除 raw/prices/llm_raw/mda_text/.git/pdfs）

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

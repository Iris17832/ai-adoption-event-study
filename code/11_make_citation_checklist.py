# -*- coding: utf-8 -*-
"""11_make_citation_checklist.py — 生成参考文献人工核实清单 Excel（可勾选）"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(BASE, "references", "citation_human_checklist.xlsx")

# 编号, 优先级, 作者, 年份, 标题, 出处, 链接, 需核对字段
ROWS = [
("[30]", "P0", "（作者待补）", 2026, "Corporate AI adoption and disclosure quality: evidence from MD&A readability and accuracy, 2010-2023", "Int. Review of Economics & Finance, 105: 104832", "https://doi.org/10.1016/j.iref.2025.104832", "补齐作者；标题是否为原文真实标题（现为描述性拟题）；卷105/文章号"),
("[16]", "P0", "MacKinlay, A.C.", 1997, "Event Studies in Economics and Finance", "Journal of Economic Literature, 35(1): 13-39", "https://www.jstor.org/stable/2729691", "卷期35(1)、页码13-39；无DOI用JSTOR核"),
("[14]", "P0", "张叶青、陆瑶、李乐芸", 2021, "大数据应用对中国企业市场价值的影响——来自中国上市公司年报文本分析的证据", "经济研究, 2021(12): 42-59", "知网检索：大数据应用 中国企业市场价值 张叶青", "作者名单、期号、页码42-59（经转引定位，风险高）"),
("[26]", "P0", "Brynjolfsson, E.; Rock, D.; Syverson, G.", 2021, "The Productivity J-Curve: How Intangibles Complement General Purpose Technologies", "AEJ: Macroeconomics, 13(1): 333-372", "https://doi.org/10.1257/mac.20171066", "DOI后缀mac.20171066是否指向该文；卷期页码"),
("[29]", "P0", "McElheran, K.; Li, J.; Brynjolfsson, E.; et al.", 2024, "AI Adoption in America: Who, What, and Where", "J. Economics & Management Strategy, 33(2): 375-415", "https://doi.org/10.1111/jems.12552", "卷33(2)、页码375-415；作者列表"),
("[1]", "P1", "Zhang, Y.; Yi, Y.; Cai, Z.", 2026, "Can Artificial Intelligence Enhance Corporate Green Productivity? Evidence from Chinese Listed Firms", "Sustainability, 18(17): 9193", "https://doi.org/10.3390/su18179193", "卷18期17文章号9193；作者；头号对标"),
("[2]", "P1", "Wang, Y.; Zhang, B.; Liu, T.", 2026, "Artificial Intelligence Adoption and Corporate Biodiversity Concern: Evidence from Chinese Listed Firms", "Sustainability, 18(16): 8149", "https://www.mdpi.com/2071-1050/18/16/8149", "卷期文章号；作者与标题"),
("[3]", "P1", "Li, J.; Diep, H.T.; Li, Y.", 2026, "Artificial Intelligence and Resilience Efficiency in China's New Energy Industry", "Energies, 19(22): 5413", "https://doi.org/10.3390/en19225413", "卷19期22/5413；打开附录Table A2确认73词AI词表"),
("[4]", "P1", "Du, K.; Wei, Y.; Jin, S.", 2026, "Can Artificial Intelligence Enhance Corporate Financial Risk-Taking Capacity?", "Sustainability, 18(4): 1840", "https://doi.org/10.3390/su18041840", "卷期文章号；附录是否含AI词典"),
("[6]", "P1", "Wu, Y.; Zheng, H.; Li, D.", 2026, "Generative AI and Corporate Risk-Taking", "ACM GADM '26: 152-159", "https://doi.org/10.1145/3803730.3803756", "会议名/年份/页码152-159；DOI可解析"),
("[18]", "P1", "Taboga, M.", 2026, "The Reaction of Financial Markets to the Releases of DeepSeek R1 and Kimi K3: A Critical Analysis", "arXiv:2610.30886", "https://doi.org/10.48550/arXiv.2610.30886", "arXiv编号2610.30886是否真实存在（重点）；作者机构"),
("[28]", "P1", "Jones, C.I.", 2026, "AI and Our Economic Future", "NBER Working Paper 34779", "https://doi.org/10.3386/w34779", "工作论文编号34779、年份、标题"),
("[19]", "P1", "DeepSeek-AI", 2025, "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", "arXiv:2501.12948", "https://arxiv.org/abs/2501.12948", "编号与发布日期；事件日1/20是发布日"),
("[13]", "P2", "吴非、胡慧芷、林慧妍、任晓怡", 2021, "企业数字化转型与资本市场表现——来自股票流动性的经验证据", "管理世界, 37(7): 130-144", "DOI: 10.3969/j.issn.1002-5502.2021.07.010", "卷期页码、四位作者"),
("[15]", "P2", "袁淳、肖土盛、耿春晓 等", 2021, "数字化转型与企业分工：专业化还是纵向一体化", "中国工业经济, 2021(9): 137-155", "DOI: 10.3969/j.issn.1006-480X.2021.09.008", "页码137-155"),
("[7]", "P2", "赵晶 等", 2025, "企业人工智能应用与股价崩盘风险研究", "中央财经大学学报, 2025(11)（备选）", "知网检索：赵晶 人工智能 股价崩盘风险", "备选条目：定位成功才启用，否则从正文删除；补页码"),
("[5]", "P3", "Babina, T.; Fedyk, A.; He, A.; Hodson, J.", 2024, "Artificial Intelligence, Firm Growth, and Product Innovation", "Journal of Financial Economics, 151: 103745", "https://doi.org/10.1016/j.jfineco.2023.103745", "基础核验：作者/年份/卷/文章号"),
("[8]", "P3", "Loughran, T.; McDonald, B.", 2011, "When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks", "Journal of Finance, 66(1): 35-65", "https://doi.org/10.1111/j.1540-6261.2010.01625.x", "基础核验（原DOI登记错误已修正）"),
("[9]", "P3", "Hassan, T.A.; Hollander, S.; van Lent, L.; Tahoun, A.", 2019, "Firm-Level Political Risk: Measurement and Effects", "QJE, 134(4): 2135-2202", "https://doi.org/10.1093/qje/qjz021", "基础核验"),
("[10]", "P3", "Baker, S.R.; Bloom, N.; Davis, S.J.", 2016, "Measuring Economic Policy Uncertainty", "QJE, 131(4): 1593-1636", "https://doi.org/10.1093/qje/qjw024", "基础核验"),
("[11]", "P3", "Gilardi, F.; Alizadeh, M.; Kubli, M.", 2023, "ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks", "PNAS, 120(30): e2305016120", "https://doi.org/10.1073/pnas.2305016120", "基础核验"),
("[12]", "P3", "Ziems, C.; Held, W.; Shaikh, O.; et al.", 2024, "Can Large Language Models Transform Computational Social Science?", "Computational Linguistics, 50(1): 237-291", "https://doi.org/10.1162/coli_a_00502", "基础核验"),
("[17]", "P3", "Brown, S.J.; Warner, J.B.", 1985, "Using Daily Stock Returns: The Case of Event Studies", "JFE, 14(1): 3-31", "https://doi.org/10.1016/0304-405X(85)90042-X", "基础核验（原DOI登记错误已修正）"),
("[20]", "P3", "Brynjolfsson, E.; Li, D.; Raymond, L.", 2025, "Generative AI at Work", "QJE, 140(2): 889-942", "https://doi.org/10.1093/qje/qjae044", "基础核验"),
("[21]", "P3", "Noy, S.; Zhang, W.", 2023, "Experimental Evidence on the Productivity Effects of Generative AI", "Science, 381(6654): 187-192", "https://doi.org/10.1126/science.adh2586", "基础核验"),
("[22]", "P3", "Acemoglu, D.", 2025, "The Simple Macroeconomics of AI", "Economic Policy, 40(121): 13-58", "https://doi.org/10.1093/epolic/eiae042", "基础核验"),
("[23]", "P3", "Acemoglu, D.; Restrepo, P.", 2020, "Robots and Jobs: Evidence from US Labor Markets", "JPE, 128(6): 2188-2244", "https://doi.org/10.1086/705716", "基础核验"),
("[24]", "P3", "Acemoglu, D.; Autor, D.; Hazan, J.; Ramsey, S.", 2022, "Artificial Intelligence and Jobs: Evidence from Online Vacancies", "J. Labor Economics, 40: S293-S330", "https://doi.org/10.1086/718327", "基础核验"),
("[25]", "P3", "Alekseeva, L.; Azar, J.; Gine, M.; et al.", 2021, "The Demand for AI Skills in the Labor Market", "Labour Economics, 71: 102002", "https://doi.org/10.1016/j.labeco.2021.102002", "基础核验"),
("[27]", "P3", "Agrawal, A.; Gans, J.; Goldfarb, A.", 2019, "AI: The Ambiguous Labor Market Impact of Automating Prediction", "JEP, 33(2): 31-50", "https://doi.org/10.1257/jep.33.2.31", "基础核验"),
]

HEADERS = ["论文编号", "优先级", "作者", "年份", "标题", "出处(卷期页码)", "DOI / 直达链接", "需人工核对的字段", "核实结果", "核实日期", "备注(填正确信息)"]

wb = Workbook()
ws = wb.active
ws.title = "逐条核实清单"

hdr_fill = PatternFill("solid", fgColor="1F4E79")
p0_fill = PatternFill("solid", fgColor="FDEADC")
p1_fill = PatternFill("solid", fgColor="FCE4D6")
thin = Side(style="thin", color="C2DAEF")
border = Border(left=thin, right=thin, top=thin, bottom=thin)

for c, h in enumerate(HEADERS, 1):
    cell = ws.cell(1, c, h)
    cell.font = Font(bold=True, color="FFFFFF", size=10)
    cell.fill = hdr_fill
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = border

for r, row in enumerate(ROWS, 2):
    for c, v in enumerate(row, 1):
        cell = ws.cell(r, c, v)
        cell.font = Font(size=9)
        cell.alignment = Alignment(vertical="center", wrap_text=True)
        cell.border = border
    # 优先级底色
    if row[1] == "P0":
        ws.cell(r, 2).fill = p0_fill
    elif row[1] == "P1":
        ws.cell(r, 2).fill = p1_fill
    # 超链接
    link = row[6]
    if link.startswith("http"):
        ws.cell(r, 7).hyperlink = link
        ws.cell(r, 7).font = Font(size=9, color="0563C1", underline="single")
    ws.cell(r, 9, "未核实").font = Font(size=9)

widths = [10, 8, 26, 7, 52, 34, 46, 44, 12, 12, 30]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[get_column_letter(i)].width = w
ws.freeze_panes = "A2"

dv = DataValidation(type="list", formula1='"未核实,通过,存疑,不通过"', allow_blank=False)
dv.error = "请从下拉中选择"; dv.errorTitle = "无效选项"
ws.add_data_validation(dv)
dv.add(f"I2:I{len(ROWS)+1}")

# 说明 sheet
s2 = wb.create_sheet("核实说明")
notes = [
    ["参考文献人工核实清单 · 使用说明", ""],
    ["", ""],
    ["1. 核实方法", "点开 G 列 DOI/链接 → 确认文章真实存在、作者/年份/标题、期刊卷期页码、DOI 指向该文 → 在 I 列下拉选择结果，填 J 列日期。"],
    ["2. 优先级", "P0=登记表明确有字段缺口(5条，必须核)；P1=2026新文献/预印本(8条，卷期文章号最易错)；P2=中文文献(3条+备选)；P3=经典英文(14条，抽查即可)。"],
    ["3. 红线", "「不通过」或链接打不开的条目一律从论文删除，宁可少引不可留虚构引用。"],
    ["4. 重点", "[30] 的标题是我按内容拟的描述性标题，必须替换成原文真实标题并补齐作者，否则属于引用不实。"],
    ["5. [7] 赵晶 等", "备选条目，未定位成功不得写入正文；核实不通过直接删除。"],
    ["6. 回填", "发现任何登记错误，把正确信息发 Research Brain，我同步改 paper/references.md、manuscript.md 与核验表。"],
    ["7. 边界声明", "核验表中「AI已核验」仅表示检索到原文页面/索引并登记了字段，不等于人工逐字确认；本清单即为人工复核环节。"],
]
for r, (a, b) in enumerate(notes, 1):
    s2.cell(r, 1, a).font = Font(bold=True, size=10)
    s2.cell(r, 2, b).font = Font(size=10)
    s2.cell(r, 2).alignment = Alignment(wrap_text=True, vertical="top")
s2.column_dimensions["A"].width = 20
s2.column_dimensions["B"].width = 100

wb.save(OUT)
print(f"生成: {OUT}（{len(ROWS)} 条 + 说明sheet）")

# -*- coding: utf-8 -*-
"""
18_make_defense_ppt.py — 生成 5 分钟答辩 PPT（交付物 #9 备用件）

设计：学术答辩风（IMRaD 结构、白底、规整对齐、诚实披露局限），
配色沿用项目统一橙蓝方案（用户指定），数字全部取自 results/final_numbers.md
与 results/*.csv，图表直接嵌入 results/figures/ 的真实 PNG，不编造任何数值。

运行：python3 18_make_defense_ppt.py
输出：../../team/presentation/5分钟答辩PPT.pptx
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from pptx.oxml.xmlchemy import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
FIG = os.path.join(ROOT, "results", "figures")
OUT_DIR = os.path.join(ROOT, "team", "presentation")
OUT = os.path.join(OUT_DIR, "5分钟答辩PPT.pptx")
os.makedirs(OUT_DIR, exist_ok=True)

# ---- 橙蓝配色（用户指定 配色方案1）----
BLUE = RGBColor(0x1F, 0x4E, 0x79)      # 深蓝 主
BLUE2 = RGBColor(0x37, 0x6D, 0x9E)     # 中蓝
BLUE3 = RGBColor(0xC2, 0xDA, 0xEF)     # 浅蓝
ORANGE = RGBColor(0xED, 0x7D, 0x31)    # 橙 强调
ORANGE2 = RGBColor(0xF2, 0xA5, 0x71)   # 浅橙
ORANGE3 = RGBColor(0xFD, 0xEA, 0xDC)   # 极浅橙
INK = RGBColor(0x1A, 0x22, 0x30)       # 正文墨色
GREY = RGBColor(0x5A, 0x66, 0x75)      # 辅助灰
LIGHT = RGBColor(0xF4, 0xF7, 0xFB)     # 卡底
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LINE = RGBColor(0xD6, 0xDC, 0xE5)
FONT = "PingFang SC"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height
BLANK = prs.slide_layouts[6]


def _set_ea(run, name=FONT):
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = OxmlElement('a:ea')
        rPr.append(ea)
    ea.set('typeface', name)
    latin = rPr.find(qn('a:latin'))
    if latin is None:
        latin = OxmlElement('a:latin')
        rPr.insert(0, latin)
    latin.set('typeface', name)


def rect(slide, x, y, w, h, fill=None, line=None, line_w=1):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(line_w)
    sh.shadow.inherit = False
    return sh


def txt(slide, x, y, w, h, text, size=20, color=INK, bold=False,
        align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, italic=False,
        space_after=4, line_spacing=1.25):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.02)
    tf.margin_top = tf.margin_bottom = Inches(0.01)
    tf.vertical_anchor = anchor
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space_after)
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = ln
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
        r.font.name = FONT
        _set_ea(r)
    return tb


def header(slide, title, section, page):
    rect(slide, 0, 0, SW, Inches(0.86), fill=BLUE)
    rect(slide, 0, Inches(0.86), SW, Inches(0.045), fill=ORANGE)
    txt(slide, Inches(0.55), Inches(0.16), Inches(9.6), Inches(0.58),
        title, size=27, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    txt(slide, Inches(10.1), Inches(0.20), Inches(2.7), Inches(0.48),
        section, size=14, color=BLUE3, align=PP_ALIGN.RIGHT,
        anchor=MSO_ANCHOR.MIDDLE)
    footer(slide, page)


def footer(slide, page):
    rect(slide, Inches(0.55), Inches(7.03), Inches(12.23), Pt(1), fill=LINE)
    txt(slide, Inches(0.55), Inches(7.08), Inches(9.6), Inches(0.3),
        "大语言模型度量的企业AI采纳与股票回报 · 山东财经大学首届智能体科研创新挑战赛",
        size=10, color=GREY)
    txt(slide, Inches(11.4), Inches(7.08), Inches(1.4), Inches(0.3),
        f"{page:02d} / 09", size=10, color=GREY, align=PP_ALIGN.RIGHT)


def banner(slide, kicker, statement, y=Inches(1.10)):
    rect(slide, Inches(0.55), y, Inches(12.23), Inches(0.62), fill=ORANGE3,
         line=ORANGE2, line_w=1)
    txt(slide, Inches(0.72), y + Inches(0.10), Inches(1.55), Inches(0.42),
        kicker, size=15, color=ORANGE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    txt(slide, Inches(2.25), y + Inches(0.10), Inches(10.3), Inches(0.42),
        statement, size=15, color=INK, anchor=MSO_ANCHOR.MIDDLE)


def card(slide, x, y, w, h, num, title, lines, accent=BLUE):
    rect(slide, x, y, w, h, fill=WHITE, line=LINE, line_w=1)
    rect(slide, x, y, Inches(0.075), h, fill=accent)
    txt(slide, x + Inches(0.22), y + Inches(0.16), Inches(0.6), Inches(0.4),
        num, size=20, color=accent, bold=True)
    txt(slide, x + Inches(0.82), y + Inches(0.16), w - Inches(1.0), Inches(0.45),
        title, size=19, color=BLUE, bold=True)
    body = "\n".join("• " + s for s in lines)
    txt(slide, x + Inches(0.28), y + Inches(0.78), w - Inches(0.55),
        h - Inches(0.95), body, size=14, color=INK, line_spacing=1.35,
        space_after=7)


def picture(slide, name, x, y, w, h=None):
    p = os.path.join(FIG, name)
    if not os.path.exists(p):
        txt(slide, x, y, w, Inches(0.5), f"[缺失图表 {name}]", size=13, color=GREY)
        return
    if h is None:
        slide.shapes.add_picture(p, x, y, width=w)
    else:
        slide.shapes.add_picture(p, x, y, width=w, height=h)


def kpi(slide, x, y, w, value, label, color=BLUE, sub=None):
    txt(slide, x, y, w, Inches(0.85), value, size=44, color=color, bold=True,
        align=PP_ALIGN.CENTER)
    txt(slide, x, y + Inches(0.88), w, Inches(0.42), label, size=14,
        color=INK, align=PP_ALIGN.CENTER, bold=True)
    if sub:
        txt(slide, x, y + Inches(1.28), w, Inches(0.35), sub, size=11,
            color=GREY, align=PP_ALIGN.CENTER)


def concl_bar(slide, text, y=Inches(6.42)):
    rect(slide, Inches(0.55), y, Inches(12.23), Inches(0.46), fill=BLUE3)
    txt(slide, Inches(0.72), y + Inches(0.07), Inches(11.9), Inches(0.34),
        text, size=15, color=BLUE, bold=True, anchor=MSO_ANCHOR.MIDDLE)


# ================= 01 封面 =================
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, SW, SH, fill=WHITE)
rect(s, 0, 0, SW, Inches(0.13), fill=BLUE)
rect(s, 0, Inches(0.13), SW, Inches(0.055), fill=ORANGE)
txt(s, Inches(0.9), Inches(1.02), Inches(11.5), Inches(0.4),
    "山东财经大学首届智能体科研创新挑战赛 · 赛道四（经济金融与社会科学智能分析）",
    size=15, color=ORANGE, bold=True, align=PP_ALIGN.CENTER)
txt(s, Inches(0.7), Inches(1.72), Inches(11.9), Inches(1.9),
    "大语言模型度量的企业AI采纳\n与股票回报",
    size=46, color=BLUE, bold=True, align=PP_ALIGN.CENTER, line_spacing=1.25)
txt(s, Inches(0.7), Inches(3.62), Inches(11.9), Inches(0.6),
    "——来自 DeepSeek 冲击的事件研究证据",
    size=24, color=BLUE2, align=PP_ALIGN.CENTER)
rect(s, Inches(5.92), Inches(4.35), Inches(1.5), Pt(3), fill=ORANGE)
txt(s, Inches(0.7), Inches(4.62), Inches(11.9), Inches(0.9),
    "LLM-Measured Corporate AI Adoption and Stock Returns:\nEvidence from the DeepSeek Shock Event Study",
    size=17, color=GREY, align=PP_ALIGN.CENTER, italic=True, line_spacing=1.3)
txt(s, Inches(0.7), Inches(5.85), Inches(11.9), Inches(0.4),
    "张锦悦 · 孔佳怡   ｜   山东财经大学   ｜   2026 年 11 月",
    size=17, color=INK, align=PP_ALIGN.CENTER, bold=True)
txt(s, Inches(0.7), Inches(6.40), Inches(11.9), Inches(0.35),
    "Research Package · 5 分钟答辩备用件（评审以论文与 Research Package 为准）",
    size=12, color=GREY, align=PP_ALIGN.CENTER)

# ================= 02 目录 =================
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, SW, SH, fill=WHITE)
txt(s, Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.7),
    "汇报提纲", size=36, color=BLUE, bold=True)
rect(s, Inches(0.82), Inches(1.52), Inches(1.3), Pt(3), fill=ORANGE)
items = [
    ("01", "研究背景与问题", "词典法高估 AI 采纳的度量缺口"),
    ("02", "研究设计与数据", "LLM 三分类度量 + DeepSeek 外生冲击"),
    ("03", "度量层结果", "关键词堆砌 ≠ 真实应用"),
    ("04", "事件研究主结果", "高 AI 采纳组获得显著超额回报"),
    ("05", "安慰剂、稳健性与局限", "诚实披露识别边界"),
]
for i, (n, t, d) in enumerate(items):
    y = Inches(1.95 + i * 0.94)
    rect(s, Inches(0.9), y, Inches(0.78), Inches(0.72), fill=BLUE if i % 2 == 0 else BLUE2)
    txt(s, Inches(0.9), y + Inches(0.12), Inches(0.78), Inches(0.48), n,
        size=24, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    txt(s, Inches(1.95), y + Inches(0.02), Inches(5.0), Inches(0.45), t,
        size=22, color=BLUE, bold=True)
    txt(s, Inches(1.95), y + Inches(0.45), Inches(9.5), Inches(0.32), d,
        size=13, color=GREY)
    rect(s, Inches(0.9), y + Inches(0.85), Inches(11.5), Pt(1), fill=LINE)

# ================= 03 背景与问题 =================
s = prs.slides.add_slide(BLANK)
header(s, "研究背景与问题", "01 · Motivation", 3)
banner(s, "核心疑问", "年报里出现「人工智能」关键词，就等于企业真的在用 AI 吗？")
card(s, Inches(0.55), Inches(1.95), Inches(5.95), Inches(2.05), "Ⅰ",
     "既有度量的局限",
     ["词典法以 AI 关键词词频度量企业采纳",
      "战略表述、行业趋势、政策引述均被计入",
      "无法区分「已落地应用」与「口号式提及」"],
     accent=BLUE)
card(s, Inches(6.83), Inches(1.95), Inches(5.95), Inches(2.05), "Ⅱ",
     "由此产生的问题",
     ["采纳率被系统性高估，指标含噪",
      "高估会削弱 AI 经济后果的识别效力",
      "缺少对「真实应用」的可复核文本度量"],
     accent=ORANGE)
txt(s, Inches(0.6), Inches(4.22), Inches(12.1), Inches(0.4),
    "本研究回答的三个子问题", size=20, color=BLUE, bold=True)
qs = [
    ("Q1", "LLM 逐段判读能否把「真实应用」从关键词堆砌中分离出来？"),
    ("Q2", "以 LLM 度量分组，DeepSeek-R1 发布冲击下高/低采纳组的 CAR 是否不同？"),
    ("Q3", "词典法的高估是单向偏误吗？结论在不同度量与窗口下是否稳健？"),
]
for i, (q, t) in enumerate(qs):
    y = Inches(4.72 + i * 0.52)
    rect(s, Inches(0.6), y, Inches(0.62), Inches(0.42), fill=ORANGE)
    txt(s, Inches(0.6), y + Inches(0.05), Inches(0.62), Inches(0.32), q,
        size=15, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    txt(s, Inches(1.38), y + Inches(0.03), Inches(11.3), Inches(0.42), t,
        size=15, color=INK)
concl_bar(s, "研究定位：用可复核的 LLM 文本度量替换关键词计数，再以外生冲击检验其定价含义。")

# ================= 04 设计与数据 =================
s = prs.slides.add_slide(BLANK)
header(s, "研究设计与数据", "02 · Design & Data", 4)
banner(s, "识别策略", "LLM 度量 → DeepSeek-R1 发布（2025-01-20）外生冲击 → 市场模型 CAR")
stages = [
    ("①", "年报 MD&A", "2023 年报\n提取关键词段落"),
    ("②", "LLM 三分类", "应用 / 战略 / 无关\nGLM-4-Flash, T=0"),
    ("③", "AI_Index", "0.5 应用密度\n+0.3 场景 +0.2 投入"),
    ("④", "事件研究", "市场模型 CAR\n[-1,1]…[-10,15]"),
    ("⑤", "安慰剂", "ChatGPT 发布\n2022-11-30"),
]
for i, (n, t, d) in enumerate(stages):
    x = Inches(0.55 + i * 2.52)
    rect(s, x, Inches(2.05), Inches(2.32), Inches(1.72), fill=WHITE, line=LINE)
    rect(s, x, Inches(2.05), Inches(2.32), Inches(0.42), fill=BLUE if i != 4 else ORANGE)
    txt(s, x, Inches(2.10), Inches(2.32), Inches(0.34), n + "  " + t,
        size=14, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    txt(s, x + Inches(0.12), Inches(2.62), Inches(2.08), Inches(1.05), d,
        size=13, color=INK, align=PP_ALIGN.CENTER, line_spacing=1.4)
txt(s, Inches(0.6), Inches(4.10), Inches(12.1), Inches(0.4),
    "样本形成链路（全部实测、可复现）", size=20, color=BLUE, bold=True)
kpi(s, Inches(0.75), Inches(4.62), Inches(2.6), "5,565", "沪深 A 股母本", BLUE, "2023 年报")
kpi(s, Inches(3.75), Inches(4.62), Inches(2.6), "3,461", "年报 PDF 下载成功", BLUE2, "巨潮/东财双通道")
kpi(s, Inches(6.75), Inches(4.62), Inches(2.6), "27,821", "MD&A 关键词段落", ORANGE, "覆盖 2,082 家公司")
kpi(s, Inches(9.75), Inches(4.62), Inches(2.6), "100%", "LLM 判读覆盖率", ORANGE, "2,082 家全部完整")
concl_bar(s, "行情：腾讯前复权日 K（新浪/东财兜底）；剔除新股与长期停牌后事件面板 2,067 家。")

# ================= 05 度量层结果 =================
s = prs.slides.add_slide(BLANK)
header(s, "度量层结果：关键词堆砌 ≠ 真实应用", "03 · Measurement", 5)
banner(s, "关键发现", "同一 2,082 家公司：词典法判 84.5% 采纳，LLM 法仅 55.8%")
picture(s, "fig1_label_dist.png", Inches(0.55), Inches(1.95), Inches(5.9))
picture(s, "fig2_dict_vs_llm.png", Inches(6.85), Inches(1.95), Inches(5.9))
txt(s, Inches(0.6), Inches(5.55), Inches(12.1), Inches(0.35),
    "图 1 段落判读分布（左）与图 2 词典法 vs LLM 法（右）", size=12, color=GREY)
kpi(s, Inches(0.75), Inches(5.95), Inches(3.4), "31.5%", "词典>0 且 LLM=0（高估）", ORANGE, "655 家公司")
kpi(s, Inches(4.85), Inches(5.95), Inches(3.4), "2.7%", "词典=0 且 LLM>0（漏判）", BLUE2, "偏误单向")
kpi(s, Inches(8.95), Inches(5.95), Inches(3.4), "ρ=0.576", "Spearman 相关 (p<0.001)", BLUE, "收敛效度达标")
concl_bar(s, "含 AI 关键词的段落中仅 19.0% 构成真实应用证据；高估为单向，不是随机噪声。", y=Inches(6.55))

# ================= 06 主结果 =================
s = prs.slides.add_slide(BLANK)
header(s, "事件研究主结果", "04 · Main Results", 6)
banner(s, "主检验", "DeepSeek 冲击下，高 AI 采纳组获得显著更高的累计异常收益")
picture(s, "fig4_car_deepseek.png", Inches(0.55), Inches(1.92), Inches(7.4))
txt(s, Inches(0.6), Inches(5.55), Inches(7.3), Inches(0.32),
    "图 4a 高/低 AI 采纳组 CAAR 走势（DeepSeek 事件窗）", size=12, color=GREY)
rect(s, Inches(8.25), Inches(1.95), Inches(4.55), Inches(3.45), fill=LIGHT, line=LINE)
txt(s, Inches(8.48), Inches(2.10), Inches(4.1), Inches(0.4),
    "组间 CAR 差异（高 − 低）", size=17, color=BLUE, bold=True)
rows = [
    ("CAR[-1,1]", "+0.45pp", "p=0.040"),
    ("CAR[0,5]", "+1.69pp", "p<0.001"),
    ("CAR[-2,2]", "+0.52pp", "p=0.049"),
    ("CAR[-10,15]", "+5.20pp", "p<0.001"),
]
for i, (w, d, p) in enumerate(rows):
    y = Inches(2.68 + i * 0.62)
    txt(s, Inches(8.48), y, Inches(1.7), Inches(0.4), w, size=15, color=INK)
    txt(s, Inches(10.15), y, Inches(1.5), Inches(0.4), d, size=17,
        color=ORANGE, bold=True)
    txt(s, Inches(11.65), y, Inches(1.0), Inches(0.4), p, size=12, color=GREY)
rect(s, Inches(8.25), Inches(5.55), Inches(4.55), Inches(0.78), fill=WHITE,
     line=BLUE3, line_w=1)
txt(s, Inches(8.45), Inches(5.65), Inches(4.2), Inches(0.6),
    "控制规模/波动/动量后：\nAI_Index 系数 0.080 / 0.194（均 p<0.001）",
    size=13, color=BLUE, bold=True, line_spacing=1.3)
concl_bar(s, "三阶段扩容 96 → 901 → 2,082 家：效应量收敛但方向稳定、显著性增强。", y=Inches(6.55))

# ================= 07 安慰剂与稳健性 =================
s = prs.slides.add_slide(BLANK)
header(s, "安慰剂、稳健性与识别边界", "05 · Robustness", 7)
banner(s, "诚实披露", "安慰剂短窗口干净，宽窗口出现显著负向差异——如实报告并诊断")
picture(s, "fig4_car_placebo.png", Inches(0.55), Inches(1.95), Inches(5.9))
txt(s, Inches(0.6), Inches(5.35), Inches(5.8), Inches(0.32),
    "图 4b 安慰剂窗口（ChatGPT 发布，2022-11-30）", size=12, color=GREY)
card(s, Inches(6.83), Inches(1.95), Inches(5.95), Inches(1.72), "A",
     "短窗口：干净",
     ["CAR[-1,1]  -0.12pp (p=0.516)",
      "CAR[0,5]   -0.07pp (p=0.797)",
      "CAR[-2,2]  -0.21pp (p=0.359)"],
     accent=BLUE)
card(s, Inches(6.83), Inches(3.80), Inches(5.95), Inches(1.72), "B",
     "宽窗口：显著负向",
     ["CAR[-10,15]  -3.18pp (p<0.001)",
      "非 beta 驱动（组间 p=0.930）",
      "最可能：前视偏差 + 年末宏观冲击重叠"],
     accent=ORANGE)
txt(s, Inches(0.6), Inches(5.72), Inches(12.1), Inches(0.38),
    "稳健性：5 种替代设定（等权 / 仅应用密度 / 二值 / P75 分组）全部显著（p<0.001）",
    size=15, color=BLUE, bold=True)
concl_bar(s, "因果权重明确置于短窗口 [0,5]；宽窗口降级为描述性补充，不作选择性省略。", y=Inches(6.50))

# ================= 08 结论与局限 =================
s = prs.slides.add_slide(BLANK)
header(s, "结论与研究局限", "06 · Conclusion", 8)
banner(s, "结论", "LLM 文本度量能纠正词典法高估，并识别出 AI 采纳的定价含义")
card(s, Inches(0.55), Inches(1.95), Inches(5.95), Inches(2.28), "Ⅰ",
     "三条结论",
     ["含 AI 关键词段落仅 19.0% 为真实应用；",
      "词典法高估 31.5%（漏判仅 2.7%，单向）；",
      "DeepSeek 冲击下高采纳组 CAR[0,5] +1.69pp、",
      "CAR[-10,15] +5.20pp（均 p<0.001）。"],
     accent=BLUE)
card(s, Inches(6.83), Inches(1.95), Inches(5.95), Inches(2.28), "Ⅱ",
     "四条局限（诚实列出）",
     ["安慰剂设计存在前视偏差（2023 年报分组 2022 事件）；",
      "宽窗口易受其它信息混杂；",
      "结论依赖提示词 v1 与 GLM-4-Flash 版本；",
      "AI 跨模型复核一致率 90%，仅覆盖 20 段，非人工判读。"],
     accent=ORANGE)
txt(s, Inches(0.6), Inches(4.45), Inches(12.1), Inches(0.4),
    "后续方向", size=19, color=BLUE, bold=True)
txt(s, Inches(0.6), Inches(4.92), Inches(12.1), Inches(1.05),
    "加入行业固定效应与多年份面板检验采纳动态；以 2021 年报度量重做无前视偏差的安慰剂；\n"
    "扩大跨模型（GPT / Claude / Qwen）一致性检验与人工判读；将 LLM 度量对接生产率与用工结果。",
    size=15, color=INK, line_spacing=1.5)
concl_bar(s, "全部数字来自 results/*.csv 实测表；原始 LLM 响应与 Agent 日志完整存档，可任意抽查。", y=Inches(6.42))

# ================= 09 参考文献 =================
s = prs.slides.add_slide(BLANK)
header(s, "参考文献（节选）", "07 · References", 9)
txt(s, Inches(0.6), Inches(1.12), Inches(12.1), Inches(0.38),
    "完整 30 条见论文 PDF 第 17–18 页与 references/citation_verification.md（逐条核验）",
    size=13, color=GREY)
refs = [
    "[1] ZHANG Y, YI Y, CAI Z. Can artificial intelligence enhance corporate green productivity? [J]. Sustainability, 2026, 18(17): 9193.",
    "[3] LI X, DIEP T, LI Y. … Energies, 2026, 19(22): 5413（附录 Table A2 提供 73 词 AI 词典）.",
    "[8] BABINA T, FEDYK A, HE A, et al. Artificial intelligence, firm growth, and product innovation [J]. JFE, 2024, 151: 103745.",
    "[16] MACKINLAY A C. Event studies in economics and finance [J]. Journal of Economic Literature, 1997, 35(1): 13-39.",
    "[17] BROWN S J, WARNER J B. Using daily stock returns [J]. Journal of Financial Economics, 1985, 14(1): 3-31.",
    "[18] TABOGA M. … DeepSeek 发布冲击与金融市场反应 [R]. arXiv:2610.30886, 2026.",
    "[20] BRYNJOLFSSON E, LI D, RAYMOND L. Generative AI at work [J]. QJE, 2025, 140(2): 889-942.",
    "[26] BRYNJOLFSSON E, ROCK D, SYVERSON C. The productivity J-curve [J]. AEJ: Macroeconomics, 2021, 13(1): 333-372.",
    "[30] LI J. Artificial intelligence innovation and financial report quality [J]. IREF, 2026, 105: 104832.",
]
for i, r in enumerate(refs):
    y = Inches(1.65 + i * 0.53)
    txt(s, Inches(0.65), y, Inches(12.0), Inches(0.48), r, size=12.5, color=INK,
        line_spacing=1.15)
    if i < len(refs) - 1:
        rect(s, Inches(0.65), y + Inches(0.47), Inches(12.0), Pt(0.6), fill=LINE)
rect(s, Inches(0.55), Inches(6.60), Inches(12.23), Inches(0.32), fill=BLUE3)
txt(s, Inches(0.72), Inches(6.62), Inches(11.9), Inches(0.28),
    "谢谢，请批评指正   ｜   GitHub: Iris17832/ai-adoption-event-study",
    size=13, color=BLUE, bold=True, align=PP_ALIGN.CENTER)

prs.save(OUT)
print(f"已生成: {OUT}")
print(f"页数: {len(prs.slides.__iter__.__self__._sldIdLst)}")
print(f"大小: {os.path.getsize(OUT)/1024:.0f} KB")

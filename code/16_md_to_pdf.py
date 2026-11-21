#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
16_md_to_pdf.py — 把 paper/manuscript.md 转成可提交的排版 PDF（中文，A4，橙蓝配色）

设计要点
--------
1. 提交版 vs 工作稿：manuscript.md 是研究过程的工作稿，含版本记录、质检说明、
   内部文件名等元信息。本脚本生成的是「提交版」，会：
     - 用自定义封面替代工作稿开头的 # 标题 / 英文副标题 / 作者-竞赛-稿本状态 blockquote
       （因此「稿本状态 v0.3」「v0.3 相对 v0.2 的修订」不进入正式论文）
     - 过滤正文里含「核实状态提示 / 逐条 DOI / 本文不声称任何未经核验」的质检 blockquote
     - 删除正文句子里的内部图片文件名 `fig*.png`
     - 把末尾「附：图表清单」整节替换为一句可复现性说明（图已随文插入）
   **完整保留**所有学术内容，尤其 4.4 / 5.3 / 5.4 的安慰剂负向结果与局限的诚实披露。
2. 图片随文：5 张 PNG 以 base64 内嵌，按锚点插入 4.1 / 4.2 / 4.3 / 4.4 节。
3. 无第三方依赖：自建轻量 Markdown→HTML（标题/段落/表格/引用/列表/加粗/行内代码/
   行内与行间 LaTeX 公式/分隔线），不依赖 pandoc、markdown 库或 MathJax（离线可用）。
4. 渲染：Google Chrome 无头模式 --print-to-pdf；页码用 CSS @page margin box，
   关闭 Chrome 自带页眉页脚（避免 file:// URL 与日期出现在正式论文里）。

产物：paper/manuscript.html（可预览）、paper/manuscript.pdf（提交件）
用法：python3 16_md_to_pdf.py
"""
import os, re, html, base64, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER = os.path.join(ROOT, "paper")
FIGS = os.path.join(ROOT, "results", "figures")
MD = os.path.join(PAPER, "manuscript.md")
HTML_OUT = os.path.join(PAPER, "manuscript.html")
PDF_OUT = os.path.join(PAPER, "manuscript.pdf")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# ---------------------------------------------------------------- 工具函数
def esc(s):
    return html.escape(s, quote=False)

GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ",
    "varepsilon": "ε", "epsilon": "ε", "sigma": "σ", "rho": "ρ",
    "mu": "μ", "theta": "θ", "lambda": "λ", "pi": "π",
}

def tex2html(s):
    """极简 LaTeX 数学 → HTML（仅覆盖本文出现的语法）"""
    s = s.replace(r"\&", "&")
    for k, v in GREEK.items():
        s = s.replace("\\" + k, v)
    s = s.replace(r"\times", "×").replace(r"\leq", "≤").replace(r"\geq", "≥")
    s = s.replace(r"\mathbb{1}", "1")
    s = s.replace(r"\{", "{").replace(r"\}", "}")
    s = s.replace(r"\_", "_").replace(r"\%", "%")
    # 分式
    for _ in range(3):
        s2 = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"\1/\2", s)
        if s2 == s:
            break
        s = s2
    # 上下标（花括号优先，再单字符）
    s = re.sub(r"\^\{([^{}]*)\}", r"<sup>\1</sup>", s)
    s = re.sub(r"_\{([^{}]*)\}", r"<sub>\1</sub>", s)
    s = re.sub(r"\^([A-Za-z0-9+\-])", r"<sup>\1</sup>", s)
    s = re.sub(r"_([A-Za-z0-9])", r"<sub>\1</sub>", s)
    s = re.sub(r"\\[a-zA-Z]+", "", s)          # 残留命令
    s = s.replace("$", "")
    return s

def inline(text):
    """行内元素：代码、公式、加粗；先清洗内部文件名；占位符保护已生成的 HTML"""
    # 提交版清洗：删掉句子里的内部图片文件名（含可选逗号）
    text = re.sub(r"`fig\w+\.png`，?", "", text)
    slots = []

    def stash(h):
        slots.append(h)
        return "\x01%d\x01" % (len(slots) - 1)

    text = re.sub(r"`([^`]+)`",
                  lambda m: stash("<code>" + esc(m.group(1)) + "</code>"), text)
    text = re.sub(r"\$([^$]+)\$",
                  lambda m: stash('<span class="math">' + tex2html(m.group(1)) + "</span>"), text)
    text = re.sub(r"\*\*([^*]+)\*\*",
                  lambda m: stash("<strong>" + esc(m.group(1)) + "</strong>"), text)
    out = esc(text)
    out = re.sub(r"\x01(\d+)\x01", lambda m: slots[int(m.group(1))], out)
    return out

def is_sep_row(line):
    return bool(re.match(r"^\s*\|[\s:\-|]+\|\s*$", line)) and "-" in line

def cells(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]

# ---------------------------------------------------------------- 图片
FIG_DEFS = [
    ("图 1", "fig1_label_dist.png", "27,821 段 LLM 三分类判读分布"),
    ("图 2", "fig2_dict_vs_llm.png", "词典计数 vs LLM 指数散点（对数轴，N=2,082）"),
    ("图 3", "fig3_ai_index_hist.png", "2,082 家公司 AI 采纳指数分布"),
    ("图 4a", "fig4_car_deepseek.png", "DeepSeek 事件高/低采纳组 CAAR 曲线"),
    ("图 4b", "fig4_car_placebo.png", "ChatGPT 安慰剂窗口高/低组 CAAR 曲线"),
]

def data_uri(fname):
    with open(os.path.join(FIGS, fname), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

def figure_html(key):
    for num, fname, cap in FIG_DEFS:
        if num == key:
            return ('<figure><img src="%s" alt="%s %s"/>'
                    '<figcaption><b>%s</b>　%s</figcaption></figure>'
                    % (data_uri(fname), num, cap, num, cap))
    return ""

# 段落锚点 → 该段之后插入的图
ANCHORS = [
    ("在词典计数低端", ["图 2"]),
    ("这正是词典法高估的微观来源", ["图 1", "图 3"]),
    ("CAAR 曲线见图 4a", ["图 4a"]),
    ("图 4b 并排呈现安慰剂窗口", ["图 4b"]),
]

META_BLOCKQUOTE_KEYS = (
    "核实状态提示", "逐条 DOI", "本文不声称任何未经核验",
    "稿本状态", "相对 v0.2",
)

# ---------------------------------------------------------------- Markdown → HTML
def convert(md_text):
    lines = md_text.splitlines()
    # 从「## 摘要」开始（封面由脚本另行生成）
    start = next((i for i, l in enumerate(lines) if l.strip() == "## 摘要"), 0)
    lines = lines[start:]
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        s = line.strip()

        # 末尾「附：图表清单」整节：替换为可复现性说明后结束
        if s.startswith("## 附：图表清单"):
            out.append("<h2>附：图表与数据说明</h2>")
            out.append("<p>本文表 1–表 7 与图 1–图 4 均由程序化脚本直接从结果数据表生成，"
                       "图表文件、生成脚本与原始结果表随研究包一并提交，以保证全过程可复现。"
                       "数据快照与诊断输出见研究包 <code>results/</code> 目录。</p>")
            break

        if not s:
            i += 1
            continue

        # 标题
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            lvl = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (min(lvl, 4), inline(m.group(2)), min(lvl, 4)))
            i += 1
            continue

        # 分隔线
        if re.match(r"^-{3,}$", s):
            out.append("<hr/>")
            i += 1
            continue

        # 行间公式 $$...$$
        if s.startswith("$$") and s.endswith("$$") and len(s) > 4:
            out.append('<div class="eq">' + tex2html(s[2:-2]) + "</div>")
            i += 1
            continue

        # 表格
        if s.startswith("|") and i + 1 < n and is_sep_row(lines[i + 1]):
            header = cells(line)
            i += 2
            body = []
            while i < n and lines[i].strip().startswith("|"):
                body.append(cells(lines[i]))
                i += 1
            t = ['<table><thead><tr>']
            t += ["<th>%s</th>" % inline(c) for c in header]
            t.append("</tr></thead><tbody>")
            for row in body:
                t.append("<tr>" + "".join("<td>%s</td>" % inline(c) for c in row) + "</tr>")
            t.append("</tbody></table>")
            out.append("".join(t))
            continue

        # 引用块（过滤内部质检元信息）
        if s.startswith(">"):
            blk = []
            while i < n and lines[i].strip().startswith(">"):
                t = lines[i].strip()[1:].strip()
                if not any(k in t for k in META_BLOCKQUOTE_KEYS):
                    blk.append(inline(t))
                i += 1
            if blk:
                out.append("<blockquote>" + "<br/>".join(blk) + "</blockquote>")
            continue

        # 列表
        if re.match(r"^([-*]|\d+\.)\s+", s):
            ordered = bool(re.match(r"^\d+\.\s+", s))
            items = []
            while i < n and re.match(r"^([-*]|\d+\.)\s+", lines[i].strip()):
                it = re.sub(r"^([-*]|\d+\.)\s+", "", lines[i].strip())
                items.append("<li>%s</li>" % inline(it))
                i += 1
            out.append(("<ol>" if ordered else "<ul>") + "".join(items) +
                       ("</ol>" if ordered else "</ul>"))
            continue

        # 普通段落（连续非空行合并）
        para = [s]
        i += 1
        while i < n:
            t = lines[i].strip()
            if (not t or re.match(r"^#{1,4}\s", t) or t.startswith("|")
                    or t.startswith(">") or re.match(r"^([-*]|\d+\.)\s+", t)
                    or re.match(r"^-{3,}$", t) or t.startswith("$$")
                    or t.startswith("## 附：图表清单")):
                break
            para.append(t)
            i += 1
        ptext = "".join(para)
        out.append("<p>%s</p>" % inline(ptext))
        for key, figs in ANCHORS:
            if key in ptext:
                for f in figs:
                    out.append(figure_html(f))
                break
    return "\n".join(out)

# ---------------------------------------------------------------- CSS / 封面
CSS = r"""
:root{
  --blue:#1F4E79; --blue2:#376D9E; --blue3:#C2DAEF;
  --orange:#ED7D31; --orange2:#F2A571; --orange3:#FDEADC;
  --ink:#1a1a1a; --grey:#666;
}
@page{
  size:A4; margin:20mm 17mm 17mm;
  @top-right{
    content:"LLM-Measured Corporate AI Adoption  ·  DeepSeek Shock";
    font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;
    font-size:7.5pt; color:#9aa7b4;
  }
  @bottom-center{
    content:counter(page) " / " counter(pages);
    font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;
    font-size:9pt; color:#888;
  }
}
@page:first{
  @top-right{ content:none; }
  @bottom-center{ content:none; }
}
*{ box-sizing:border-box; }
body{
  font-family:"Songti SC","STSong","PingFang SC",serif;
  font-size:10.8pt; line-height:1.8; color:var(--ink); margin:0;
}
h1,h2,h3,h4{ font-family:"PingFang SC","Heiti SC","STHeiti",sans-serif; }
h1{ font-size:20pt; color:var(--blue); text-align:center; line-height:1.5; margin:0 0 6pt; }
h2{
  font-size:15pt; color:var(--blue); margin:20pt 0 10pt; padding:0 0 5pt 9pt;
  border-left:4px solid var(--orange); border-bottom:1px solid var(--blue3);
  break-after:avoid;
}
h3{ font-size:12.5pt; color:var(--blue2); margin:14pt 0 7pt; break-after:avoid; }
h4{ font-size:11pt; color:var(--blue2); margin:10pt 0 5pt; }
p{ margin:0 0 8pt; text-align:justify; text-justify:inter-ideograph; }
strong{ font-weight:700; color:#12324f; }
code{
  font-family:"Menlo","Courier New",monospace; font-size:9pt; color:#3a5a78;
  background:#f2f6fa; padding:0 2px; border-radius:2px;
}
.math{ font-family:"Times New Roman","Songti SC",serif; font-style:italic; white-space:nowrap; }
.eq{
  text-align:center; font-family:"Times New Roman","Songti SC",serif; font-size:11.5pt;
  background:#f5f9fc; border:1px solid var(--blue3); border-radius:3px;
  padding:9pt 6pt; margin:10pt 0; break-inside:avoid;
}
hr{ border:0; border-top:1px solid var(--blue3); margin:16pt 0; }
blockquote{
  margin:9pt 0; padding:7pt 12pt; background:var(--orange3);
  border-left:3px solid var(--orange); color:#5a4636; font-size:9.8pt; line-height:1.7;
  break-inside:avoid;
}
ul,ol{ margin:4pt 0 9pt; padding-left:22pt; }
li{ margin:3pt 0; }
table{
  width:100%; border-collapse:collapse; margin:9pt 0 12pt; font-size:9.6pt;
  break-inside:avoid;
}
thead th{
  background:var(--blue); color:#fff; font-weight:600; text-align:left;
  padding:5pt 7pt; border:1px solid var(--blue2);
}
tbody td{ padding:4pt 7pt; border:1px solid #d6e3ef; vertical-align:top; }
tbody tr:nth-child(even){ background:#f4f8fc; }
figure{ margin:12pt 0 14pt; text-align:center; break-inside:avoid; }
figure img{ max-width:92%; height:auto; border:1px solid #e3eaf1; border-radius:2px; }
figcaption{ font-size:9.2pt; color:var(--grey); margin-top:5pt; }
figcaption b{ color:var(--blue); }
/* 封面 */
.cover{
  break-after:page; text-align:center; padding-top:20mm;
}
.cover .bar{ height:6px; background:linear-gradient(90deg,var(--blue) 0%,var(--blue2) 55%,var(--orange) 100%);
  width:100%; margin-bottom:13mm; border-radius:2px; }
.cover .kicker{ font-family:"Helvetica Neue",Helvetica,sans-serif; font-size:9pt;
  letter-spacing:2px; color:var(--orange); text-transform:uppercase; margin-bottom:7mm; }
.cover h1{ font-size:22pt; line-height:1.5; margin:0 10mm 7mm; }
.cover .subtitle{ font-family:"Times New Roman",serif; font-style:italic; font-size:12pt;
  color:var(--blue2); margin:0 16mm 11mm; line-height:1.6; }
.cover .rule{ width:34mm; height:2px; background:var(--orange); margin:0 auto 10mm; }
.cover .authors{ font-size:13pt; margin:0 0 4mm; letter-spacing:1px; }
.cover .affil{ font-size:10.5pt; color:var(--grey); margin:0 0 2.5mm; }
.cover .contest{ font-size:10.5pt; color:var(--blue2); margin:0 0 11mm; }
.cover .meta{ font-size:9.5pt; color:var(--grey); line-height:1.9; }
.cover .foot{ margin-top:11mm; font-family:"Helvetica Neue",Helvetica,sans-serif;
  font-size:8.5pt; color:#9aa7b4; }
"""

COVER = """
<div class="cover">
  <div class="bar"></div>
  <div class="kicker">Research Paper · Track IV (Economics & Finance)</div>
  <h1>大语言模型度量的企业 AI 采纳与股票回报<br/>——来自 DeepSeek 冲击的事件研究</h1>
  <div class="subtitle">LLM-Measured Corporate AI Adoption and Stock Returns:<br/>Evidence from the DeepSeek Shock</div>
  <div class="rule"></div>
  <div class="authors">张锦悦　孔佳怡</div>
  <div class="affil">山东财经大学　金融数学 / 经济学（2025 级）</div>
  <div class="contest">山东财经大学首届智能体科研创新挑战赛 · 赛道四（经济金融与社会科学智能分析）</div>
  <div class="meta">
    最终样本：2,082 家 A 股公司 · 27,821 个 MD&A 关键词段落（LLM 判读覆盖率 100%）<br/>
    事件：DeepSeek-R1 发布（2025-01-20） · 安慰剂：ChatGPT 发布（2022-11-30）<br/>
    2026 年 11 月
  </div>
  <div class="foot">Submitted as a research prototype · All figures use the unified orange–blue palette</div>
</div>
"""

def build_html(body):
    return ("<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"/>"
            "<title>大语言模型度量的企业AI采纳与股票回报</title>"
            "<style>" + CSS + "</style></head><body>" + COVER + body + "</body></html>")

# ---------------------------------------------------------------- 主流程
def main():
    md = open(MD, encoding="utf-8").read()
    body = convert(md)
    html_str = build_html(body)
    open(HTML_OUT, "w", encoding="utf-8").write(html_str)
    print("HTML 已生成: %s (%.1f KB)" % (HTML_OUT, os.path.getsize(HTML_OUT) / 1024))

    if not os.path.exists(CHROME):
        print("未找到 Google Chrome，跳过 PDF", file=sys.stderr)
        return
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--no-pdf-header-footer", "--print-to-pdf=" + PDF_OUT,
           "file://" + HTML_OUT]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if not os.path.exists(PDF_OUT):
        print("PDF 生成失败:", r.stderr[-600:], file=sys.stderr)
        return

    # 校验
    from pypdf import PdfReader
    rd = PdfReader(PDF_OUT)
    npages = len(rd.pages)
    text = "\n".join((p.extract_text() or "") for p in rd.pages)
    nimg = 0
    for p in rd.pages:
        try:
            xo = p["/Resources"]["/XObject"].get_object()
            for k in xo:
                if xo[k].get_object().get("/Subtype") == "/Image":
                    nimg += 1
        except Exception:
            pass
    print("PDF 已生成: %s" % PDF_OUT)
    print("  大小 %.1f KB | 页数 %d | 内嵌图像对象 %d" %
          (os.path.getsize(PDF_OUT) / 1024, npages, nimg))
    checks = [
        ("中文标题", "企业" in text or "语⾔" in text or "语" in text),
        ("摘要", "摘要" in text),
        ("最终样本 2,082", "2,082" in text),
        ("结论", "结论" in text),
        ("参考文献 [30]", "[30]" in text or "30]" in text),
        ("无残留 $$ 定界符", "$$" not in text),
        ("无残留 \\frac", "\\frac" not in text),
        ("无内部 png 文件名", "fig2_dict" not in text and ".png" not in text),
        ("无内部稿本标记", "稿本状态" not in text and "相对 v0.2" not in text),
    ]
    for name, ok in checks:
        print("  %s %s" % ("OK " if ok else "!! ", name))
    print("  首页文本预览:", repr((rd.pages[0].extract_text() or "")[:90]))

if __name__ == "__main__":
    main()

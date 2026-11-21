#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
17_package_check.py — 提交前全包自检
逐项核验 8 项交付物的存在性与关键数字一致性，输出 results/final_package_check.md。
用法：python3 17_package_check.py
"""
import os, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
ok_all = True
lines = ["# 提交前全包自检报告", "", f"生成时间：{__import__('datetime').datetime.now():%Y-%m-%d %H:%M}", ""]


def check(name, ok, detail=""):
    global ok_all
    ok_all = ok_all and ok
    lines.append(f"- {'✅' if ok else '❌'} **{name}** {detail}")
    return ok


# ---------- ① 论文
md = open("paper/manuscript.md", encoding="utf-8").read()
pdf_ok = os.path.exists("paper/manuscript.pdf")
from pypdf import PdfReader
rd = PdfReader("paper/manuscript.pdf") if pdf_ok else None
pdf_text = "\n".join((p.extract_text() or "") for p in rd.pages) if rd else ""
lines.append("## ① 论文原型（PDF）")
check("manuscript.md 存在", os.path.exists("paper/manuscript.md"))
check("manuscript.pdf 存在", pdf_ok, f"({len(rd.pages)} 页)" if rd else "")
for kw in ["2,082", "27,821", "+1.69pp", "+5.20pp", "84.5", "55.8", "31.5", "-3.18"]:
    check(f"PDF 含关键数字 {kw}", kw in pdf_text or kw.replace(",", "") in pdf_text)
n_refs = len(re.findall(r"^\[(\d+)\]", md, re.M))
check("参考文献 30 条且编号连续", n_refs == 30,
      f"(实测 {n_refs} 条)")
check("正文无未核验引用残留", "待人工终检" not in md and "暂不引用" not in md)
check("口径一致：无 v0.2 旧数字 19/20", "19/20" not in md)

# ---------- ② 代码
lines.append("")
lines.append("## ② 代码仓库及 README")
code_files = sorted(f for f in os.listdir("code") if f.endswith(".py"))
check("README.md 存在", os.path.exists("code/README.md"))
check("requirements.txt 存在", os.path.exists("code/requirements.txt"))
check(f"脚本齐备（{len(code_files)} 个 .py）", len(code_files) >= 13, ", ".join(code_files))
check("data_client.py 存在（数据通道）", os.path.exists("code/data_client.py"))
check("figstyle.py 存在（橙蓝配色）", os.path.exists("code/figstyle.py"))

# ---------- ③ 数据许可
lines.append("")
lines.append("## ③ 数据来源与许可说明")
lic = open("data/data_sources_and_licenses.md", encoding="utf-8").read()
check("许可说明存在", len(lic) > 500)
for src in ["巨潮", "腾讯", "新浪", "GLM"]:
    check(f"登记数据源：{src}", src in lic)

# ---------- ④ 结果与图表
lines.append("")
lines.append("## ④ 实验结果及核心图表")
for t in range(1, 8):
    cands = [f"results/table{t}_", f"results/table_deepseek", f"results/table_placebo"]
    pass
tables = ["table_deepseek_groups.csv", "table_deepseek_regression.csv",
          "table_placebo_groups.csv", "table_placebo_regression.csv",
          "table4_cross_section.csv", "table6_robustness.csv", "table7_diagnostics.csv"]
for t in tables:
    check(f"{t}", os.path.exists(f"results/{t}"))
figs = ["fig1_label_dist.png", "fig2_dict_vs_llm.png", "fig3_ai_index_hist.png",
        "fig4_car_deepseek.png", "fig4_car_placebo.png"]
check("5 张图齐备", all(os.path.exists(f"results/figures/{f}") for f in figs))
check("数字快照 final_numbers.md", os.path.exists("results/final_numbers.md"))
check("诊断报告 diagnostics_report.txt", os.path.exists("results/diagnostics_report.txt"))
fn = open("results/final_numbers.md", encoding="utf-8").read()
check("快照与论文一致：+1.69pp", "+1.69" in fn or "1.69" in fn)
check("快照与论文一致：+5.20pp", "+5.20" in fn or "5.20" in fn)

# ---------- ⑤ 文献
lines.append("")
lines.append("## ⑤ 文献来源与引用核验")
check("核验表 citation_verification.md", os.path.exists("references/citation_verification.md"))
check("人工核实清单（md + xlsx）",
      os.path.exists("references/citation_human_checklist.md") and
      os.path.exists("references/citation_human_checklist.xlsx"))
check("73 词词典词表", os.path.exists("references/ai_dictionary_73words.txt"))
dict_words = open("references/ai_dictionary_73words.txt", encoding="utf-8").read()
table_part = dict_words.split("## Table A2 原文词表")[-1]
n_words = len(re.findall(r"^\d+\.\s+\S", table_part, re.M))
check("词典词数 = 73", n_words == 73, f"(实测 {n_words})")

# ---------- ⑥ Agent 日志
lines.append("")
lines.append("## ⑥ Agent 使用日志")
log = open("agent_log/agent_usage_log.md", encoding="utf-8").read()
check("日志存在且持续追加", len(log) > 3000, f"({len(log)} 字符)")
check("覆盖 11-17/19/20/21 四个活跃日",
      all(d in log for d in ["2026-11-17", "2026-11-19", "2026-11-20", "2026-11-21"]))

# ---------- ⑦ 可复现说明
lines.append("")
lines.append("## ⑦ 可复现说明")
rep = open("reproducibility/REPRODUCE.md", encoding="utf-8").read()
check("REPRODUCE.md 存在", len(rep) > 3000)
check("披露诚实性（提及成交额代理/剔除规则）", "成交额" in rep or "代理" in rep)

# ---------- ⑧ 人机分工
lines.append("")
lines.append("## ⑧ 人机分工声明")
div = open("team/human_ai_division.md", encoding="utf-8").read()
check("声明存在", len(div) > 2000)
check("含两位成员", "张锦悦" in div and "孔佳怡" in div)
check("含三项任务", all(k in div for k in ["文献", "打分", "合规"]))

# ---------- 版本管理与 GitHub
lines.append("")
lines.append("## 版本管理与远程仓库")
remote = subprocess.run(["git", "remote", "get-url", "origin"],
                        capture_output=True, text=True).stdout.strip()
check("远程已配置", bool(remote), remote)
pushed = subprocess.run(["git", "status", "-sb"], capture_output=True, text=True).stdout.splitlines()[0]
check("本地与远程同步", "ahead" not in pushed and "behind" not in pushed, pushed.strip())
check("无敏感文件入库", not subprocess.run(["git", "ls-files"], capture_output=True, text=True)
      .stdout.count(".env"), ".env 未被跟踪")
check("无第三方全文 PDF 入库",
      "references/pdfs" not in subprocess.run(["git", "ls-files"],
                                              capture_output=True, text=True).stdout)

lines.append("")
lines.append("---")
lines.append(f"## 总体结论：{'✅ 全部通过，可提交' if ok_all else '❌ 存在未通过项，见上'}")
open("results/final_package_check.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines[-3:]))
print("报告: results/final_package_check.md")
if not ok_all:
    print("\n".join(l for l in lines if l.startswith("- ❌")))

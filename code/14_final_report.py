# -*- coding: utf-8 -*-
"""
14_final_report.py — 从 results/*.csv 自动抽取最终样本全部关键数字，
生成可直接粘贴进论文 manuscript.md 的数字快照（杜绝手工抄数错误）。

输入：results/ 下的表 + data/processed/ 下的样本表
输出：results/final_numbers.md
"""
import os
import pandas as pd

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES = os.path.join(BASE, "results")
PROC = os.path.join(BASE, "data", "processed")


def rd(name, **kw):
    p = os.path.join(RES, name)
    return pd.read_csv(p, **kw) if os.path.exists(p) else None


def fmt_p(p):
    try:
        p = float(p)
    except Exception:
        return str(p)
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def pp(x):
    return f"{x*100:+.2f}pp"


lines = ["# 最终样本数字快照（由 14_final_report.py 从 results/*.csv 自动生成）", ""]
lines.append(f"> 生成时间见文件时间戳；本文件所有数字均由程序读取，无手工录入。")
lines.append("")

# 样本规模
firm = pd.read_csv(os.path.join(PROC, "ai_adoption_firm.csv"), dtype={"code": str})
llm = pd.read_csv(os.path.join(PROC, "ai_adoption_llm.csv"), dtype={"code": str})
para = pd.read_csv(os.path.join(PROC, "mda_paragraphs.csv"), dtype={"code": str})
lines.append("## 样本规模")
lines.append(f"- 段落表：{len(para)} 段 / {para.code.nunique()} 家公司")
lines.append(f"- 已完成 LLM 判读：{len(llm)} 段 / {llm.code.nunique()} 家公司")
lines.append(f"- 公司级指数表：{len(firm)} 家")
need = para.groupby("code").size(); done = llm.groupby("code").size()
comp = sum(1 for c in firm.code if done.get(c, 0) / need.get(c, 1) >= 0.999)
lines.append(f"- 段落 100% 完整判读公司：{comp} 家（{comp/len(firm)*100:.1f}%）")
vc = llm.label.value_counts()
lines.append(f"- 标签分布：application {vc.get('application',0)} ({vc.get('application',0)/len(llm)*100:.1f}%) / "
             f"strategy {vc.get('strategy',0)} ({vc.get('strategy',0)/len(llm)*100:.1f}%) / "
             f"none {vc.get('none',0)} ({vc.get('none',0)/len(llm)*100:.1f}%)")
lines.append(f"- AI_Index>0：{int((firm.ai_index>0).sum())} 家 ({(firm.ai_index>0).mean()*100:.1f}%)")
lines.append("")

# 度量对比（同一合并样本）
d = pd.read_csv(os.path.join(PROC, "ai_adoption_dict.csv"), dtype={"code": str})
m = firm[["code", "ai_index"]].merge(d[["code", "ai_hit"]], on="code", how="inner")
dh, lh = m.ai_hit > 0, m.ai_index > 0
lines.append("## 度量对比（同一合并样本）")
lines.append(f"- N = {len(m)}")
lines.append(f"- 词典命中>0：{int(dh.sum())} ({dh.mean()*100:.1f}%)；LLM>0：{int(lh.sum())} ({lh.mean()*100:.1f}%)；差 {(dh.mean()-lh.mean())*100:.1f}pp")
lines.append(f"- 词典>0 且 LLM=0（高估）：{int((dh & ~lh).sum())} ({(dh & ~lh).mean()*100:.1f}%)")
corr = open(os.path.join(RES, "dict_vs_llm_correlation.txt")).read()
for l in corr.splitlines():
    if "Spearman" in l or "Pearson" in l:
        lines.append(f"- {l.strip()}")
lines.append("")

# 主结果
tg, tr = rd("table_deepseek_groups.csv"), rd("table_deepseek_regression.csv")
pg, pr = rd("table_placebo_groups.csv"), rd("table_placebo_regression.csv")
t4, t6, t7 = rd("table4_cross_section.csv"), rd("table6_robustness.csv"), rd("table7_diagnostics.csv")

lines.append("## DeepSeek 主结果（表2/表3）")
if tg is not None:
    lines.append("| 窗口 | 高组 | 低组 | 差异 | t | p |")
    lines.append("|---|---|---|---|---|---|")
    for _, r in tg.iterrows():
        lines.append(f"| {r.CAR_window} | {r.high_mean*100:+.2f}% | {r.low_mean*100:+.2f}% | "
                     f"{pp(r['diff'])} | {r.t_stat:.2f} | {fmt_p(r.p_value)} |")
    lines.append(f"- 分组 N：高 {int(tg.high_n.iloc[0])} / 低 {int(tg.low_n.iloc[0])}")
lines.append("")
if tr is not None:
    lines.append("| 窗口 | AI_Index 系数 | t | p | R² | N |")
    lines.append("|---|---|---|---|---|---|")
    for _, r in tr.iterrows():
        lines.append(f"| {r.CAR_window} | {r.coef_ai_index:.4f} | {r.t:.2f} | {fmt_p(r.p)} | {r.r2:.3f} | {int(r.n)} |")
lines.append("")

lines.append("## 横截面回归（表4，控制规模/波动/动量）")
if t4 is not None:
    for w in ["CAR[0,5]", "CAR[-10,15]"]:
        s = t4[(t4.CAR_window == w) & (t4.variable == "ai_index")]
        if len(s):
            r = s.iloc[0]
            lines.append(f"- {w}: ai_index = {r.coef:.4f} (t={r.t:.2f}, p={fmt_p(r.p)}), R²={r.r2:.3f}, N={int(r.n)}")
lines.append("")

lines.append("## 安慰剂（表5）— 含宽窗口负向差异，必须如实披露")
if pg is not None:
    lines.append("| 窗口 | 高−低差异 | t | p |")
    lines.append("|---|---|---|---|")
    for _, r in pg.iterrows():
        lines.append(f"| {r.CAR_window} | {pp(r['diff'])} | {r.t_stat:.2f} | {fmt_p(r.p_value)} |")
lines.append("")

lines.append("## 稳健性（表6，替代度量）")
if t6 is not None:
    for _, r in t6.iterrows():
        lines.append(f"- {r.robustness} / {r.window}: {pp(r['diff'])} (p={fmt_p(r.p)}, n={int(r.n_hi)}/{int(r.n_lo)})")
lines.append("")

lines.append("## 诊断（表7）")
if t7 is not None:
    lines.append("| 检验 | 事件 | 窗口 | 样本 | 差异/系数 | p |")
    lines.append("|---|---|---|---|---|---|")
    for _, r in t7.iterrows():
        val = r.get("diff", r.get("coef_ai", float("nan")))
        try:
            vs = pp(val) if r.test.startswith("D1") or r.test.startswith("D3") else f"{float(val):+.4f}"
        except Exception:
            vs = "-"
        lines.append(f"| {r.test} | {r.event} | {r.get('window','')} | {r.get('sample','')} | {vs} | {fmt_p(r.get('p', r.get('p_ai', float('nan'))))} |")
lines.append("")

out = "\n".join(lines)
open(os.path.join(RES, "final_numbers.md"), "w").write(out + "\n")
print(out)
print("\n输出: results/final_numbers.md")

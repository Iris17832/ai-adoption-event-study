# -*- coding: utf-8 -*-
"""
10_robustness.py — 稳健性检验：替代度量与替代分组
=================================================
内容（对应论文 5.1 节）：
  R1 等权指数        ai_index_eq  = (density + breadth + invest) / 3
  R2 仅应用密度      ai_density   = n_app / n
  R3 二值采纳        ai_binary    = 1{n_app > 0}
  R4 75分位分组      主 ai_index 按 P75 阈值分组（替代中位数分组）
每个替代度量：DeepSeek 事件主窗口 CAR[0,5] 与 CAR[-10,15] 的
  组间差异 t 检验 + 指数回归，与主结果（中位数分组的 ai_index）并列输出。

输入：data/processed/ai_adoption_llm.csv（段落级）、results/car_panel_deepseek.csv（06 产物）
输出：results/table6_robustness.csv
"""
import os, sys
import numpy as np
import pandas as pd
import statsmodels.api as sm

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PARA_CSV = os.path.join(BASE, "data", "processed", "ai_adoption_llm.csv")
PANEL_CSV = os.path.join(BASE, "results", "car_panel_deepseek.csv")
OUT = os.path.join(BASE, "results", "table6_robustness.csv")

DOMAINS = ["研发", "生产制造", "营销销售", "客户服务", "风控合规", "供应链", "经营管理", "对外AI产品"]
MAIN_WINDOWS = ["CAR[0,5]", "CAR[-10,15]"]


def build_alt_indexes():
    df = pd.read_csv(PARA_CSV, dtype={"code": str})
    df = df[df["label"] != "FAILED"]
    rows = []
    for code, g in df.groupby("code"):
        n = len(g)
        n_app = int((g["label"] == "application").sum())
        density = n_app / n
        domains = set()
        for d in g["domain"].fillna(""):
            for dd in str(d).split("|"):
                if dd.strip() in DOMAINS:
                    domains.add(dd.strip())
        breadth = len(domains) / len(DOMAINS)
        invest = 1 if (g["investment_mention"] == True).any() else 0
        rows.append({"code": code, "n_paras": n, "n_application": n_app,
                     "ai_density": density, "domain_breadth": breadth, "investment": invest,
                     "ai_index_eq": (density + breadth + invest) / 3.0,
                     "ai_binary": 1.0 if n_app > 0 else 0.0})
    return pd.DataFrame(rows)


def ttest(hi, lo):
    from scipy import stats as sps
    return sps.ttest_ind(hi, lo, equal_var=False)


def run():
    alt = build_alt_indexes()
    panel = pd.read_csv(PANEL_CSV, dtype={"code": str})
    df = panel.merge(alt, on="code", how="inner", suffixes=("", "_alt"))
    print(f"稳健性样本: {len(df)} 家（段落级聚合 {len(alt)} 家 ∩ CAR 面板 {len(panel)} 家）")

    out = []
    # 主度量（中位数分组 + P75 分组），供对照
    for measure, label in [("ai_index", "主指数(中位数)"), ("ai_index", "主指数(P75)")]:
        q = 0.5 if "中位数" in label else 0.75
        for w in MAIN_WINDOWS:
            s = df[[measure, w]].dropna()
            thr = s[measure].quantile(q)
            hi, lo = s[s[measure] >= thr][w], s[s[measure] < thr][w]
            t, p = ttest(hi, lo)
            out.append({"robustness": label, "measure": measure, "window": w,
                        "high_mean": hi.mean(), "low_mean": lo.mean(),
                        "diff": hi.mean() - lo.mean(), "t": t, "p": p, "n_hi": len(hi), "n_lo": len(lo)})
    # 替代度量（中位数分组；binary 用 1/0）
    for measure, label in [("ai_index_eq", "R1 等权指数"), ("ai_density", "R2 仅应用密度"),
                           ("ai_binary", "R3 二值采纳")]:
        for w in MAIN_WINDOWS:
            s = df[[measure, w]].dropna()
            if measure == "ai_binary":
                hi, lo = s[s[measure] == 1][w], s[s[measure] == 0][w]
            else:
                thr = s[measure].median()
                hi, lo = s[s[measure] >= thr][w], s[s[measure] < thr][w]
            t, p = ttest(hi, lo)
            out.append({"robustness": label, "measure": measure, "window": w,
                        "high_mean": hi.mean(), "low_mean": lo.mean(),
                        "diff": hi.mean() - lo.mean(), "t": t, "p": p, "n_hi": len(hi), "n_lo": len(lo)})
    res = pd.DataFrame(out)
    res.to_csv(OUT, index=False)
    print(res.round(4).to_string(index=False))
    print(f"\n输出: {OUT}")


if __name__ == "__main__":
    run()

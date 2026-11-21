# -*- coding: utf-8 -*-
"""
13_diagnostics.py — 扩容样本的学术质量诊断（诚实披露用）

背景：最终样本 2,082 家（段落表 27,821 段已 100% 完成 LLM 判读）。
本脚本沿用扩容阶段建立的诊断框架，服务于两类核验：
  (P1) 打分完整性 —— 最终样本已全覆盖，D1 用于确认「全样本 ≡ 完整判读
       子样本」，即历史扩容阶段的"部分打分"测量偏差已彻底消除；
  (P2) 安慰剂窗口 CAR[-10,15] 在扩容后持续显著负向（-3.18pp, p<0.001），
       需排除 beta / 公司特征等替代解释，并明确「干净」的窗口边界。

本脚本产出：
  results/car_panel_placebo.csv          安慰剂完整面板（06 只存 deepseek）
  results/table7_diagnostics.csv         诊断结果汇总
  results/diagnostics_report.txt         可直接写进论文的诚实披露文本

诊断项：
  D1 完整打分子样本重跑主结果 —— 最终样本下验证全样本与完整子样本一致
  D2 组间 beta 差异 + 加 beta 控制的 CAR 回归 —— 检验 P2 是否由风险暴露驱动
  D3 安慰剂短窗口 vs 长窗口对照 —— 明确"干净"的窗口边界
  D4 再控制规模/波动/动量 —— 检验负向差异是否由公司特征驱动
"""
import os, sys, importlib.util
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CODE = os.path.join(BASE, "code")
PROC = os.path.join(BASE, "data", "processed")
RES = os.path.join(BASE, "results")
os.makedirs(RES, exist_ok=True)

# 复用 06 的 CAR 计算口径（保证与正文完全一致）
spec = importlib.util.spec_from_file_location("car06", os.path.join(CODE, "06_car_analysis.py"))
car06 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(car06)


def build_panel(window_name, firm_df):
    """重算某事件窗口的完整 CAR 面板（含 beta），与 06 完全同式"""
    idx_df = pd.read_csv(os.path.join(BASE, "data", "prices", "index_000300.csv"))
    idx_df = idx_df[idx_df["window"] == window_name]
    event_date = car06.EVENTS[window_name]
    rows = []
    for _, fr in firm_df.iterrows():
        pth = os.path.join(BASE, "data", "prices", window_name, f"{fr['code']}.csv")
        if not os.path.exists(pth):
            continue
        try:
            stock_df = pd.read_csv(pth, dtype={"date": str})
            merged = car06.align_trading_days(stock_df, idx_df)
            r = car06.compute_car(merged, event_date)
        except Exception:
            continue
        if r is None:
            continue
        rows.append({"code": fr["code"], "name": fr["name"], "ai_index": fr["ai_index"], **r})
    return pd.DataFrame(rows)


def group_ttest(df, col, q=0.5):
    """按 AI 采纳分组做 Welch t 检验。
    注意：当子样本中 ai_index=0 占比过高导致中位数=0 时，>=median 会把全部样本
    分进高组、低组为空（scipy 返回 NaN）。此时自动退化为 ai_index>0 二值分组，
    并在返回的 split 字段标注，避免 silently 产出 NaN。"""
    med = df["ai_index"].median()
    hi, lo = df[df["ai_index"] >= med], df[df["ai_index"] < med]
    split = f"median(={med:.3f})"
    if len(hi) < 2 or len(lo) < 2:
        hi, lo = df[df["ai_index"] > 0], df[df["ai_index"] == 0]
        split = "binary(ai_index>0)"
    t, p = stats.ttest_ind(hi[col].dropna(), lo[col].dropna(), equal_var=False)
    return {"high_n": len(hi), "low_n": len(lo), "split": split,
            "high_mean": hi[col].mean(), "low_mean": lo[col].mean(),
            "diff": hi[col].mean() - lo[col].mean(), "t": t, "p": p}


def ols(df, y, controls):
    s = df[[y, "ai_index"] + controls].dropna()
    X = sm.add_constant(s[["ai_index"] + controls])
    m = sm.OLS(s[y], X).fit()
    return {"coef_ai": m.params["ai_index"], "t_ai": m.tvalues["ai_index"],
            "p_ai": m.pvalues["ai_index"], "r2": m.rsquared, "n": int(m.nobs)}


def main():
    firm = pd.read_csv(os.path.join(PROC, "ai_adoption_firm.csv"), dtype={"code": str})
    para = pd.read_csv(os.path.join(PROC, "mda_paragraphs.csv"), dtype={"code": str})
    llm = pd.read_csv(os.path.join(PROC, "ai_adoption_llm.csv"), dtype={"code": str})

    # --- 段落完整性标记 ---
    need = para.groupby("code").size().rename("need")
    done = llm.groupby("code").size().rename("done")
    chk = pd.concat([need, done], axis=1).fillna(0)
    chk["ratio"] = chk["done"] / chk["need"]
    complete_codes = set(chk[chk["ratio"] >= 0.999].index) & set(firm["code"])
    print(f"段落完整打分公司: {len(complete_codes)} / {len(firm)}")

    # --- 构建两个事件的完整面板 ---
    d_panel = build_panel("deepseek", firm)
    p_panel = build_panel("placebo", firm)
    p_panel.to_csv(os.path.join(RES, "car_panel_placebo.csv"), index=False)
    print(f"面板: deepseek {len(d_panel)} 家 | placebo {len(p_panel)} 家")

    rows, report = [], []
    report.append("=== 扩容样本诊断报告（2026-11-21）===\n")

    # ---------- D1 段落完整子样本 ----------
    report.append("[D1] 段落完整性对主结论的影响")
    for wname, panel in [("deepseek", d_panel), ("placebo", p_panel)]:
        sub = panel[panel["code"].isin(complete_codes)]
        for col in ["CAR[0,5]", "CAR[-10,15]"]:
            full = group_ttest(panel, col)
            only = group_ttest(sub, col)
            rows.append({"test": "D1_完整子样本", "event": wname, "window": col,
                         "sample": "full", **{k: full[k] for k in ["high_n", "low_n", "diff", "t", "p"]}})
            rows.append({"test": "D1_完整子样本", "event": wname, "window": col,
                         "sample": "complete_only", **{k: only[k] for k in ["high_n", "low_n", "diff", "t", "p"]}})
            report.append(f"  {wname} {col}: 全样本 diff={full['diff']*100:+.2f}pp (p={full['p']:.4f}, n={full['high_n']+full['low_n']}) "
                          f"| 完整子样本 diff={only['diff']*100:+.2f}pp (p={only['p']:.4f}, n={only['high_n']+only['low_n']})")
    report.append("")

    # ---------- D2 beta 驱动检验 ----------
    report.append("[D2] 安慰剂长窗口负向差异是否由风险暴露(beta)驱动")
    med_p = p_panel["ai_index"].median()
    hi_p = p_panel[p_panel["ai_index"] >= med_p]["beta"].dropna()
    lo_p = p_panel[p_panel["ai_index"] < med_p]["beta"].dropna()
    tb, pb = stats.ttest_ind(hi_p, lo_p, equal_var=False)
    report.append(f"  安慰剂面板 高组 beta={hi_p.mean():.4f} vs 低组 beta={lo_p.mean():.4f} (差 {hi_p.mean()-lo_p.mean():+.4f}, t={tb:.2f}, p={pb:.4f})")
    rows.append({"test": "D2_beta组间差", "event": "placebo", "window": "beta",
                 "sample": "full", "high_mean": hi_p.mean(), "low_mean": lo_p.mean(),
                 "diff": hi_p.mean()-lo_p.mean(), "t": tb, "p": pb})
    for wname, panel in [("deepseek", d_panel), ("placebo", p_panel)]:
        for col in ["CAR[0,5]", "CAR[-10,15]"]:
            bare = ols(panel, col, [])
            ctrl = ols(panel, col, ["beta"])
            rows.append({"test": "D2_beta控制回归", "event": wname, "window": col,
                         "sample": "不加控制", "coef_ai": bare["coef_ai"], "p_ai": bare["p_ai"], "n": bare["n"]})
            rows.append({"test": "D2_beta控制回归", "event": wname, "window": col,
                         "sample": "控制beta", "coef_ai": ctrl["coef_ai"], "p_ai": ctrl["p_ai"], "n": ctrl["n"]})
            report.append(f"  {wname} {col}: 不控制 beta 系数={bare['coef_ai']:+.4f} (p={bare['p_ai']:.4f}) "
                          f"| 控制 beta 后={ctrl['coef_ai']:+.4f} (p={ctrl['p_ai']:.4f})")
    report.append("")

    # ---------- D4 控制公司特征后的安慰剂负向差异 ----------
    report.append("[D4] 控制公司特征(规模/波动/动量/beta)后，安慰剂长窗口负向差异是否仍存在")
    spec7 = importlib.util.spec_from_file_location("cs07", os.path.join(CODE, "07_cross_section.py"))
    cs07 = importlib.util.module_from_spec(spec7)
    spec7.loader.exec_module(cs07)
    feats = []
    for code in p_panel["code"]:
        f = cs07.build_features(code) or {}
        feats.append({"code": code, **f})
    p_ctrl = p_panel.merge(pd.DataFrame(feats), on="code", how="left")
    for ctrl_set, cols in [("仅beta", ["beta"]),
                           ("beta+规模/波动/动量", ["beta", "size_proxy", "vol_pre", "mom_pre"])]:
        r = ols(p_ctrl, "CAR[-10,15]", cols)
        rows.append({"test": "D4_安慰剂控制特征", "event": "placebo", "window": "CAR[-10,15]",
                     "sample": ctrl_set, "coef_ai": r["coef_ai"], "p_ai": r["p_ai"], "n": r["n"]})
        report.append(f"  安慰剂 CAR[-10,15] 控制 {ctrl_set}: ai_index 系数={r['coef_ai']:+.4f} "
                      f"(p={r['p_ai']:.4f}, n={r['n']})")
    report.append("")

    # ---------- D3 安慰剂窗口边界 ----------
    report.append("[D3] 安慰剂各窗口（明确'干净'的窗口边界）")
    for col in ["CAR[-1,1]", "CAR[0,5]", "CAR[-2,2]", "CAR[-10,15]"]:
        g = group_ttest(p_panel, col)
        rows.append({"test": "D3_安慰剂窗口", "event": "placebo", "window": col,
                     "sample": "full", "diff": g["diff"], "t": g["t"], "p": g["p"]})
        report.append(f"  {col}: diff={g['diff']*100:+.2f}pp, t={g['t']:.2f}, p={g['p']:.4f}")
    report.append("")

    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(RES, "table7_diagnostics.csv"), index=False)
    txt = "\n".join(report)
    open(os.path.join(RES, "diagnostics_report.txt"), "w").write(txt + "\n")
    print("\n" + txt)
    print("输出: results/table7_diagnostics.csv + diagnostics_report.txt + car_panel_placebo.csv")


if __name__ == "__main__":
    main()

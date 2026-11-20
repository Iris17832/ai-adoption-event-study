# -*- coding: utf-8 -*-
"""
06_car_analysis.py — 事件研究主分析：DeepSeek-R1发布冲击 × 企业AI采纳强度
设计:
  事件日 t=0: 2025-01-20（DeepSeek-R1 发布）
  市场模型: alpha_i, beta_i 用估计窗 [-250, -21] 交易日的 OLS
  事件窗: [-10, +15]，报告 CAR[-1,+1]、CAR[0,+5]、CAR[-2,+2]、CAR[-10,+15]
  分组: 按 ai_index 中位数分高/低采纳组（稳健性：三分位）
  检验: 组间 CAR 差异 t 检验 + CAR 对 ai_index 单变量回归（Newey-West可后续加）
  安慰剂: ChatGPT 发布 2022-11-30，同一设计
用法:
    python 06_car_analysis.py
产物:
    results/table1_car_groups.csv    分组CAR与差异检验（主表）
    results/table2_car_regression.csv  CAR对ai_index回归
    results/table3_placebo.csv       ChatGPT安慰剂
"""
import sys, os
import numpy as np
import pandas as pd
import statsmodels.api as sm

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P_DIR = os.path.join(BASE, "data", "prices")
R_DIR = os.path.join(BASE, "results")
os.makedirs(R_DIR, exist_ok=True)

EVENTS = {"deepseek": "2025-01-20", "placebo": "2022-11-30"}
CAR_WINDOWS = [(-1, 1), (0, 5), (-2, 2), (-10, 15)]
EST_RANGE = (-250, -21)

def load_firm_index():
    df = pd.read_csv(os.path.join(BASE, "data", "processed", "ai_adoption_firm.csv"), dtype={"code": str})
    return df

def align_trading_days(stock_df, index_df):
    """按日期对齐个股与市场收益（内连接，保证同一交易日历）"""
    s = stock_df[["date", "close"]].rename(columns={"close": "cs"}).copy()
    m = index_df[["date", "close"]].rename(columns={"close": "cm"}).copy()
    merged = s.merge(m, on="date", how="inner").sort_values("date").reset_index(drop=True)
    merged["rs"] = merged["cs"].pct_change()
    merged["rm"] = merged["cm"].pct_change()
    return merged

def compute_car(merged, event_date):
    dates = merged["date"].tolist()
    if event_date not in dates:
        # 找事件日后的第一个交易日
        after = [d for d in dates if d >= event_date]
        if not after:
            return None
        t0 = dates.index(after[0])
    else:
        t0 = dates.index(event_date)
    # 估计窗
    e0, e1 = t0 + EST_RANGE[0], t0 + EST_RANGE[1]
    est = merged.iloc[max(e0, 1):e1 + 1].dropna(subset=["rs", "rm"])
    if len(est) < 60:
        return None
    X = sm.add_constant(est["rm"])
    model = sm.OLS(est["rs"], X).fit()
    alpha, beta = model.params["const"], model.params["rm"]
    # 事件窗异常收益
    lo = max(t0 - 10, 0)
    hi = min(t0 + 15, len(merged) - 1)
    ev = merged.iloc[lo:hi + 1].copy()
    ev["ar"] = ev["rs"] - (alpha + beta * ev["rm"])
    ev["t_rel"] = np.arange(lo, hi + 1) - t0
    out = {"alpha": alpha, "beta": beta, "n_est": len(est)}
    for (a, b) in CAR_WINDOWS:
        w = ev[(ev["t_rel"] >= a) & (ev["t_rel"] <= b)]
        out[f"CAR[{a},{b}]"] = w["ar"].sum()
    return out

def analyze_window(window_name, firm_df):
    event_date = EVENTS[window_name]
    idx_df = pd.read_csv(os.path.join(P_DIR, "index_000300.csv"))
    idx_df = idx_df[idx_df["window"] == window_name]
    rows = []
    for _, fr in firm_df.iterrows():
        pth = os.path.join(P_DIR, window_name, f"{fr['code']}.csv")
        if not os.path.exists(pth):
            continue
        try:
            stock_df = pd.read_csv(pth, dtype={"date": str})
            merged = align_trading_days(stock_df, idx_df)
            res = compute_car(merged, event_date)
        except Exception:
            continue
        if res is None:
            continue
        rows.append({"code": fr["code"], "name": fr["name"], "ai_index": fr["ai_index"],
                     "n_application": fr["n_application"], **res})
    return pd.DataFrame(rows)

def ttest_diff(x, y):
    """Welch t 检验"""
    from scipy import stats
    t, p = stats.ttest_ind(x.dropna(), y.dropna(), equal_var=False)
    return t, p

def main():
    firm_df = load_firm_index()
    print(f"已打分公司: {len(firm_df)}")

    out_tables = {}
    for wname in ["deepseek", "placebo"]:
        df = analyze_window(wname, firm_df)
        if df.empty:
            print(f"[{wname}] 无可用数据")
            continue
        med = df["ai_index"].median()
        hi, lo = df[df["ai_index"] >= med], df[df["ai_index"] < med]
        rows = []
        for c in [f"CAR[{a},{b}]" for (a, b) in CAR_WINDOWS]:
            t, p = ttest_diff(hi[c], lo[c])
            rows.append({"CAR_window": c, "high_mean": hi[c].mean(), "high_n": len(hi),
                         "low_mean": lo[c].mean(), "low_n": len(lo),
                         "diff": hi[c].mean() - lo[c].mean(), "t_stat": t, "p_value": p})
        tt = pd.DataFrame(rows)
        tt.to_csv(os.path.join(R_DIR, f"table_{wname}_groups.csv"), index=False)
        # 单变量回归（每窗口）
        regs = []
        for c in [f"CAR[{a},{b}]" for (a, b) in CAR_WINDOWS]:
            m = sm.OLS(df[c].dropna(), sm.add_constant(df.loc[df[c].dropna().index, "ai_index"])).fit()
            regs.append({"CAR_window": c, "coef_ai_index": m.params["ai_index"],
                         "se": m.bse["ai_index"], "t": m.tvalues["ai_index"],
                         "p": m.pvalues["ai_index"], "r2": m.rsquared, "n": int(m.nobs)})
        rg = pd.DataFrame(regs)
        rg.to_csv(os.path.join(R_DIR, f"table_{wname}_regression.csv"), index=False)
        out_tables[wname] = (df, tt, rg)
        print(f"\n===== {wname}（事件日 {EVENTS[wname]}）分组检验 =====")
        print(tt.round(4).to_string(index=False))
        print(f"\n----- {wname} CAR ~ ai_index 回归 -----")
        print(rg.round(4).to_string(index=False))

    # 主事件完整面板存档（供横截面回归 07 使用）
    if "deepseek" in out_tables:
        out_tables["deepseek"][0].to_csv(os.path.join(R_DIR, "car_panel_deepseek.csv"), index=False)
        print("\n面板已存档: results/car_panel_deepseek.csv")

if __name__ == "__main__":
    main()
